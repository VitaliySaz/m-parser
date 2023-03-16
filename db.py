import sqlite3
from dataclasses import dataclass, field
from statistics import mean
from typing import List


@dataclass
class PriceHistory:
    id: str
    prices: List[tuple] = field(repr=False)

    def __bool__(self):
        return bool(self.prices)

    @property
    def price_list(self):
        return [price[0] for price in self.prices]

    @property
    def middle_price(self):
        return mean(self.price_list)


class PriceDB:
    CREATE_TABLES = ("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item VARCHAR(20) NOT NULL UNIQUE         
            );
        """,
                     f"""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_item INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_item) REFERENCES items (item_id)
            );
        """)
    GET_ID_ITEM = "SELECT id FROM items WHERE item = ?"
    SAVE_ITEM = "INSERT INTO items (item) VALUES (?)"
    SAVE_PRICES = "INSERT INTO prices (id_item, price) VALUES (?, ?)"
    GET_PRICES = "SELECT id_item, price, created_at FROM prices WHERE id_item = ?"

    db_name = 'prices'

    def __init__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def create_tables(self):
        for table in self.CREATE_TABLES:
            self.cur.execute(table)

    def add_price(self, item, price):
        self.cur.execute(self.GET_ID_ITEM, (item,))
        if not self.cur.fetchone():
            self.cur.execute(self.SAVE_ITEM, (item,))
        self.cur.execute(self.SAVE_PRICES, (item, price))

    def get_prices(self, item):
        self.cur.execute(self.GET_PRICES, (item,))
        rows = self.cur.fetchall()
        return PriceHistory(item, [row[1:] for row in rows])

    def commit(self):
        self.conn.commit()
