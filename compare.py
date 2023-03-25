from __future__ import annotations

from typing import Sequence, NamedTuple, List, Iterable

from data import PriceHistory, ComparePrices, Item

from db import SavePriceDeque

strategies = {}
db = SavePriceDeque()

class CompareData(NamedTuple):
    item: str
    compare_item_id: str
    compare_data: tuple

def compare(item_dict: dict[str, Item], strategy: str):
    add_to_history(item_dict)
    res = strategies[strategy](item_dict.values())
    prices = db.get_prices([i for _, i in res])
    for id_, compare_id in res:
        price_hist, item = prices.get(compare_id), item_dict.get(id_)
        if not (price_hist and item):
            continue
        history = PriceHistory(item_id=compare_id, prices=price_hist)
        yield ComparePrices(item=item, history=history)

def add_to_history(item_dict: dict[str, Item]):
    for value in item_dict.values():
        db.add_price(item_id=value.item_id, price=value.price)
    db.commit()

##############

def _register(func):
    strategies[func.__name__] = func
    return func

@_register
def simple_strategy(items: Iterable[Item]) -> List[tuple]:
    return [(item.item_id, item.item_id) for item in items]

@_register
def ua_eu_strategy(items: Iterable[Item]) -> List[tuple]:
    return [(item.item_id, item.id_eu) for item in items]
