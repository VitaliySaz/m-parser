from __future__ import annotations

import abc
from statistics import mean
from typing import Sequence, NamedTuple, List, Iterable, Dict, Callable, Tuple

from data import ItemMakeup, ItemMakeupHistory, CompareMakeupPrices, ItemT
from db import SavePriceDeque, SavePrice

strategies = {}


class CompareManagerBase(abc.ABC):

    def __init__(self, dict_item: Dict[str, ItemMakeup]):
        self.dict_item = dict_item

    @abc.abstractmethod
    def get_compare_data(self, compare_list: Dict[str, str]) -> Iterable[str, ItemT]:
        pass

    def to_compare(self, strategy: Callable[[Iterable[ItemMakeup]], dict]):
        compare_dict = strategy(self.dict_item.values())
        compare_data = self.get_compare_data(compare_dict)
        for base_id, compare_obj in compare_data:
            if not self.dict_item.get(base_id):
                continue
            yield CompareMakeupPrices(item=self.dict_item[base_id], compare=compare_obj)


class DbManagerBase:
    db = SavePriceDeque()

    def add_to_history(self, dict_item):
        for value in dict_item.values():
            self.db.add_price(item_id=value.item_id, price=value.price)
        self.db.commit()


class CompareManagerHistory(DbManagerBase, CompareManagerBase):

    def get_compare_data(self, compare_dict):
        prices_dict = self.db.get_prices(compare_dict.values())
        for base_id, compare_id in compare_dict.items():
            if not (prices := prices_dict.get(compare_id)):
                continue
            mean_price = mean(price[1] for price in prices)
            yield base_id, ItemMakeupHistory(item_id=compare_id, price=mean_price)


class CompareManagerItem(CompareManagerBase):

    db = SavePriceDeque()

    def __init__(self, dict_item, dict_item_compare):
        super().__init__(dict_item)
        self.dict_item_compare = dict_item_compare

    def get_compare_data(self, compare_dict):
        for base_id, compare_id in compare_dict.items():
            if not (compare_item := self.dict_item_compare.get(compare_id)):
                continue
            yield base_id, compare_item

##############

def simple_strategy(items: Iterable[ItemMakeup]) -> dict:
    return {item.item_id: item.item_id for item in items}


def ua_eu_strategy(items: Iterable[ItemMakeup]) -> dict:
    return {item.item_id: item.id_ua for item in items if item.is_eu}
