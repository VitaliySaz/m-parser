import json
import time
import asyncio
import datetime
from pprint import pprint
from typing import NamedTuple, Optional, List
from loguru import logger

import telegram

import pars
from compare import CompareItemToHistory, ua_eu_strategy, CompareItemToItem, simple_strategy
from data import ItemMakeup
from manager import Manager
from timechecker import CallAfterTimedeltaError, OtherTimeError, TimeChecker
from utils import get_items_obj_dict


class Settings(NamedTuple):
    pars: List[dict]
    delta_limit: int = 1
    pars_interval: dict = {'seconds': 5}
    add_to_history_interval: dict = {'seconds': 20}


settings: Optional[Settings] = None
logger.add("logs/main.log", rotation="500 MB")
time_check = TimeChecker()

@TimeChecker.call_within_timeframe(datetime.time(9, 0), datetime.time(23, 0))
async def gat_compares(data, manager):
    item_list = await pars.get_items(data)
    items_obj_dict = get_items_obj_dict(item_list, ItemMakeup)
    logger.info(f'got {len(items_obj_dict)} items')
    compare = CompareItemToHistory(items_obj_dict, simple_strategy)
    compare_set = set(comp for comp in compare if comp > settings.delta_limit)
    logger.info(f'got {len(compare)} compares')
    manager.add_comparison(compare_set)
    logger.info(f'\n --- got base_compare: {len(manager.base_compare)}'
                f'\n --- got new_compare: {len(manager.new_compare)}'
                f'\n --- got difference: {len(manager.difference)}')
    try:
        res = time_check.call_after_delta(settings.add_to_history_interval)
        res(compare.add_to_history)()
        logger.info(f'add {len(compare)} to history')
    except OtherTimeError as ex:
        logger.info(ex)
    return sorted(list(manager.difference), reverse=True)


async def handle_client(reader, writer):
    global settings
    try:
        while True:
            try:
                data = await reader.read(2048)
                res = json.loads(data.decode())
                settings = Settings(**res)
            except TypeError:
                raise ConnectionResetError
            manager = Manager()
            print('value is obtained', settings)
            while True:
                await writer.drain()
                await asyncio.sleep(datetime.timedelta(**settings.pars_interval).seconds)
                for pars_data in settings.pars:
                    try:
                        res = await gat_compares(pars.Settings(**pars_data), manager)
                    except CallAfterTimedeltaError as ex:
                        logger.info(ex)
                        continue
                    if res:
                        writer.write(json.dumps([str(x) for x in res]).encode())
    except ConnectionResetError:
        logger.info('The client disconnected')
    finally:
        writer.close()


async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 6060)
    async with server:
        await server.serve_forever()


def run():
    asyncio.run(main())


if __name__ == '__main__':
    try:
        run()
    except:
        logger.exception("What?!")

