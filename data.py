from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Complex
from statistics import mean
from typing import *

@dataclass
class ItemBase:

    """Клас ItemBase є базовим класом, який визначає деякі спільні властивості
    та методи для об'єктів товарів, включаючи ідентифікатор товару та його ціну,
     а також методи для порівняння, рівності та хешування."""

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
class ItemMakeup(ItemBase):

    """Клас Item розширює ItemBase конкретно для роботи з магазином Makeup.com.ua і додає
    дві властивості для отримання ідентифікатора  продукту та його значення, а також методи
     для визначення того, чи є товар в ЄС та отримання його ідентифікаторів в ЄС та Україні."""

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

    def __hash__(self):
        return hash(self.item_id)

@dataclass
class ItemMakeupHistory(ItemBase):

    """Клас ItemMakeupHistory також є підкласом класу ItemBase,
    але не містить жодних додаткових властивостей чи методів.
    Його призначення - зберігати історію цін на продукт."""

    @property
    def middle_price(self):
        return self.price


ItemT = TypeVar('ItemT', bound=ItemBase)

@dataclass
class CompareMakeupPrices:

    """Клас CompareMakeupPrices призначений для порівняння цін на продукти
     в магазині Makeup.com.ua. Він містить об'єкти типу ItemMakeup та ItemT
     який може бути будь-яким підкласом ItemBase, включаючи ItemMakeup та ItemMakeupHistory,
      а також атрибут price_delta (різниця в цінах між продуктами у відсотках).
      Клас також містить методи для порівняння та хешування."""

    item: ItemMakeup
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

