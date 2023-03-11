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
