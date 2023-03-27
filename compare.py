from __future__ import annotations

import abc
from statistics import mean
from typing import Sequence, NamedTuple, List, Iterable, Dict, Callable, Tuple

from data import Item, ItemHistory, ComparePrices, ItemT
from db import SavePriceDeque, SavePrice

strategies = {}


class CompareManagerBase(abc.ABC):

    def __init__(self, dict_item: Dict[str, Item]):
        self.dict_item = dict_item

    @abc.abstractmethod
    def get_compare_data(self, compare_list: Dict[str, str]) -> Dict[str, ItemT]:
        pass

    def to_compare(self, strategy: Callable[[Iterable[Item]], dict]):
        compare_list = strategy(self.dict_item.values())
        compare_data = self.get_compare_data(compare_list)
        for base_id, compare_obj in compare_data.items():
            if not self.dict_item.get(base_id):
                continue
            yield ComparePrices(item=self.dict_item[base_id], compare=compare_obj)


class DbManagerBase:
    db = SavePriceDeque()

    def add_to_history(self, dict_item):
        for value in dict_item.values():
            self.db.add_price(item_id=value.item_id, price=value.price)
        self.db.commit()


class CompareManagerHistory(DbManagerBase, CompareManagerBase):

    def get_compare_data(self, compare_list):
        compare_data = {}
        prices = self.db.get_prices(compare_list.values())
        for item_id, prices in prices.items():
            mean_price = mean(price[1] for price in prices)
            compare_data[item_id] = ItemHistory(item_id=item_id, price=mean_price)
        return compare_data


class CompareManagerItem(CompareManagerBase):

    db = SavePriceDeque()

    def __init__(self, dict_item, dict_item_compare):
        super().__init__(dict_item)
        self.dict_item_compare = dict_item_compare

    def get_compare_data(self, compare_list):
        return self.dict_item_compare

##############

def simple_strategy(items: Iterable[Item]) -> dict:
    return {item.item_id: item.item_id for item in items}


def ua_eu_strategy(items: Iterable[Item]) -> dict:
    return {item.item_id: item.id_ua for item in items}
