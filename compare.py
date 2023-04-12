from __future__ import annotations

import abc
from statistics import mean
from typing import Iterable, Dict

from data import ItemMakeup, ItemMakeupHistory, CompareMakeupPrices, ItemT
from db import SavePriceDeque

strategies = {}
compares = {}


def register_strategy(strategy):
    strategies[strategy.__name__] = strategy
    return strategy


def register_compare(compare):
    compares[compare.__name__] = compare
    return compare


class CompareBase(abc.ABC):
    """Клас CompareBase є абстрактним базовим класом
    для управління порівнянням товарів в інтернет-магазині Makeup.com.ua"""

    def __init__(self, dict_item: Dict[str, ItemMakeup], strategy):
        self.dict_item = dict_item
        self.strategy = strategy

    @abc.abstractmethod
    def get_compare_data(self, compare_dict: Dict[str, str]) -> Iterable[str, ItemT]:
        pass

    def __iter__(self):
        compare_dict = self.strategy(self.dict_item.values())
        compare_data = self.get_compare_data(compare_dict)
        for base_id, compare_obj in compare_data:
            if not self.dict_item.get(base_id):
                continue
            yield CompareMakeupPrices(item=self.dict_item[base_id], compare=compare_obj)

    def __len__(self):
        return len(self.dict_item)


class DbMixin:
    db = SavePriceDeque()

    def add_to_history(self):
        for value in self.dict_item.values():
            self.db.add_price(item_id=value.item_id, price=value.price)
        self.db.commit()

    def get_prices_dict(self, compare_dict):
        return self.db.get_prices(compare_dict.values())


@register_compare
class CompareItemToHistory(DbMixin, CompareBase):

    def get_compare_data(self, compare_dict):
        prices_dict = self.get_prices_dict(compare_dict)
        for base_id, compare_id in compare_dict.items():
            if not (prices := prices_dict.get(compare_id)):
                continue
            mean_price = mean(price[1] for price in prices)
            yield base_id, ItemMakeupHistory(item_id=compare_id, price=mean_price)


@register_compare
class CompareItemToItem(CompareBase):
    lost_dict_item = None

    def get_compare_data(self, compare_dict):
        for base_id, compare_id in compare_dict.items():
            try:
                compare_item = __class__.lost_dict_item[compare_id]
                yield base_id, compare_item
            except KeyError:
                continue
            except TypeError:
                break
        __class__.lost_dict_item = self.dict_item

##############

@register_strategy
def simple_strategy(items: Iterable[ItemMakeup]) -> Dict[str, str]:
    return {item.item_id: item.item_id for item in items}


@register_strategy
def ua_eu_strategy(items: Iterable[ItemMakeup]) -> Dict[str, str]:
    return {item.item_id: item.id_ua for item in items if item.is_eu}
