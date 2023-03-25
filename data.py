from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Complex
from statistics import mean
from typing import *


class Item:

    def __init__(self, item_id: str, product_id: str, price: float, **kwargs):
        self.item_id = str(item_id)
        self.product_id = str(product_id)
        self.price = float(price)
        self.value_with_wh = None
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.item_id}, {self.price}>"

    def __str__(self):
        return self.item_id

    def __eq__(self, other):
        return self.item_id == other.item_id

    def __lt__(self, other):
        return self.price > other.price

    def __gt__(self, other):
        return self.price < other.price

    def __hash__(self):
        return hash(self.item_id)

    @property
    def is_eu(self) -> bool:
        return '_' in self.item_id

    @property
    def id_ua(self) -> str:
        return self.item_id.split('_')[0]

    @property
    def id_eu(self) -> str:
        if self.is_eu:
            return self.item_id
        return self.item_id + '_3'


@dataclass
class PriceHistory:
    item_id: str
    prices: Deque[tuple] = field(repr=False)

    def __post_init__(self):
        self.price_list = [price[1] for price in self.prices]
        self.middle_price = mean(self.price_list)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.item_id}, {self.middle_price}>'

    def __bool__(self):
        return bool(self.prices)


@dataclass
class ComparePrices:
    item: Item
    history: PriceHistory
    price_delta: float = field(init=False, default=None)

    def __post_init__(self):
        self.price_delta = ((self.item.price - self.history.middle_price) / self.history.middle_price) * 100

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.item}, {self.history}, {self.price_delta}>'

    def __str__(self):
        return f'https://makeup.com.ua/ua/product/{self.item.product_id}/\n ' \
               f'| {self.item.value_with_wh} : {self.item.price} | {self.price_delta}'

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.price_delta > other.price_delta
        return self.price_delta > other

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.price_delta < other.price_delta
        return self.price_delta < other

    def __hash__(self):
        return hash(self.item)

