from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import *


class Item:

    def __init__(self, item_id: str, product_id: str, price: float, **kwargs):
        self.product_id = str(product_id)
        self.item_id = str(item_id)
        self.price = float(price)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.item_id}, {self.price}>"

    def __eq__(self, other):
        return self.item_id == other

    @property
    def is_eu(self) -> bool:
        return '_' in self.item_id

    @property
    def id_ua(self) -> str:
        return self.item_id.split('_')[0]


@dataclass
class PriceHistory:
    item_id: str
    prices: List[tuple] = field(repr=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.item_id}, {self.get_middle_price()}>'

    def __bool__(self):
        return bool(self.prices)

    def get_price_list(self):
        return [price[1] for price in self.prices]

    def get_middle_price(self):
        return mean(self.get_price_list())


@dataclass
class ComparePrices:
    item: Item
    history: PriceHistory

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.item}, {self.history}, {self.get_price_delta()}>'

    def get_price_delta(self):
        middle_price = self.history.get_middle_price()
        return ((self.item.price - middle_price) / middle_price) * 100

def get_only_sale_prices(compare_prices: Iterable[ComparePrices]) -> Iterable[ComparePrices]:
    for price in compare_prices:
        if price.get_price_delta() < 0:
            yield price

def sorted_by_delta(compare_prices: Iterable[ComparePrices]) -> Iterable[ComparePrices]:
    return sorted(compare_prices, key=lambda x: x.get_price_delta())
