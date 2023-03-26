from __future__ import annotations

from statistics import mean
from typing import Sequence, NamedTuple, List, Iterable

from data import Item, ItemHistory, ComparePrices
from db import SavePriceDeque

strategies = {}
db = SavePriceDeque()

class CompareData(NamedTuple):
    item: str
    compare_item_id: str
    compare_data: tuple

def compare(item_dict: dict[str, Item], strategy: str):
    compare_list = strategies[strategy](item_dict.values())
    prices = db.get_prices(compare_id for _, compare_id in compare_list)
    for base_id, compare_id in compare_list:
        price_hist, item = prices.get(compare_id), item_dict.get(base_id)
        if not (price_hist and item):
            continue
        history = ItemHistory(item_id=compare_id, price=mean(price[1] for price in price_hist))
        yield ComparePrices(item=item, compare=history)

def add_to_history(item_dict: dict[str, Item]):
    for value in item_dict.values():
        db.add_price(item_id=value.item_id, price=value.price)
    db.commit()

##############

def _register(func):
    strategies[func.__name__] = func
    return func

@_register
def simple_strategy(items: Iterable[Item]) -> list:
    return [(item.item_id, item.item_id) for item in items]

@_register
def ua_eu_strategy(items: Iterable[Item]) -> list:
    return [(item.item_id, item.id_ua) for item in items]
