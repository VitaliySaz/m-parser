from __future__ import annotations

from abc import ABC, abstractmethod
from collections import UserList
from dataclasses import dataclass

from tabulate import tabulate

import db
import pars


@dataclass
class ComparePrices:

    item: pars.Item
    history: db.PriceHistory

    @property
    def price_delta(self):
        return ((self.item.price - self.history.middle_price) / self.history.middle_price) * 100

    def __repr__(self):
        return f'{self.item.product_id:<15}' \
               f'{self.item.item_id:<15}' \
               f'{self.item.price:<15.2f}' \
               f'{self.history.id:<15}' \
               f'{self.history.middle_price:<15.2f}' \
               f'{self.price_delta:<15.2f}'


class ComparePricesList(UserList):

    def as_table(self, limit=0):
        data = [[h.item.product_id, h.item.item_id, h.history.id, h.item.price, h.history.middle_price, h.price_delta]
                for h in self.get_limit_delta(limit) if h.price_delta]
        headers = ["product_id", "item_id", "h_item_id", "item.price", "h_m_price", "h_price_delta"]
        return tabulate(data, headers=headers, tablefmt="outline", stralign='left', numalign='left')

    def get_limit_delta(self, limit=0):
        return [h for h in self.data if h.price_delta > limit]

    def sorted_by_price_delta(self):
        self.data.sort(key=lambda x: abs(x.price_delta), reverse=True)


class CompareStrategy(ABC):

    def __init__(self, item_dict: dict[str, pars.Item]):
        self.db = db.PriceDB()
        self.items = item_dict
        self.handlers = ComparePricesList()

    def compare(self):
        if self.handlers:
            return
        for item in self.items.values():
            res = self._compare(item)
            if res:
                self.handlers.append(ComparePrices(**res))

    @abstractmethod
    def _compare(self, item):
        pass

    def add_to_history(self):
        for item_data in self.items.values():
            self.db.add_price(item=item_data.item_id, price=item_data.price)
        self.db.commit()


class UaEuVsUaEuStrategy(CompareStrategy):

    def _compare(self, item: pars.Item):
        history = self.db.get_prices(item.item_id)
        if history:
            return dict(history=history, item=item)


class EuVsUaStrategy(CompareStrategy):

    def _compare(self, item):
        if not item.is_eu:
            return
        history = self.db.get_prices(item.id_ua)
        if history:
            return dict(history=history, item=item)

