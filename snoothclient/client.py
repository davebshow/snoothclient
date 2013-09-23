# -*- coding: utf-8 -*-
import requests
from api_key import API_KEY
from handlers import (
    SnoothException, wine_search_handler, wine_search_client_handler
)
from utils import wineify


class SnoothClient(object):
    WINE_SEARCH_URL = 'https://api.snooth.com/wines/'

    def __init__(self, api_key=API_KEY, format='json', ip=None,
                 username=None, password=None, timeout=None):
        self.api_key = API_KEY
        self.format = format
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout

    def wine_search(self, q='wine', first_result=1, count=10, available=0,
                    prod_type=None, color=None, store_id=None, country=None,
                    zipcode=None, lat=None, lng=None, sort=None,
                    min_price=None, max_price=None, min_rank=None,
                    max_rank=None, lang=None, timeout=None):
        if timeout is None:
            timeout = self.timeout
        if lat and not lng or lng and not lat:
            raise SnoothException('Must pass both lat and lng')
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
        return self._wineify_wine_search(python_response)

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


# u'minimum price (mp) is not numeric'
# u'maximum price (xp) is not numeric'
# u'no longitude included' # 'why doesn't this happen with lng param?
# s.wine_search(max/min_rank='asdfsadf') == 500 internal server
# s.wine_search(min_rank=10000000000000000000000000000000000) == 500
