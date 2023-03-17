from __future__ import annotations
import typing as _

import data
from data import PriceHistory, ComparePrices

from db import PriceDB


class Manager:

    def __init__(
            self,
            item_dict: dict[str, data.Item],
            strategy: _.Callable
    ) -> None:
        self.db = PriceDB()
        self.items = item_dict
        self.strategy = strategy

    def compare(self) -> _.Iterable[ComparePrices]:
        for item in self.items.values():
            try:
                history = self.strategy(self.db, item)
                yield ComparePrices(item, history)
            except ValueError:
                continue

    def add_to_history(self):
        for value in self.items.values():
            self.db.add_price(item=value.item_id, price=value.price)
        self.db.commit()

def simple_strategy(db: PriceDB, item: data.Item) -> PriceHistory:
    history = db.get_prices(item.item_id)
    return PriceHistory(item.item_id, history)

def ua_eu_strategy(db: PriceDB, item: data.Item) -> PriceHistory:
    if not item.is_eu:
        raise ValueError
    history = db.get_prices(item.id_ua)
    return PriceHistory(item.item_id, history)
