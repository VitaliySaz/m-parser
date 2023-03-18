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

def get_only_sale_prices(compare_prices: _.Iterable[ComparePrices]) -> _.Iterable[ComparePrices]:
    for price in compare_prices:
        if price.price_delta < 0:
            yield price

def sorted_by_delta(compare_prices: _.Iterable[ComparePrices]) -> _.Iterable[ComparePrices]:
    return sorted(compare_prices, key=lambda x: x.price_delta)

def limited(compare_prices: _.Iterable[ComparePrices], limit=0) -> _.Iterable[ComparePrices]:
    return (cp for cp in compare_prices if cp.price_delta < -limit)

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
