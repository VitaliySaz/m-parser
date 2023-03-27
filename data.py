from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Complex
from statistics import mean
from typing import *

@dataclass
class ItemBase:

    item_id: str
    price: float

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


@dataclass
class Item(ItemBase):

    product_id: str
    value: str

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
class ItemHistory(ItemBase):

    @property
    def middle_price(self):
        return self.price


ItemT = TypeVar('ItemT', bound=ItemBase)

@dataclass
class ComparePrices:

    item: Item
    compare: ItemT
    price_delta: float = field(init=False, default=None)

    def __post_init__(self):
        self.price_delta = ((self.item.price - self.compare.price) / self.compare.price) * 100

    def __repr__(self):
        return f'<{type(self).__name__}: {self.item}, {self.compare}, {self.price_delta}>'

    def __str__(self):
        return f'https://makeup.com.ua/ua/product/{self.item.product_id}/\n ' \
               f'| {self.item.value} : {self.item.price} | {self.price_delta}'

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

