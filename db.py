import abc
import shelve
import sqlite3
import time
from collections import deque, defaultdict
from typing import NamedTuple, Deque, Sequence, Dict, TypeVar, Iterable

from data import ItemMakeup

ItemId = TypeVar('ItemId', bound=str)

class Hist(NamedTuple):
    time: float
    price: float

class SavePrice(abc.ABC):
    db_name = 'prices_db'

    @abc.abstractmethod
    def create_tables(self):
        pass

    @abc.abstractmethod
    def add_price(self, item: ItemId, price: float) -> None:
        pass

    @abc.abstractmethod
    def get_prices(self, items: Iterable[ItemId]) -> Dict[ItemId, Deque[Hist]]:
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        pass

class SavePriceDeque(SavePrice):

    def __init__(self):
        self.db = shelve.open(f'prices_db/{self.db_name}.db', writeback=True)

    def __del__(self):
        self.db.close()

    def create_tables(self):
        pass

    def add_price(self, item_id, price):
        try:
            self.db[item_id].append((time.time(), price))
        except KeyError:
            self.db[item_id] = deque([(time.time(), price)], maxlen=1000)

    def get_prices(self, items):
        return {item: list(self.db[item]) for item in items if item in self.db}

    def commit(self):
        self.db.sync()
