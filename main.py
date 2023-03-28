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
    delta_limit: int = 20
    timedelta: dict = {'seconds': 5}
    set_to_db: dict = {'seconds': 20}

timedelta: Optional[datetime.timedelta] = None
future = None
settings: Optional[ManagerSettings] = None

def to_history():
    global settings, future
    now = datetime.datetime.now()
    if not future:
        future = now + timedelta
    remaining_seconds = (future - now).total_seconds()
    if remaining_seconds < 0:
        print('save the data')
        future = now + timedelta


async def main1(data):
    print('start')
    item_list = await pars.get_items(data)
    print('end pars')
    items_obj_dict = get_items_obj_dict(item_list, ItemMakeup)
    manager = CompareManagerItem(items_obj_dict, items_obj_dict)
    compare_item = manager.to_compare(ua_eu_strategy)
    # print(set(compare_item))
    limit = settings.delta_limit
    for r in filter(lambda x: x > -limit, sorted(compare_item, reverse=True)):
        # bot = telegram.Bot(token='token')
        # await bot.send_message(chat_id='1000612443', text=str(r))
        print(r)
    print('#'*10)

    to_history()

async def handle_client(reader, writer):
    global settings, timedelta
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            try:
                res = json.loads(data.decode())
                settings = ManagerSettings(**res)
                timedelta = datetime.timedelta(**settings.set_to_db)
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



