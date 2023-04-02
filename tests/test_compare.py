import unittest
from unittest import mock
from statistics import mean
from typing import Dict, Generator

from data import ItemMakeup, ItemMakeupHistory, CompareMakeupPrices
from compare import CompareManagerHistory, ua_eu_strategy, CompareManagerItem, simple_strategy


class TestCompareManagerHistory(unittest.TestCase):

    def setUp(self) -> None:
        self.item1 = ItemMakeup(item_id='1', price=100, product_id='12345', value='1')
        self.item2 = ItemMakeup(item_id='2', price=200, product_id='12345', value='2')
        self.item3 = ItemMakeup(item_id='3_3', price=300, product_id='1234567', value='3')
        self.dict_item = {'1': self.item1, '2': self.item2, '3_3': self.item3}
        self.manager = CompareManagerHistory(self.dict_item)

    def test_empty_dict_item(self):
        manager = CompareManagerHistory({})
        res = list(manager.to_compare(ua_eu_strategy))
        self.assertEqual(len(res), 0)

    @mock.patch('compare.DbManagerBase.get_prices_dict')
    def test_get_compare_ua_eu_strategy(self, mock_get_prices_dict):
        mock_get_prices_dict.return_value = {
            '2': [(1679776380.949, 150), (1679776380.949, 200)],
            '3': [(1679776380.949, 500)]
        }
        res = list(self.manager.to_compare(ua_eu_strategy))
        self.assertEqual(repr(res), '[<CompareMakeupPrices: 3_3, 3, -40.0>]')
        # self.assertEqual(res.price_delta, -40)

    @mock.patch('compare.DbManagerBase.get_prices_dict')
    def test_get_compare_simple_strategy(self, mock_get_prices_dict):
        mock_get_prices_dict.return_value = {
            '2': [(1679776380.949, 300), (1679776380.949, 500)],
            '3': [(1679776380.949, 500)]
        }
        res = list(self.manager.to_compare(simple_strategy))
        self.assertEqual(repr(res), '[<CompareMakeupPrices: 2, 2, -50.0>]')

    @mock.patch('compare.DbManagerBase.get_prices_dict')
    def test_get_compare_empty_dict(self, mock_get_prices_dict):
        mock_get_prices_dict.return_value = {}
        res = list(self.manager.to_compare(ua_eu_strategy))
        self.assertEqual(len(res), 0)


class TestCompareManagerItem(unittest.TestCase):

    def setUp(self):
        self.item1 = ItemMakeup(item_id='1', price=100, product_id='12345', value='1')
        self.item2 = ItemMakeup(item_id='2', price=200, product_id='12345', value='2')
        self.item21 = ItemMakeup(item_id='3_3', price=200, product_id='12345', value='2')
        self.dict_item = {'1': self.item1, '2': self.item2, '3_3': self.item21}
        self.item3 = ItemMakeup(item_id='1', price=200, product_id='12345', value='1')
        self.item4 = ItemMakeup(item_id='2', price=300, product_id='12345', value='2')
        self.item41 = ItemMakeup(item_id='3', price=300, product_id='12345', value='2')
        self.dict_item2 = {'1': self.item3, '2': self.item4, '3': self.item41}

    def test_empty_dict_item(self):
        manager = CompareManagerItem({}, {})
        res = list(manager.to_compare(ua_eu_strategy))
        self.assertEqual(len(res), 0)

    def test_get_compare_simple_strategy(self):
        self.manager = CompareManagerItem(self.dict_item, self.dict_item2)
        res = list(self.manager.to_compare(simple_strategy))
        self.assertEqual(len(res), 2)
        self.assertEqual(
            repr(res), '[<CompareMakeupPrices: 1, 1, -50.0>, <CompareMakeupPrices: 2, 2, -33.33333333333333>]')

    def test_get_compare_ua_eu_strategy(self):
        self.manager = CompareManagerItem(self.dict_item, self.dict_item2)
        self.manager2 = CompareManagerItem(self.dict_item2, self.dict_item)
        res = list(self.manager.to_compare(ua_eu_strategy))
        res2 = list(self.manager2.to_compare(ua_eu_strategy))
        self.assertEqual(len(res), 1)
        self.assertEqual(
            repr(res), '[<CompareMakeupPrices: 3_3, 3, -33.33333333333333>]')
        self.assertEqual(len(res2), 0)


