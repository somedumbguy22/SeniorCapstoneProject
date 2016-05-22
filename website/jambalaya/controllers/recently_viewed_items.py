__author__ = 'Aakash Sham'

import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta

from jambalaya.models import RecentlyViewedItem, Item

@login_required
def recentlyViewedItems(request):

    session = request.db_session

    recently_viewed = []
    curr_date = datetime.now()
    recent_date = datetime.now() - timedelta(days=5)

    recent_items = session.query(RecentlyViewedItem.ItemID).\
        filter(RecentlyViewedItem.Timestamp <= curr_date).filter(RecentlyViewedItem.Timestamp >= recent_date).\
        group_by(RecentlyViewedItem.ItemID).all()

    all_items = session.query(Item).all()

    for result in recent_items:
        for item in all_items:
            if item.ID == result.ItemID:
                recently_viewed.append(item)


    return render(request, 'item/recently_viewed.html', {'recently_viewed': recently_viewed})