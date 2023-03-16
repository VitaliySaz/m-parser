import asyncio
import json
from collections import UserDict, UserList
from dataclasses import dataclass, field

from typing import Set, Optional

from utils import aiohttp_request, exceptions_handler, get_page_products_id


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

HEADERS = {
    'Content type': 'text_html/javascript; charset=utf-8',
    'Accept': 'application/json, text_html/javascript, */*; q=0.01; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Appl'
                  'eWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'}


class Item:

    def __init__(self, item_id: str, product_id: str, price: float, **kwargs):
        self.product_id = str(product_id)
        self.item_id = str(item_id)
        self.price = float(price)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"Item(item_id='{self.item_id}', price={self.price})"

    def __eq__(self, other):
        return self.item_id == other

    @property
    def is_eu(self) -> bool:
        return '_' in self.item_id

    @property
    def id_ua(self) -> str:
        return self.item_id.split('_')[0]


@dataclass
class Settings:
    category_id: int
    page_count: int
    data: dict = field(default_factory=dict)


class ParserProducts:

    COUNT_PRODUCTS_IN_PAGE = 36
    PAGE_URL = 'https://makeup.com.ua/ajax/filter/'

    def __init__(self, settings: Settings):
        self.settings = settings
        self.product_set = set()

    async def get_product_set(self):
        tasks = [asyncio.create_task(self._get_page_products_set(num))
                 for num in range(self.settings.page_count)]
        await asyncio.gather(*tasks)

    @exceptions_handler()
    async def _get_page_products_set(self, page_num: int):
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


class ParserItems:
    ITEM_URL = 'https://makeup.com.ua/ajax/product/{}/options/'

    def __init__(self, product_id_set: Set[str]):
        self.product_id_set = product_id_set
        self.item_dict = {}

    @exceptions_handler()
    async def _set_product_items(self, product_id: str):
        resp, json_items = await aiohttp_request(
            self.ITEM_URL.format(product_id),
            headers=HEADERS)
        if resp.status == 200:
            for item in json.loads(json_items):
                item.update({'product_id': product_id, 'item_id': item.pop('id')})
                self.item_dict[item['item_id']] = Item(**item)

    async def get_item_dict(self):
        await asyncio.gather(
            *[asyncio.create_task(self._set_product_items(pr)) for pr in self.product_id_set]
        )

async def get_items(settings: Settings):
    pr = ParserProducts(settings)
    await pr.get_product_set()
    it = ParserItems(pr.product_set)
    await it.get_item_dict()
    return it.item_dict
