import json
import os

PARS_DATA = [
    {
        'PARS':
            {
                'page_count': 10, 'category_id': 3
            },
        'DELTA_LIMIT': 5
    }
]

DB_NAME = 'prices'

# Time management
PARS_TIMEFRAME = ((9, 0), (23, 0))
ADD_TO_HISTORY_AFTER = {'seconds': 20}
PARS_AFTER = {'seconds': 1}

# compare
COMPARE = 'CompareItemToHistory'
COMPARE_STRATEGY = 'simple_strategy'

TELEGRAM = {
    'TOKEN': os.getenv('TOKEN') or input('Set telegram token: '),
    'CHAT_ID': os.getenv('CHAT_ID') or input('Set telegram chat id: ')
}

if not os.path.exists(DB_NAME):
    os.makedirs(DB_NAME)
