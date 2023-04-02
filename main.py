import json
import time
import asyncio
import datetime
from pprint import pprint
from typing import NamedTuple, Optional, List

import telegram

import pars
from compare import CompareManagerHistory, ua_eu_strategy, CompareManagerItem
from data import ItemMakeup
from utils import get_items_obj_dict


class ManagerSettings(NamedTuple):
    pars: List[dict]
    delta_limit: int = 30
    timedelta: dict = {'seconds': 5}
    set_to_db: dict = {'seconds': 10}


settings: Optional[ManagerSettings] = None


def time_manager(timedelta):
    future = None

    def wrapper(func):
        def decorate(*args, **kwargs):
            nonlocal future
            td = datetime.timedelta(**timedelta)
            now = datetime.datetime.now()
            if not future:
                future = now + td
            remaining_seconds = (future - now).total_seconds()
            if remaining_seconds < 0:
                func(*args, **kwargs)
                future = now + td
        return decorate
    return wrapper

def to_history():
    print('save the data')


async def main1(data):
    print('start')
    item_list = await pars.get_items(data)
    print('end pars')
    items_obj_dict = get_items_obj_dict(item_list, ItemMakeup)
    manager = CompareManagerHistory(items_obj_dict)
    compare_item = manager.to_compare(ua_eu_strategy)
    # print(set(compare_item))
    limit = settings.delta_limit
    for r in filter(lambda x: x > limit, sorted(compare_item, reverse=True)):
        # bot = telegram.Bot(token='token')
        # await bot.send_message(chat_id='1000612443', text=str(r))
        print(r)
    print('#' * 10)
    res = time_manager(settings.set_to_db)
    dec = res(manager.add_to_history)
    dec()


async def handle_client(reader, writer):
    global settings
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            try:
                res = json.loads(data.decode())
                settings = ManagerSettings(**res)
                print('value is obtained', settings)
                while True:
                    for pars_data in settings.pars:
                        await main1(pars.Settings(**pars_data))
                    # writer.write(str(some_int).encode())
                    await writer.drain()
                    await asyncio.sleep(datetime.timedelta(**settings.timedelta).seconds)
            except Exception as e:
                writer.write(f'Error: {e}'.encode())
                raise e
    except ConnectionResetError:
        print(f'клієнт розірвар зєднання')
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 6060)
    async with server:
        await server.serve_forever()


def run():
    asyncio.run(main())


if __name__ == '__main__':
    run()
