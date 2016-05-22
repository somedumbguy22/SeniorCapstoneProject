from sqlalchemy import Column, ForeignKey, Integer, String, func, desc, asc
from sqlalchemy.orm import relationship

from models import Base, Item


class Category(Base):
    __tablename__ = 'Category'

    ID = Column(Integer, primary_key=True)
    Name = Column(String(255), nullable=False)
    ParentCategoryID = Column(ForeignKey(u'Category.ID', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)

    parent = relationship(u'Category', remote_side=[ID], backref="children")

    @classmethod
    def eager_load_tree(cls, session, visitor_fn=None):
        all_data = session.query(Category, func.count(Item.ID)).outerjoin(Item).group_by(Category.ID).order_by(
            desc(func.isnull(Category.ParentCategoryID)), asc(Category.Name)).all()

        # Create a mapping of parent => children
        parent_to_child = {}
        top_level = []

        for tup in all_data:
            node = tup[0]
            if node.ParentCategoryID is None:
                top_level.append(tup)
            else:
                parent_to_child.setdefault(node.ParentCategoryID, []).append(tup)

        # Actually build the nested tree structure
        def recurse(nodes):
            ret = []
            for node, item_count in nodes:
                children = recurse(parent_to_child.setdefault(node.ID, []))
                if visitor_fn:
                    ret.append(visitor_fn(node, item_count, children))
                else:
                    entry = {
                        "category": node,
                        "children": children,
                        "item_count": item_count
                    }
                    ret.append(entry)
            return ret

        return recurse(top_level), parent_to_child