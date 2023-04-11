
import asyncio

from loguru import logger

import telegram

import pars
from compare import CompareItemToHistory, simple_strategy
from data import ItemMakeup
from manager import Manager
from settings import *
from timechecker import CallAfterTimedeltaError, OtherTimeError, TimeChecker
from utils import get_items_obj_dict


logger.add("logs/main.log", rotation="500 MB")
manager = Manager()


@TimeChecker.call_within_timeframe(*PARS_TIMEFRAME)
async def gat_compares(data):
    logger.info(f'Start parsing')
    item_list = await pars.get_items(data)
    items_obj_dict = get_items_obj_dict(item_list, ItemMakeup)
    logger.info(f'Get {len(items_obj_dict)} items')
    compare = CompareItemToHistory(items_obj_dict, simple_strategy)
    compare_set = set(comp for comp in compare if comp > DELTA_LIMIT_PERCENT)
    logger.info(f'Get {len(compare)} compares')
    manager.add_comparison(compare_set)
    logger.info(f'\n --- Get base_compare: {len(manager.base_compare)}'
                f'\n --- Get new_compare: {len(manager.new_compare)}'
                f'\n --- got difference: {len(manager.difference)}')
    try:
        add_to_history(compare)
    except OtherTimeError:
        pass
    return sorted(list(manager.difference), reverse=True)


@TimeChecker.call_after_delta(**ADD_TO_HISTORY_AFTER)
def add_to_history(compare):
    compare.add_to_history()
    logger.info(f'add {len(compare)} to history')


def send_massage(data):
    print(f'send masage {data}')


@TimeChecker.call_after_delta(**PARS_AFTER)
async def run():
    for pars_data in PARS_DEFAULT:
        try:
            res = await gat_compares(pars.Settings(**pars_data))
            send_massage(res)
        except CallAfterTimedeltaError:
            continue


async def main():
    while True:
        try:
            await run()
        except OtherTimeError:
            continue


if __name__ == '__main__':
    asyncio.run(main())
