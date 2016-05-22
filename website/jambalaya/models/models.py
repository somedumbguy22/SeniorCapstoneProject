from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, text, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.base import BIT, LONGBLOB
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Address(Base):
    __tablename__ = 'Address'

    ID = Column(Integer, primary_key=True)
    StreetName = Column(String(255), nullable=False)
    StreetNumber = Column(Integer, nullable=False)
    State = Column(String(45), nullable=False)
    Zipcode = Column(Integer, nullable=False)
    PhoneNumber = Column(String(10))

    User = relationship(u'User', secondary='UserAddress', backref="addresses")


class Bid(Base):
    __tablename__ = 'Bid'

    Amount = Column(Float, nullable=False)
    Timestamp = Column(DateTime, primary_key=True, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False,
                    index=True)
    ListingID = Column(ForeignKey(u'Listing.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                       nullable=False, index=True)

    Listing = relationship(u'Listing', backref="bids")
    User = relationship(u'User', backref="bids")


class CartListing(Base):
    __tablename__ = 'CartListing'

    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    DirectSaleListingID = Column(
        ForeignKey(u'DirectSaleListing.ListingParentID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
        nullable=False, index=True)
    Quantity = Column(Integer, nullable=False)

    DirectSaleListing = relationship(u'DirectSaleListing')
    User = relationship(u'User', backref="cartlistings")


class CreditCardInfo(Base):
    __tablename__ = 'CreditCardInfo'

    Number = Column(Integer, primary_key=True, nullable=False)
    UserID = Column(ForeignKey(u'User.ID'), primary_key=True, nullable=False, index=True)
    Vendor = Column(String(255), nullable=False)
    ExpirationDate = Column(Date, nullable=False)
    SecurityCode = Column(Integer, nullable=False)
    AddressID = Column(ForeignKey(u'Address.ID', onupdate=u'CASCADE'), nullable=False, index=True)

    Address = relationship(u'Address')
    User = relationship(u'User', backref="creditcards")


class Item(Base):
    __tablename__ = 'Item'

    ID = Column(Integer, primary_key=True)
    Name = Column(String(255), nullable=False)
    Description = Column(String(255), nullable=False)
    CategoryID = Column(ForeignKey(u'Category.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False,
                        index=True)
    ImageBlob = Column(LONGBLOB)

    Category = relationship(u'Category', backref="items")


class ItemRating(Base):
    __tablename__ = 'ItemRating'

    ID = Column(Integer, primary_key=True)
    Comment = Column(String(140))
    Rating = Column(Integer, nullable=False)
    ItemID = Column(ForeignKey(u'Item.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)

    Item = relationship(u'Item', backref="ratings")
    User = relationship(u'User', backref="itemratings")


class Listing(Base):
    __tablename__ = 'Listing'

    ID = Column(Integer, primary_key=True)
    Website = Column(String(255), nullable=False)
    Condition = Column(String(255), nullable=False)
    ItemID = Column(ForeignKey(u'Item.ID'), nullable=False, index=True)
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    IsAuction = Column(BIT(1), nullable=False)
    Created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    Item = relationship(u'Item', backref="listings")
    User = relationship(u'User', backref="listings")

    __mapper_args__ = {
        'polymorphic_identity': 'listing',
        'polymorphic_on': IsAuction,
        'with_polymorphic': '*'
    }


class AuctionListing(Listing):
    __tablename__ = 'AuctionListing'

    ListingParentID = Column(ForeignKey(u'Listing.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True)
    MinPrice = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 1
    }


class DirectSaleListing(Listing):
    __tablename__ = 'DirectSaleListing'

    ListingParentID = Column(ForeignKey(u'Listing.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True)
    Price = Column(Float, nullable=False)
    Quantity = Column(Integer, nullable=False)
    SellerID = Column(ForeignKey(u'Seller.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)

    Seller = relationship(u'Seller')

    __mapper_args__ = {
        'polymorphic_identity': 0
    }


class Order(Base):
    __tablename__ = 'Order'

    ID = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    Total = Column(Float, nullable=False)
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    Status = Column(Integer, nullable=False)

    User = relationship(u'User', backref="user")


class OrderEvent(Base):
    __tablename__ = 'OrderEvent'

    OrderID = Column(ForeignKey(u'Order.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                     nullable=False)
    Timestamp = Column(DateTime, primary_key=True, nullable=False,
                       server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    Type = Column(Integer, nullable=False)

    Order = relationship(u'Order', backref="events")


class OrderListing(Base):
    __tablename__ = 'OrderListing'

    OrderID = Column(ForeignKey(u'Order.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
                     nullable=False)
    DirectSaleListingID = Column(
        ForeignKey(u'DirectSaleListing.ListingParentID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
        nullable=False, index=True)
    Quantitiy = Column(Integer, nullable=False)

    DirectSaleListing = relationship(u'DirectSaleListing')
    Order = relationship(u'Order', backref="listings")


class RecentlyViewedItem(Base):
    __tablename__ = 'RecentlyViewedItem'

    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False)
    ItemID = Column(ForeignKey(u'Item.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True, nullable=False,
                    index=True)
    Timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    Item = relationship(u'Item')
    User = relationship(u'User', backref="recentlyviewitems")


class Seller(Base):
    __tablename__ = 'Seller'

    ID = Column(Integer, primary_key=True)
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    Name = Column(String(255), nullable=False)
    Phone = Column(String(45), nullable=False)
    AddressID = Column(ForeignKey(u'Address.ID', onupdate=u'CASCADE'), nullable=False, index=True)

    Address = relationship(u'Address')
    User = relationship(u'User', backref="seller")


class SellerRating(Base):
    __tablename__ = 'SellerRating'

    ID = Column(Integer, primary_key=True)
    Comment = Column(String(140))
    Rating = Column(Integer, nullable=False)
    SellerID = Column(ForeignKey(u'Seller.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    UserID = Column(ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)

    Seller = relationship(u'Seller', backref="ratings")
    User = relationship(u'User', backref="sellerratings")


class User(Base):
    __tablename__ = 'User'

    ID = Column(Integer, primary_key=True)
    Email = Column(String(255), nullable=False, unique=True)
    FirstName = Column(String(255), nullable=False)
    LastName = Column(String(255), nullable=False)
    Password = Column(Text, nullable=False)
    Username = Column(String(30), nullable=False, unique=True)
    IsStaff = Column(BIT(1), nullable=False)
    DateJoined = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    LastLogin = Column(DateTime)


t_UserAddress = Table(
    'UserAddress', metadata,
    Column('UserID', ForeignKey(u'User.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
           nullable=False),
    Column('AddressID', ForeignKey(u'Address.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True,
           nullable=False, index=True)
)