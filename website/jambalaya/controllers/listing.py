from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from jambalaya.forms import CreateListingForm
from jambalaya.models import Item, AuctionListing, DirectSaleListing


def __make_listing(form, user):
    if not form["is_auction"] and not user.seller:
        raise SystemError("Request was tampered with")

    if form["is_auction"]:
        listing = AuctionListing(MinPrice=form["auction_min_price"])
    else:
        listing = DirectSaleListing(Price=form["direct_sale_price"], Quantity=form["quantity"], Seller=user.seller)
    listing.Website = form["website"]
    listing.Condition = form["condition"]
    listing.User = user
    return listing


@login_required
def create(request, item_id):
    # Are we creating a listing for an item we haven't created yet?
    item = None
    session = request.db_session
    prev_form = {}
    if ("new_item_token" in request.session) and (request.session["new_item_token"] == item_id):
        prev_form = request.session["create_item_form"]
        item_name = prev_form["item_name"]
    else:
        item = session.query(Item).filter(Item.ID == item_id).one()
        item_name = item.Name

    is_seller = not not request.s_user.seller

    if request.method == "GET":
        form = CreateListingForm(is_seller=is_seller, item_id=item_id)
    else:
        form = CreateListingForm(request.POST, is_seller=is_seller, item_id=item_id)
        if form.is_valid():
            # Create the listing
            if not item:
                item = Item(Name=prev_form["item_name"], Description=prev_form["description"],
                            CategoryID=prev_form["category"], ImageBlob= prev_form["image"])
                session.add(item)
            listing = __make_listing(form.cleaned_data, request.s_user)
            item.listings.append(listing)
            return HttpResponseRedirect(reverse("home"))

    return render(request, "listing/create.html",
                  {"form": form, "item_name": item_name, "item_exists": item is not None, "is_seller": is_seller})