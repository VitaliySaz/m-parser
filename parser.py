import asyncio
import json
import time
from dataclasses import dataclass, field
from pprint import pprint
from typing import NamedTuple, Tuple, Union, ClassVar, Dict, Optional, Set, List, Iterable

import aiohttp
import requests
from bs4 import BeautifulSoup

from utils import get_links_id

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

headers = {
    'Content type': 'text/javascript; charset=utf-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


@dataclass
class Item:
    id: int
    value: str
    img: str
    price: str
    price_old: str
    checked: bool
    wished: bool


@dataclass
class Product:
    _items_url = 'https://makeup.com.ua/ajax/product/{}/options/'

    id: str
    items: list = field(default_factory=list)

    async def set_product_items(self) -> None:
        print(self.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(self._items_url.format(self.id), headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    self.items.append(json.loads(text))

@dataclass
class Pages:
    __products_id = set()

    url: str
    count_pages: int

    @property
    def products_id(self) -> Set[str]:
        for page in self._get_all_pages():
            self.__products_id |= set(self._get_all_products_in_page(page))
        return self.__products_id

    def _get_all_pages(self) -> Iterable[str]:
        response = requests.get(self.url)
        yield response.text

    @staticmethod
    def _get_all_products_in_page(page: str) -> Iterable[str]:
        soup = BeautifulSoup(page, 'html.parser')
        for a in soup.find_all('a'):
            link = a.get('href')
            if 'product' in link:
                yield link.split('/')[3]


@dataclass
class Pars:
    __products = list()

    url: str

    @property
    def products(self) -> List[Product]:
        return self.__products

    def get_count_pages(self) -> int:
        return 1

    def set_products(self) -> None:
        pages = Pages(self.url, self.get_count_pages())
        for product_id in pages.products_id:
            self.products.append(Product(product_id))
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(
            asyncio.gather(*[p.set_product_items() for p in self.products]))
        event_loop.close()


if __name__ == '__main__':

    pars = Pars('https://makeup.com.ua/ua/categorys/3/')
    pars.set_products()

