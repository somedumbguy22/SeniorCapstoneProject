import re

from django.shortcuts import render
from sqlalchemy import func
from django.core.urlresolvers import reverse

from jambalaya.models import Item, DirectSaleListing, AuctionListing, ItemRating


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string):
    terms = normalize_query(query_string)
    query = terms

    return query


def search(request):
    session = request.db_session
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string)

        items = session.query(Item, func.avg(ItemRating.Rating)).outerjoin(ItemRating).filter(
            Item.Name.like('%' + entry_query[0] + '%')).group_by(Item.ID).all()

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

        # for words in entry_query:
        # objects = request.db_session.query(Item).\
        # filter(Item.Name.like('%' +words+ '%'))
        #
        # for object in objects:
        #     found_entries.append(object)

        return render(request, 'item/search.html',
                      {'query_string': query_string, 'items': results})