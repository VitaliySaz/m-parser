import asyncio
import json
from collections import UserDict
from dataclasses import dataclass, field

from typing import Set, Optional

from utils import aiohttp_request, exceptions_handler, get_page_products_id


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HEADERS = {
    'Content type': 'text_html/javascript; charset=utf-8',
    'Accept': 'application/json, text_html/javascript, */*; q=0.01; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Appl'
                  'eWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

@dataclass
class Item:
    id: str
    product_id: str
    img: str
    price: float
    value_with_wh: str
    wished: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = str(self.id)
        self.price = float(self.price)

    def __repr__(self):
        return f"Item(id='{self.id}', price={self.price})"

    @property
    def is_eu(self) -> bool:
        return '_' in self.id

    @property
    def id_ua(self) -> str:
        return self.id.split('_')[0]

class ItemDict(UserDict):
    """Клас ItemDict функціонал для роботи з розпасеними позиціями товарів"""

    def __setitem__(self, key, value):
        self.data[str(key)] = Item(**value)


class ParserProducts:

    @dataclass
    class Settings:
        category_id: int
        page_count: int
        data: dict = field(default_factory=dict)

    COUNT_PRODUCTS_IN_PAGE = 36
    PAGE_URL = 'https://makeup.com.ua/ajax/filter/'

    def __init__(self, settings: Settings):
        self.settings = settings
        self.product_set = set()

    async def __await_page_text(self):
        tasks = [asyncio.create_task(self.__get_page_products_set(num))
                 for num in range(self.settings.page_count)]
        await asyncio.gather(*tasks)

    @exceptions_handler()
    async def __get_page_products_set(self, page_num: int):
        data = {'offset': page_num * self.COUNT_PRODUCTS_IN_PAGE,
                'click': 'pager',
                'categoryID': self.settings.category_id}
        data.update(self.settings.data)
        resp, text = await aiohttp_request(
            self.PAGE_URL,
            data=data,
            headers=HEADERS,
            post=True,
            timeout=50)
        if resp.status == 200:
            page = json.loads(text)['products']
            self.product_set |= set(get_page_products_id(page))

    def get_product_set(self):
        asyncio.run(self.__await_page_text())
        return self.product_set


class ParserItems:
    ITEM_URL = 'https://makeup.com.ua/ajax/product/{}/options/'

    def __init__(self, product_id_set: Set[str]):
        self.product_id_set = product_id_set
        self.item_dict = ItemDict()

    @exceptions_handler()
    async def _set_product_items(self, product_id: str):
        resp, json_items = await aiohttp_request(
            self.ITEM_URL.format(product_id),
            headers=HEADERS)
        if resp.status == 200:
            for item in json.loads(json_items):
                item.update({'product_id': product_id})
                self.item_dict[item['id']] = item

    async def _await_product_items_tasks(self):
        tasks = [asyncio.create_task(self._set_product_items(pr)) for pr in self.product_id_set]
        await asyncio.gather(*tasks)

    def get_item_dict(self):
        asyncio.run(self._await_product_items_tasks())
        return self.item_dict
