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

    def test_wine_search(self):
        response = self.snooth.wine_search()
        self.asserTrue(len(response > 0))
        for wine in response:
            self.assertTrue(isinstance(wine, dict))
