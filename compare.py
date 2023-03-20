from __future__ import annotations
import typing as _

import data
from data import PriceHistory, ComparePrices

from db import PriceDB


strategies = {}
db = PriceDB()

def compare(item_dict: dict[str, data.Item], strategy: str):
    for item in item_dict.values():
        try:
            history = strategies[strategy](item)
            yield ComparePrices(item, history)
        except ValueError:
            continue

def add_to_history(item_dict: dict[str, data.Item]):
    for value in item_dict.values():
        db.add_price(item=value.item_id, price=value.price)
    db.commit()

##############

def _register(func):
    strategies[func.__name__] = func
    return func

@_register
def simple_strategy(item: data.Item) -> PriceHistory:
    history = db.get_prices(item.item_id)
    return PriceHistory(item.item_id, history)

@_register
def ua_eu_strategy(item: data.Item) -> PriceHistory:
    if not item.is_eu:
        raise ValueError
    history = db.get_prices(item.id_ua)
    return PriceHistory(item.item_id, history)
