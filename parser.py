import asyncio
import json
import time
from dataclasses import dataclass, field
from pprint import pprint
from typing import NamedTuple, Tuple, Union, ClassVar, Dict, Optional, Set, List, Iterable

import aiohttp
import requests
from bs4 import BeautifulSoup

class Item:
    def __init__(self, product_id: str,  item: dict):
        self.product_id = product_id
        self.item_id: Optional[int] = None
        self.item_value: Optional[str] = None
        self.item_value_with_wh: Optional[str] = None
        self.item_img: Optional[str] = None
        self.item_thumb: Optional[str] = None
        self.item_price: Optional[int] = None
        self.item_price_old: Optional[int] = None
        self.item_checked: Optional[bool] = None
        self.item_wished: Optional[bool] = None

        for key, value in item.items():
            setattr(self, 'item_'+key, value)


class Products:

    COUNT_PRODUCTS_IN_PAGE = 36

    HEADERS = {
        'Content type': 'text_html/javascript; charset=utf-8',
        'Accept': 'application/json, text_html/javascript, */*; q=0.01; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Appl'
                      'eWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    PAGE_URL = 'https://makeup.com.ua/ajax/filter/'

    def __init__(self, category: str, page_count: int):
        self.category = category
        self.page_count = page_count
        self.products_id = set()

    @staticmethod
    def _get_page_products_id(text_html: str):
        text_soup = BeautifulSoup(text_html, 'html.parser')
        for a in text_soup.find_all('a'):
            link = a.get('href')
            if 'product' in link:
                yield link.split('/')[2]

    def _get_page_data(self, page_num: int) -> dict:
        return {
            'offset': page_num * self.COUNT_PRODUCTS_IN_PAGE,
            'click': 'pager',
            'categoryID': self.category
        }

    async def _get_page_text(self, page_num: int) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.PAGE_URL,
                    data=self._get_page_data(page_num),
                    headers=self.HEADERS
            ) as resp:
                if resp.status == 200:
                    return json.loads(await resp.text())['products']

    def _set_products_id(self, pages: str):
        for page in pages:
            self.products_id |= set(self._get_page_products_id(page))


class ProductItem(Products):

    ITEM_URL = 'https://makeup.com.ua/ajax/product/{}/options/'

    def __init__(self, category: str, page_count: int):
        super().__init__(category, page_count)
        self.items: List[Item] = []

    async def set_product_items(self, product_id: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.ITEM_URL.format(product_id), headers=self.HEADERS) as resp:
                if resp.status == 200:
                    items = json.loads(await resp.text())
                    self.items.extend([Item(product_id, i) for i in items])


class Parser(ProductItem):

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    event_loop = asyncio.get_event_loop()

    async def _await_product_items_tasks(self):
        tasks = [self.set_product_items(task) for task in self.products_id]
        await asyncio.gather(*tasks)

    async def _await_page_text(self):
        tasks = [self._get_page_text(num) for num in range(self.page_count)]
        return await asyncio.gather(*tasks)

    def run(self):
        pages = self.event_loop.run_until_complete(self._await_page_text())
        self._set_products_id(pages)
        self.event_loop.run_until_complete(self._await_product_items_tasks())
        self.event_loop.close()


if __name__ == '__main__':
    start = time.time()
    pars = Parser(category='3', page_count=10)
    pars.run()
    print(len(pars.items))
    print(time.time() - start)
