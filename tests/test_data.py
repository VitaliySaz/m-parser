import unittest
from typing import List

from data import ItemBase, ItemMakeup, ItemMakeupHistory, CompareMakeupPrices


class TestItemBase(unittest.TestCase):

    def test_item_base_repr(self):
        item = ItemBase(item_id="12345", price=10.0)
        self.assertEqual(repr(item), "<ItemBase: 12345, 10.0>")

    def test_item_base_str(self):
        item = ItemBase(item_id="12345", price=10.0)
        self.assertEqual(str(item), "12345")

    def test_item_base_eq(self):
        item1 = ItemBase(item_id="12345", price=10.0)
        item2 = ItemBase(item_id="12345", price=15.0)
        item3 = ItemBase(item_id="67890", price=10.0)
        self.assertTrue(item1 == item2)
        self.assertFalse(item1 == item3)

    def test_item_base_lt(self):
        item1 = ItemBase(item_id="12345", price=10.0)
        item2 = ItemBase(item_id="67890", price=15.0)
        self.assertTrue(item1 < item2)
        self.assertFalse(item2 < item1)

    def test_item_base_gt(self):
        item1 = ItemBase(item_id="12345", price=10.0)
        item2 = ItemBase(item_id="67890", price=15.0)
        self.assertTrue(item2 > item1)
        self.assertFalse(item1 > item2)

    def test_item_base_hash(self):
        item = ItemBase(item_id="12345", price=10.0)
        self.assertEqual(hash(item), hash("12345"))


class TestItemMakeup(unittest.TestCase):

    def setUp(self) -> None:
        self.item1 = ItemMakeup(item_id="12345_67890", price=10.0, product_id="12345", value="67890")
        self.item2 = ItemMakeup(item_id="12345", price=15.0, product_id="12345", value="67890")

    def test_item_makeup_is_eu(self):
        self.assertTrue(self.item1.is_eu)
        self.assertFalse(self.item2.is_eu)

    def test_item_makeup_id_ua(self):
        self.assertEqual(self.item1.id_ua, "12345")

    def test_item_makeup_id_eu(self):
        self.assertEqual(self.item1.id_eu, "12345_67890")
        self.assertEqual(self.item2.id_eu, "12345_3")

    def test_item_makeup_hash(self):
        item = ItemMakeup(item_id="12345_67890", price=10.0, product_id="12345", value="67890")
        self.assertEqual(hash(item), hash("12345_67890"))


class TestItemMakeupHistory(unittest.TestCase):

    def test_item_makeup_history_middle_price(self):
        item = ItemMakeupHistory(item_id="12345", price=10.0)
        self.assertEqual(item.middle_price, 10.0)

    def test_item_makeup_hash(self):
        item = ItemMakeupHistory(item_id="12345", price=10.0)
        self.assertEqual(hash(item), hash("12345"))


class TestCompareMakeupPrices(unittest.TestCase):

    def setUp(self) -> None:
        self.item1 = ItemMakeup(item_id="111", price=10.0, product_id="1111", value="Value 1")
        self.item2 = ItemMakeup(item_id="222", price=20.0, product_id="2222", value="Value 2")
        self.item3 = ItemMakeup(item_id="333", price=30.0, product_id="3333", value="Value 3")

    def test_compare_makeup_prices(self):
        compare1 = CompareMakeupPrices(item=self.item1, compare=self.item2)
        self.assertAlmostEqual(compare1.price_delta, -50.0, delta=0.001)
        self.assertLess(compare1, 0)
        self.assertGreater(compare1, -100)
        self.assertEqual(str(compare1), "https://makeup.com.ua/ua/product/1111/\n | Value 1 : 10.0 | -50.0")

        compare2 = CompareMakeupPrices(item=self.item3, compare=self.item2)
        self.assertAlmostEqual(compare2.price_delta, 50.0, delta=0.001)
        self.assertGreater(compare2, 0)
        self.assertLess(compare2, 100)
        self.assertEqual(str(compare2), "https://makeup.com.ua/ua/product/3333/\n | Value 3 : 30.0 | 50.0")
