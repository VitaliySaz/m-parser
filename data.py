from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List
import db
import pars


@dataclass
class ItemHandler:

    item: pars.Item
    history: db.PriceHistory

    @property
    def price_delta(self):
        return ((self.item.price - self.history.middle_price) / self.history.middle_price) * 100

    def __repr__(self):
        return f'{self.item.product_id:<10}' \
               f'{self.item.price:<10.2f}' \
               f'{self.history.middle_price:<10.2f}' \
               f'{self.price_delta:<10.2f}'


class ItemsManager(ABC):

    def __init__(self, item_dict: pars.ItemDict):
        self.db = db.PriceDB()
        self.items = item_dict
        self.handlers: List[ItemHandler] = []

    def compare(self):
        if self.handlers:
            return
        for item in self.items.values():
            res = self._compare(item)
            if res:
                self.handlers.append(ItemHandler(**res))

    @abstractmethod
    def _compare(self, item):
        pass

    def add_to_history(self):
        for item_data in self.items.values():
            self.db.add_price(item=item_data.id, price=item_data.price)
        self.db.commit()


class UaEuCompareUaEu(ItemsManager):

    def _compare(self, item):
        history = self.db.get_prices(item.id)
        if history:
            return dict(history=history, item=item)


class EuCompareUa(ItemsManager):

    def _compare(self, item):
        if not item.is_eu:
            return
        history = self.db.get_prices(item.id_ua)
        if history:
            return dict(history=history, item=item)

