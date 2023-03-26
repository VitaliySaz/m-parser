import asyncio
from typing import Iterable, Tuple
import aiohttp
from aiohttp import ClientResponse
from bs4 import BeautifulSoup


def get_page_products_id(text_html: str) -> Iterable[str]:
    text_soup = BeautifulSoup(text_html, 'html.parser')
    for a in text_soup.find_all('a'):
        link = a.get('href')
        if 'product' in link:
            yield link.split('/')[2]

async def aiohttp_request(url, post=False, **kwargs) -> Tuple[ClientResponse, str]:
    if 'timeout' in kwargs:
        ten_millis = aiohttp.ClientTimeout(total=kwargs['timeout'])
        kwargs['timeout'] = ten_millis
    async with aiohttp.ClientSession() as session:
        async with (session.get, session.post)[post](url, **kwargs) as resp:
            return resp, await resp.text()

def exceptions_handler():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except asyncio.exceptions.TimeoutError as ex:
                print(f'Помилка TimeoutError: {func.__name__} де {args, kwargs}')
            except aiohttp.ClientConnectorError:
                print('Cannot connect to host')
        return wrapper
    return decorator


def get_items_obj_dict(item_list, item_obj):
    res_dict = {}
    for i_dict in item_list:
        item_id = {
            'item_id': str(i_dict['id']),
            'price': float(i_dict['price']),
            'value': str(i_dict['value_with_wh']),
            'product_id': str(i_dict['product_id']),
        }
        res_dict[item_id['item_id']] = item_obj(**item_id)
    return res_dict
