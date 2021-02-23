from api.loggers import logger
from api.db import session_scope
from api.db.models import Good as DbGood, User as DbUser, GoodsList as DbGoodsList
from api.exceptions import ListNotExistsError, GoodInListAlreadyExistsError

from api.models import Good, GoodList


class Storage:

    @staticmethod
    def all_goods_in_list(user_id: int, list_name: str) -> list[Good]:
        goods = []
        with session_scope() as s:
            for good in s.query(DbGood.name, DbGood.qtty).join(DbGoodsList).filter(
                    DbGoodsList.name == list_name, DbGoodsList.user_id == user_id).all():
                goods.append(Good(good[0], good[1]))
        return goods

    @staticmethod
    def create_good_list(user_id: int, list_name: str):
        with session_scope() as s:
            user = s.query(DbUser).filter(DbUser.id == user_id).first()
            if not user:
                user = DbUser(id=user_id)
                s.add(user)
            s.add(
                DbGoodsList(name=list_name, user=user)
            )

    @staticmethod
    def add_new_item(user_id: int, item_name: str, list_name):
        with session_scope() as s:
            user = s.query(DbUser).filter(DbUser.id == user_id).first()
            if not user:
                user = DbUser(id=user_id)
                s.add(user)
            items_list = s.query(DbGoodsList).filter(DbGoodsList.name == list_name, user == user).first()

            if not items_list:
                raise ListNotExistsError

            item = s.query(DbGood).filter(DbGood.name == item_name, DbGood.good_list == items_list).first()
            if item:
                raise GoodInListAlreadyExistsError

            s.add(
                DbGood(name=item_name, list_id=items_list.id)
            )

    @staticmethod
    def delete_item(user_id: int, list_name: str, item_name: str):
        with session_scope() as s:
            item = s.query(DbGood).join(DbGoodsList).filter(
                    DbGoodsList.name == list_name,
                    DbGoodsList.user_id == user_id,
                    DbGood.name == item_name).first()

            s.delete(item)

    @staticmethod
    def delete_list(user_id: int, list_name: str):
        with session_scope() as s:
            item = s.query(DbGoodsList).filter(
                    DbGoodsList.name == list_name,
                    DbGoodsList.user_id == user_id).first()

            s.delete(item)

    @staticmethod
    def substract_item_qtty(user_id: int, list_name: str, item_name: str):
        with session_scope() as s:
            item = s.query(DbGood).join(DbGoodsList).filter(
                DbGoodsList.name == list_name,
                DbGoodsList.user_id == user_id,
                DbGood.name == item_name).first()
            if item.qtty == 1:
                s.delete(item)
            else:
                item.qtty -= 1
                s.add(item)

    def add_item_qtty(user_id: int, list_name: str, item_name: str):
        with session_scope() as s:
            item = s.query(DbGood).join(DbGoodsList).filter(
                DbGoodsList.name == list_name,
                DbGoodsList.user_id == user_id,
                DbGood.name == item_name).first()
            item.qtty += 1
            s.add(item)

    @staticmethod
    def all_list(user_id: int) -> list[GoodList]:
        items = []
        with session_scope() as s:
            for item in s.query(DbGoodsList.name).filter(DbGoodsList.user_id == user_id).all():
                items.append(
                    GoodList(item[0])
                )
        return items
