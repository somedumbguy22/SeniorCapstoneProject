from models import *
from jambalaya.settings import Session
from category import *
import json
import random


def do_import():
    j = json.loads(open("jambalaya/models/output.txt", "r").read())
    session = Session(autoflush=False, autocommit=False)

    for item in j:
        name = item[0]
        blob = item[1]
        price = item[2]
        description = item[3]
        condition = item[4]
        ratings = item[5]
        category = item[6]
        print category

        category = session.query(Category).filter(Category.Name == category).one()

        new_item = Item()
        new_item.Name = name
        new_item.Description = description
        new_item.ImageBlob = blob
        new_item.Category = category

        is_auction = random.choice([True, False])

        if is_auction:
            new_listing = AuctionListing()
        else:
            new_listing = DirectSaleListing()

        new_listing.IsAuction = is_auction

        if new_listing.IsAuction == 0:
            new_listing.Price = price
            new_listing.Quantity = random.randrange(0, 20)
        else:
            new_listing.MinPrice = price

        new_item.listings = [new_listing]
        new_listing.Condition = condition
        new_listing.Website = "http://www.dammit.com"
        new_listing.SellerID = random.randrange(1, 30)

        for rating in ratings:
            score = rating[0]
            user = rating[1]
            comment = rating[2]
            new_rating = ItemRating()
            new_rating.Comment = comment
            if not user:
                user = random.randrange(1, 30)
            new_rating.UserID = user
            new_rating.Rating = score
            new_item.ratings.append(new_rating)

        session.add(new_item)

    session.commit()