import os

DELTA_LIMIT_PERCENT = 20

PARS_DATA = os.getenv('PARS_DATA') or [
    {'page_count': 10, 'category_id': 3}
]

# Time management
PARS_TIMEFRAME = os.getenv('PARS_TIMEFRAME') or ((9, 0), (23, 0))
ADD_TO_HISTORY_AFTER = {'seconds': 20}
PARS_AFTER = {'seconds': 5}

# compare
COMPARE = 'CompareItemToHistory'
COMPARE_STRATEGY = 'simple_strategy'
