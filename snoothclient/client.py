# -*- coding: utf-8 -*-
import requests
from api_key import API_KEY
from errors import SnoothException
from handlers import (
    wine_search_handler, wine_search_client_handler, store_search_handler,
    store_search_client_handler
)
from utils import wineify


class SnoothClient(object):
    WINE_SEARCH_URL = 'https://api.snooth.com/wines/'
    STORE_SEARCH_URL = 'https://api.snooth.com/stores/'

    def __init__(self, api_key=API_KEY, format='json', ip=None,
                 username=None, password=None, timeout=None):
        self.api_key = API_KEY
        self.format = format
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout

    def wine_search(self, q='wine', wineify=False, count=10, page=1,
                    first_result=None, available=1, prod_type=None,
                    color=None, store_id=None, country=None,
                    zipcode=None, lat=None, lng=None, sort=None,
                    min_price=None, max_price=None, min_rank=None,
                    max_rank=None, lang=None, timeout=None):
        if lat and not lng or lng and not lat:
            raise SnoothException('Must pass both lat and lng')
        if timeout is None:
            timeout = self.timeout
        if first_result is None:
            first_result = page * count + 1
        query = {
            'akey': self.api_key, 'format': self.format, 'ip': self.ip,
            'u': self.username, 'p': self.password, 'q': q, 'f': first_result,
            'n': count, 'a': available, 't': prod_type, 'color': color,
            'm': store_id, 'c': country, 'z': zipcode, 'lat': lat, 'lng': lng,
            's': sort, 'mp': min_price, 'xp': max_price, 'mr': min_rank,
            'xr': max_rank, 'lang': lang
        }
        response = self.get_wine_search(query, timeout=timeout)
        python_response = self.parse_wine_search(response)
        if wineify is True:
            python_response = self._wineify_wine_search(response)
        return python_response

    @wine_search_handler
    def get_wine_search(self, query, timeout):
        response = requests.get(
            self.WINE_SEARCH_URL,
            params=query,
            verify=True,
            timeout=timeout
        )
        return response

    @wine_search_client_handler
    def parse_wine_search(self, response):
        return response.json()

    def _wineify_wine_search(self, python_response):
        wines = python_response['wines']
        return wineify(wines)

    def store_search(self, country=None, zipcode=None,
                     lat=None, lng=None, timeout=None):
        if timeout is None:
            timeout = self.timeout
        if lat and not lng or lng and not lat:
            raise SnoothException('Must pass both lat and lng')
        query = {
            'akey': self.api_key, 'format': self.format, 'ip': self.ip,
            'u': self.username, 'p': self.password, 'c': country,
            'z': zipcode, 'lat': lat, 'lng': lng
        }
        response = self.get_store_search(query, timeout)
        python_response = self.parse_store_search(response)
        return python_response

    @store_search_handler
    def get_store_search(self, query, timeout):
        response = requests.get(
            self.STORE_SEARCH_URL,
            params=query,
            verify=True,
            timeout=timeout
        )
        return response

    @store_search_client_handler
    def parse_store_search(self, response):
        return response.json()
