import string
import random
import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy import func
from django.core.urlresolvers import reverse

from jambalaya.forms import CreateItemForm
from jambalaya.models import Category, Item, DirectSaleListing, AuctionListing, ItemRating, SellerRating


@login_required
def create(request, category_id):
    category_tree, _ = Category.eager_load_tree(request.db_session)
    if request.method == "GET":
        if "create_item_form" in request.session:
            del request.session["create_item_form"]
        form = CreateItemForm(categories=category_tree, selected_category=category_id)
    else:
        # create a form instance and populate it with data from the request:
        form = CreateItemForm(request.POST, categories=category_tree)
        # check whether it's valid:
        if form.is_valid():
            image_data = None
            if "image" in request.FILES:
                image_data = "data:image/png;base64,%s" % request.FILES["image"].read().encode("base64")
            token = "jam" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
            request.session["create_item_form"] = dict(form.cleaned_data, **{
                "image": image_data
            })
            request.session["new_item_token"] = token
            return HttpResponseRedirect(reverse("list_item", kwargs={"item_id": token}))

    return render(request, "item/create.html", {"form": form})


def view(request, item_id):
    session = request.db_session
    data = session.query(Item, func.avg(ItemRating.Rating), func.count(ItemRating)).join(ItemRating).filter(Item.ID == item_id).one()
    item = data[0]

    direct_sales = []
    for listing in [l for l in item.listings if type(l) is DirectSaleListing]:
        seller_rating = session.query(func.avg(SellerRating.Rating)).filter(SellerRating.SellerID == listing.SellerID).scalar() or 0
        direct_sales.append({
            "listing": listing,
            "seller_rating": seller_rating
        })

    auctions = []
    for auction in [l for l in item.listings if type(l) is AuctionListing]:
        bids = len(auction.bids)
        high_bid = max([bid.Amount for bid in auction.bids]) if bids else None
        auctions.append({
            "listing": auction,
            "high_bid": high_bid,
            "bids": bids,
            "expires": auction.Created + datetime.timedelta(weeks=2)
        })

    commentor_list = ["images/commentors/%d.jpg" % i for i in range(1, 11)]
    commentors = random.sample(commentor_list, len(item.ratings))

    ratings = []
    for rating in item.ratings:
        ratings.append({
            "rating": rating,
            "commentor": commentors.pop()
        })

    return render(request, "item/view.html", {
        "item": item,
        "sell_link": reverse("list_item", kwargs={"item_id": item_id}),
        "active_category": item.CategoryID,
        "rating": data[1],
        "rating_count": data[2],
        "auctions": auctions,
        "direct_sales": direct_sales,
        "ratings": ratings
    })


def browse(request, category_id, category_name):
    # TODO: Pagination
    # TODO: Different formats for viewing the items
    # TODO: Optimize queries
    session = request.db_session
    category = session.query(Category.Name).filter(Category.ID == category_id).scalar()
    items = session.query(Item, func.avg(ItemRating.Rating)).outerjoin(ItemRating).filter(Item.CategoryID == category_id).group_by(Item.ID).all()

    results = []
    for entry in items:
        item = entry[0]
        direct_sale = [listing for listing in item.listings if type(listing) is DirectSaleListing]
        auction = [listing for listing in item.listings if type(listing) is AuctionListing]
        rating = entry[1] or 0
        results.append({
            "item": item,
            "available": any(auction) or any(direct_sale),
            "auctions": auction,
            "direct_sales": direct_sale,
            "min_direct_sale": min([listing.Price for listing in direct_sale]) if direct_sale else None,
            "link": reverse("view_item", kwargs={"item_id": item.ID}),
            "rating": rating
        })

    return render(request, "listing/../../templates/item/browse.html", {
        "category": category,
        "active_category": category_id,
        "items": results,
        "create_link": reverse("create_item", kwargs={"category_id": category_id})
    })