# -*- coding: utf-8 -*-
import os
import sys
import requests
from handlers import SnoothError, http_error_handler, snooth_error_handler

try:
    API_KEY = os.environ['API_KEY']
except KeyError:
    API_KEY = None
    sys.stderr.write('Please set os.environ["API_KEY"] = yourapikey, '
                     'or pass api_key param in SnoothClient')


class SnoothBase(object):

    def properties(self):
        property_dict = {
            field: value for (field, value) in vars(self).iteritems()
        }
        return property_dict

    def fields(self):
        field_list = [
            field for field in vars(self).iterkeys()
        ]
        return field_list

    def values(self):
        value_list = [
            value for value in vars(self).itervalues()
        ]
        return value_list

    def _set_credentials(self, username, password):
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        return username, password


class SnoothClient(SnoothBase):
    WINE_SEARCH_URL = 'https://api.snooth.com/wines/'
    WINE_DETAIL_URL = 'https://api.snooth.com/wine/'
    MY_WINES_URL = 'https://api.snooth.com/my-wines/'
    WINERY_DETAIL_URL = 'https://api.snooth.com/winery/'
    RATE_WINE_URL = 'https://api.snooth.com/rate/'
    WISHLIST_WINE_URL = 'https://api.snooth.com/wishlist/'
    STORE_SEARCH_URL = 'https://api.snooth.com/stores/'
    STORE_DETAIL_URL = 'https://api.snooth.com/store'
    CREATE_ACCOUNT_URL = 'https://api.snooth.com/create-account/'
    USER_ACTIVITY_URL = 'https://api.snooth.com/action/'

    def __init__(self, api_key=API_KEY, format='json', ip=None,
                 username=None, password=None, timeout=None):
        self.api_key = API_KEY
        self.format = format
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout

    def basic_params(self):
        params = {
            'akey': self.api_key,
            'format': self.format,
            'ip': self.ip,
            'u': self.username,
            'p': self.password,
        }
        return params

    def wine_search(self, q='wine', wineify=False, count=10, page=1,
                    first_result=None, available=False, prod_type=None,
                    color=None, store_id=None, country=None,
                    zipcode=None, lat=None, lng=None, sort=None,
                    min_price=None, max_price=None, min_rank=None,
                    max_rank=None, lang=None, timeout=None):
        timeout = self._set_timeout(timeout)
        bools = self._translate_bool(available)
        first_result = self._paginator(count, page, first_result)
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        new_params = {
            'q': q,
            'f': first_result,
            'n': count,
            'a': bools[0],
            't': prod_type,
            'color': color,
            'm': store_id,
            'c': country,
            'z': zipcode,
            'lat': lat,
            'lng': lng,
            's': sort,
            'mp': min_price,
            'xp': max_price,
            'mr': min_rank,
            'xr': max_rank,
            'lang': lang
        }
        params.update(new_params)
        response = self.get(self.WINE_SEARCH_URL, params, timeout=timeout)
        python_response = self.parse_get_response(response)
        output = self.wine_output(python_response)
        if output and wineify is True:
            output = self.wineify(output)
        return output

    def wine_detail(self, wine_id, price=False, country=None, zipcode=None,
                    pairings=False, photos=False, lat=None, lng=None,
                    language=None, timeout=None):
        timeout = self._set_timeout(timeout)
        bools = self._translate_bool(price, pairings, photos)
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        new_params = {
            'id': wine_id,
            'i': bools[0],
            'c': country,
            'z': zipcode,
            'food': bools[1],
            'photos': bools[2],
            'lat': lat,
            'lng': lng,
            'lang': language
        }
        params.update(new_params)
        response = self.get(self.WINE_DETAIL_URL, params, timeout)
        python_response = self.parse_get_response(response)
        try:
            output = python_response['wines']
        except KeyError:
            raise SnoothError('Unknown error has occured.')
        return output

    def my_wines(self, username=None, password=None, count=10, page=1,
                 ratings=True, wishlist=True, cellar=True, timeout=None):
        timeout = self._set_timeout(timeout)
        bools = self._translate_bool(ratings, wishlist, cellar)
        username, password = self._set_credentials(username, password)
        params = self.basic_params()
        new_params = {
            'username': username,
            'password': password,
            'n': count,
            'pg': page,
            'r': bools[0],
            'w': bools[1],
            'c': bools[2]
        }
        params.update(new_params)
        response = self.get(self.MY_WINES_URL, params, timeout)
        python_response = self.parse_get_response(response)
        output = self.wine_output(python_response)
        return output

    def wineify(self, output, username=None, password=None):
        username, password = self._set_credentials(username, password)
        wines = [
            Wine(
                wine,
                username=username,
                password=password
            )
            for wine in output
        ]
        return wines

    def winery_detail(self, winery_id, timeout=None):
        timeout = self._set_timeout(timeout)
        params = self.basic_params()
        new_params = {'id': winery_id}
        params.update(new_params)
        response = self.get(self.WINERY_DETAIL_URL, params, timeout)
        python_response = self.parse_get_response(response)
        try:
            output = python_response['winery']
        except KeyError:
            raise SnoothError('Unknown error has occured.')
        return output

    def rate_wine(self, wine_id, method='POST', username=None,
                  password=None, rating=None, review=None,
                  private=False, tags=None, wishlist=False,
                  cellar_count=None, timeout=None):
        timeout = self._set_timeout(timeout)
        username, password = self._set_credentials(username, password)
        bools = self._translate_bool(private, wishlist)
        params = self.basic_params()
        new_params = {
            'id': wine_id,
            'u': username,
            'p': password,
            'r': rating,
            'b': review,
            'v': bools[0],
            't': tags,
            'w': bools[1],
            'c': cellar_count,
        }
        params.update(new_params)
        if method == 'POST':
            response = self.post(self.RATE_WINE_URL, params, timeout)
        elif method == 'PUT':
            response = self.put(self.RATE_WINE_URL, params, timeout)
        else:
            raise SnoothError('Please use method="POST" to create a new '
                              'review or method="PUT" to update a review.')
        python_response = self.parse_post_response(response)
        return python_response

    def wishlist(self, wine_id, username=None, password=None, timeout=None):
        """Currently just adds to wine list"""
        timeout = self._set_timeout(timeout)
        username, password = self._set_credentials(username, password)
        params = self.basic_params()
        new_params = {
            'id': wine_id,
            'username': username,
            'password': password
        }
        params.update(new_params)
        response = self.post(self.WISHLIST_WINE_URL, params, timeout)
        python_response = self.parse_post_response(response)
        return python_response

    def store_search(self, country=None, zipcode=None,
                     lat=None, lng=None, timeout=None):
        timeout = self._set_timeout(timeout)
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        new_params = {'c': country, 'z': zipcode, 'lat': lat, 'lng': lng}
        params.update(new_params)
        response = self.get(self.STORE_SEARCH_URL, params, timeout)
        python_response = self.parse_get_response(response)
        if 'stores' in python_response:
            output = python_response['stores']
        else:
            output = None
        return output

    def store_detail(self, store_id, reviews=True, timeout=None):
        timeout = self._set_timeout(timeout)
        bools = self._translate_bool(reviews)
        params = self.basic_params()
        new_params = {'id': store_id, 'reviews': bools[0]}
        params.update(new_params)
        response = self.get(self.STORE_DETAIL_URL, params, timeout)
        python_response = self.parse_get_response(response)
        try:
            output = python_response['store']
        except KeyError:
            raise SnoothError('Unknown error has occured.')
        return output

    def create_account(self, email=None, screen_name=None,
                       password=None, timeout=None):
        timeout = self._set_timeout(timeout)
        params = {
            'akey': self.api_key,
            'format': self.format,
            'ip': self.ip,
            'e': email,
            's': screen_name,
            'p': password
        }
        response = self.post(self.CREATE_ACCOUNT_URL, params, timeout)
        python_response = self.parse_post_response(response)
        return python_response

    def user_activity(self, activity_type=None, before_date='now', count=50,
                      page=1, first_result=1, timeout=None):
        timeout = self._set_timeout(timeout)
        first_result = self._paginator(count, page, first_result)
        params = {
            'akey': self.api_key,
            'format': self.format,
            'ip': self.ip,
            'b': before_date,
            'f': first_result,
            'n': count,
        }
        response = self.get(self.USER_ACTIVITY_URL, params, timeout)
        python_response = self.parse_get_response(response)
        try:
            output = python_response['actions']
        except KeyError:
            raise SnoothClient('Unkown error has occured.')
        return output

    @http_error_handler
    def get(self, url, params, timeout):
        response = requests.get(
            url,
            params=params,
            verify=True,
            timeout=timeout
        )
        return response

    @http_error_handler
    def post(self, url, params, timeout):
        response = requests.post(
            url,
            params=params,
            verify=True,
            timeout=timeout
        )
        return response

    @http_error_handler
    def put(self, url, params, timeout):
        response = requests.put(
            url,
            params=params,
            verify=True,
            timeout=timeout
        )
        return response

    @snooth_error_handler(post='')
    def parse_get_response(self, response):
        return response.json()

    @snooth_error_handler(post='POST')
    def parse_post_response(self, response):
        return response.json()

    def wine_output(self, python_response):
        if 'wines' in python_response:
            output = python_response['wines']
        else:
            output = None
        return output

    def _translate_bool(self, *args):
        results = []
        for arg in args:
            if arg is False:
                arg = 0
            else:
                arg = 1
            results.append(arg)
        return results

    def _paginator(self, count, page, first_result):
        if first_result is None:
            first_result = page * count + 1
        return first_result

    def _set_credentials(self, username, password):
        if not username:
            username = self.username
        if not password:
            password = self.password
        return username, password

    def _set_timeout(self, timeout):
        if not timeout:
            timeout = self.timeout
        return timeout

    def _check_lat_lng(self, lat, lng):
        if lat and not lng or lng and not lat:
            raise SnoothError('Must pass both lat and lng')


