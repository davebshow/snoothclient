# -*- coding: utf-8 -*-
import os
import sys
import unittest
from client import SnoothClient

try:
    API_KEY = os.environ['API_KEY']
except KeyError:
    API_KEY = None
    sys.stderr.write('Please set os.environ["API_KEY"] = yourapikey, '
                     'or pass api_key param in SnoothClient')


class SnoothTests(unittest.TestCase):

    def setUp(self):
        self.snooth = SnoothClient(api_key=API_KEY)

    def test_api_urls(self):
        self.assertEqual(self.WINE_SEARCH_URL, 'http://api.snooth.com/wines/')
        self.assertEqual(
            self.CREATE_ACCOUNT_URL,
            'http://api.snooth.com/create-account/'
        )
        self.assertEqual(
            self.STORE_SEARCH_URL,
            'http://api.snooth.com/stores/'
        )
