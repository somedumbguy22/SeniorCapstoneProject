__author__ = 'Aakash Sham'
import re

from django.shortcuts import render
from sqlalchemy import func
from datetime import datetime, timedelta

from jambalaya.models import Order, OrderListing, DirectSaleListing, Listing


def getHotItems(request):
    session = request.db_session

    hot = []
    foundEntries = False


    curr_date = datetime.now()
    hot_dates = datetime.now() - timedelta(days=5)


    hot_items = session.query(DirectSaleListing.ItemID, func.sum(OrderListing.Quantitiy), Order.Timestamp).join(OrderListing).\
        join(Order).having((func.sum(OrderListing.Quantitiy)) > 5).filter(Order.Timestamp <= curr_date).\
        filter(Order.Timestamp >= hot_dates).group_by(DirectSaleListing.ItemID).all()

    for itms in hot_items:
        hot.append(itms)


    if hot:
        foundEntries = True


    return render(request, 'item/hot_deals.html',
                  {'foundEntries': foundEntries, 'hot_items': hot_items})


    #------------------------------------------------------------------------#


    # This is the SQL for the Hot Items Query - Need to convert to SQL Alchemy
    # Select l.ItemId, Sum(ol.Quantitiy) as count, o.TimeStamp
    # From orderListing ol
    # join listing l on l.id = ol.ListingId
    # join `order` o on o.Id = ol.OrderId
    # group by l.ItemId
    # having count > 5

    #------------------------------------------------------------------------#

    #items = session.query(Item).group_by(Item.ID).all()

    # itemCount = 0
    # #360NoScopeAcrossTheMapDome <---Quality Comments Right Here
    # for item in items:
    #     for order in orders:
    #         if((order.contains(item)) and (order.Timestamp.DateTime > date.today().day - 5)):
    #             itemCount = itemCount + 1
    #     if (itemCount > 5):
    #         hot_items.append(item)
    #
    # if itemCount > 0:
    #     foundEntries = True

    #------------------------------------------------------------------------#