import json
import time
import asyncio
import datetime
from pprint import pprint
from typing import NamedTuple, Optional, List
from loguru import logger

import telegram

import pars
from compare import CompareItemToHistory, ua_eu_strategy, CompareItemToItem
from data import ItemMakeup
from manager import time_manager, Manager
from utils import get_items_obj_dict


class Settings(NamedTuple):
    pars: List[dict]
    delta_limit: int = 30
    timedelta: dict = {'seconds': 5}
    set_to_db: dict = {'seconds': 10}


settings: Optional[Settings] = None
logger.add("file_1.log", rotation="500 MB")

def to_history():
    print('save the data')


async def gat_compares(data, manager):
    item_list = await pars.get_items(data)
    items_obj_dict = get_items_obj_dict(item_list, ItemMakeup)
    # logger.info(f'got {len(items_obj_dict)} items')
    compare = CompareItemToHistory(items_obj_dict, ua_eu_strategy)
    # logger.info(f'got {len(set(compare))} compares')
    manager.add_comparison(compare)
    logger.info(f'\n got base_compare {len(set(manager.base_compare))} and'
                f'\n new_compare {len(set(manager.new_compare))} and'
                f'\n difference {len(set(manager.difference))}: {set(manager.difference)}')
    res = time_manager(settings.set_to_db)
    res(compare.add_to_history)()
    return sorted((comp for comp in manager.difference if comp > settings.delta_limit), reverse=True)


async def handle_client(reader, writer):
    global settings
    try:
        while True:
            data = await reader.read(2048)
            if not data:
                break
            try:
                res = json.loads(data.decode())
                settings = Settings(**res)
                manager = Manager()
                print('value is obtained', settings)
                while True:
                    for pars_data in settings.pars:
                        res = await gat_compares(pars.Settings(**pars_data), manager)
                        if res:
                            writer.write(json.dumps([str(x) for x in res]).encode())
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
