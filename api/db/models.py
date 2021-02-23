from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, orm, String

from api.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)



class GoodsList(Base):
    __tablename__ = 'goods_list'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), unique=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = orm.relationship(
        'User',
        backref='goodslist',
        lazy='joined'
    )

    __table_args__ = (
        UniqueConstraint('name', 'user_id'),
    )


class Good(Base):
    __tablename__ = 'goods'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), unique=False)
    qtty = Column(Integer, nullable=False, default=1)
    list_id = Column(Integer, ForeignKey('goods_list.id'))
    good_list = orm.relationship(
        'GoodsList',
        backref='goods',
        lazy='joined'
    )

    __table_args__ = (
        UniqueConstraint('name', 'list_id'),
    )


Base.metadata.create_all()
