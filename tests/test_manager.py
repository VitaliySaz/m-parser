import unittest

from compare import CompareItemToHistory, ua_eu_strategy
from data import ItemMakeup
from manager import Manager


class TestManager(unittest.TestCase):

    def test(self):
        compare = Manager()
        compare.add_comparison({1, 2, 3})
        self.assertEqual(compare.difference, {1, 2, 3})
        compare.add_comparison(set())
        self.assertFalse(compare.difference)
        compare.add_comparison({1, 2, 3})
        self.assertFalse(compare.difference)
        compare.add_comparison({1, 2, 3, 4, 5})
        self.assertEqual(compare.difference, {4, 5})

