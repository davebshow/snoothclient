# -*- coding: utf-8 -*-
import os
import sys
import unittest
from requests import Timeout
from client import SnoothClient, Wine
try:
    API_KEY = os.environ['API_KEY']
except KeyError:
    API_KEY = None

    sys.stderr.write('Please set os.environ["API_KEY"] = yourapikey, '
                     'or pass api_key param in SnoothClient')


class SnoothTests(unittest.TestCase):

    def setUp(self):
        self.snooth = SnoothClient(api_key=API_KEY)

    def test_wine_search(self):
        response = self.snooth.wine_search()
        self.assertTrue(len(response) > 0)
        for wine in response:
            self.assertTrue(isinstance(wine, dict))

    def test_wine_search_meta(self):
        response = self.snooth.wine_search(meta=True)
        self.assertTrue('meta' in response)

    def test_wine_search_wineify(self):
        response = self.snooth.wine_search(wineify=True)
        self.assertTrue(len(response) > 0)
        for wine in response:
            self.assertTrue(isinstance(wine, Wine))

    def test_wine_search_count(self):
        response = self.snooth.wine_search(count=20)
        self.assertEqual(len(response), 20)

    def test_wine_search_timeout(self):
        self.assertRaises(
            Timeout,
            self.snooth.wine_search,
            timeout=0.0000000000000000001
        )

    def test_wine_detail(self):
        response = self.snooth.wine_detail(
            'chateau-recougne-red-bordeaux-blend-bordeaux-superieur-2009-4'
        )
        self.assertTrue(len(response) == 1)

    def test_wine_detail_timeout(self):
        self.assertRaises(
            Timeout,
            self.snooth.wine_detail,
            'chateau-recougne-red-bordeaux-blend-bordeaux-superieur-2009-4',
            timeout=0.0000000000000000001
        )

if __name__ == '__main__':
    unittest.main()