class Wine(SnoothBase):

    def __init__(self, wine, username=None, password=None):
        self.username = username
        self.password = password
        self.code = wine.get('code', '')
        self.name = wine.get('name', '')
        self.winery = wine.get('winery', '')
        self.winery_id = wine.get('winery_id', '')
        self.vintage = wine.get('vintage', '')
        self.region = wine.get('region', '')
        self.varietal = wine.get('varietal', '')
        self.type = wine.get('type', '')
        self.link = wine.get('link', '')
        self.image = wine.get('image', '')
        self.num_merchants = wine.get('num_merchants', '')
        self.price = wine.get('price', '')
        self.num_reviews = wine.get('num_reviews', '')
        self.tags = wine.get('tags', '')
        self.snoothrank = wine.get('snoothrank', '')
        if wine.get('available', '') == 1:
            self.available = True
        else:
            self.available = False

    def detail(self, price=False, country=None, zipcode=None,
               pairings=False, photos=False, lat=None, lng=None,
               language=None, timeout=None):
        snooth = SnoothClient(timeout=timeout)
        response = snooth.wine_detail(
            wine_id=self.code,
            price=price,
            country=country,
            zipcode=zipcode,
            pairings=pairings,
            photos=photos,
            lat=lat,
            lng=lng,
            language=language,
        )
        return response

    def rate(self, method='POST', username=None, password=None,
             rating=None, review=None, private=False, tags=None,
             wishlist=False, cellar_count=None, timeout=None):
        username, password = self._set_credentials(username, password)
        snooth = SnoothClient(
            username=username,
            username=password,
            timeout=timeout
        )
        response = snooth.wine_rate(
            wine_id=self.code,
            method=method,
            rating=rating,
            review=review,
            private=private,
            tags=tags,
            wishlist=wishlist,
            cellar_count=cellar_count,
        )
        return response

    def list(self, username=None, password=None, timeout=None):
        username, password = self._set_credentials(username, password)
        snooth = SnoothClient(
            username=username,
            password=password,
            timeout=timeout
        )
        response = snooth.wishlist(wine_id=self.code)
        return response


class WineStore(SnoothBase):
    pass


class Winery(SnoothBase):
    pass
