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


class SnoothClient(object):

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
        params = {'akey': self.api_key, 'format': self.format, 'ip': self.ip,
                  'u': self.username, 'p': self.password}
        return params

    def wine_search(self, q='wine', wineify=False, count=10, page=1,
                    first_result=None, available=False, prod_type=None,
                    color=None, store_id=None, country=None,
                    zipcode=None, lat=None, lng=None, sort=None,
                    min_price=None, max_price=None, min_rank=None,
                    max_rank=None, lang=None, timeout=None):
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        bools = self._translate_bool(available)
        first_result = self._paginator(count, page, first_result)
        timeout = self._get_timeout(timeout)
        new_params = {'q': q, 'f': first_result, 'n': count, 'a': bools[0],
                      't': prod_type, 'color': color, 'm': store_id,
                      'c': country, 'z': zipcode, 'lat': lat, 'lng': lng,
                      's': sort, 'mp': min_price, 'xp': max_price,
                      'mr': min_rank, 'xr': max_rank, 'lang': lang}
        params.update(new_params)
        response = self.get(self.WINE_SEARCH_URL, params, timeout=timeout)
        python_response = self.parse_get_response(response)
        output = self._wine_output(python_response)
        if output and wineify is True:
            output = self.wineify(output)
        return output

    def wine_detail(self, wine_id, price=False, country=None, zipcode=None,
                    pairings=False, photos=False, lat=None, lng=None,
                    language=None, timeout=None):
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        bools = self._translate_bool(price, pairings, photos)
        timeout = self._get_timeout(timeout)
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
        params = self.basic_params()
        username, password = self._get_credentials(username, password)
        bools = self._translate_bool(ratings, wishlist, cellar)
        timeout = self._get_timeout(timeout)
        new_params = {
            'u': username,
            'p': password,
            'n': count,
            'pg': page,
            'r': bools[0],
            'w': bools[1],
            'c': bools[2]
        }
        params.update(new_params)
        response = self.get(self.MY_WINES_URL, params, timeout)
        python_response = self.parse_get_response(response)
        output = self._wine_output(python_response)
        return output

    def wineify(self, output, username=None, password=None):
        username, password = self._get_credentials(username, password)
        wines = [
            Wine(wine, username=username,
                 password=password) for wine in output
        ]
        return wines

    def winery_detail(self, winery_id, timeout=None):
        params = self.basic_params()
        timeout = self._get_timeout(timeout)
        new_params = {'id': winery_id}
        params.update(new_params)
        response = self.get(self.WINERY_DETAIL_URL, params, timeout)
        python_response = self.parse_get_response(response)
        try:
            output = python_response['winery']
        except KeyError:
            raise SnoothError('Unknown error has occured.')
        return output

    def rate_wine(self, wine_id, method='POST', username=None, password=None,
                  rating=None, review=None, private=False, tags=None,
                  wishlist=False, cellar_count=None, timeout=None):
        params = self.basic_params()
        username, password = self._get_credentials(username, password)
        bools = self._translate_bool(private, wishlist)
        timeout = self._get_timeout(timeout)
        new_params = {
            'id': wine_id,
            'u': username,
            'p': password,
            'r': rating,
            'b': review,
            'v': bools[0],
            't': tags,
            'w': bools[1],
            'c': cellar_count
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
        params = self.basic_params()
        username, password = self._get_credentials(username, password)
        timeout = self._get_timeout(timeout)
        new_params = {
            'id': wine_id,
            'u': username,
            'p': password
        }
        params.update(new_params)
        response = self.post(self.WISHLIST_WINE_URL, params, timeout)
        python_response = self.parse_post_response(response)
        return python_response

    def store_search(self, country=None, zipcode=None,
                     lat=None, lng=None, timeout=None):
        self._check_lat_lng(lat, lng)
        params = self.basic_params()
        timeout = self._get_timeout(timeout)
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
        params = self.basic_params()
        bools = self._translate_bool(reviews)
        timeout = self._get_timeout(timeout)
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
        timeout = self._get_timeout(timeout)
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
        first_result = self._paginator(count, page, first_result)
        timeout = self._get_timeout(timeout)
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

    def _wine_output(self, python_response):
        if 'wines' in python_response:
            output = python_response['wines']
        else:
            output = None
        return output

    def _paginator(self, count, page, first_result):
        if first_result is None:
            first_result = page * count + 1
        return first_result

    def _get_credentials(self, username, password):
        if not username:
            username = self.username
        if not password:
            password = self.password
        return username, password

    def _get_timeout(self, timeout):
        if not timeout:
            timeout = self.timeout
        return timeout

    def _check_lat_lng(self, lat, lng):
        if lat and not lng or lng and not lat:
            raise SnoothError('Must pass both lat and lng')

    def _translate_bool(self, *args):
        results = []
        for arg in args:
            if arg is False:
                arg = 0
            else:
                arg = 1
            results.append(arg)
        return results


class SnoothBaseObject(object):

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


class Wine(SnoothBaseObject):

    def __init__(self, wine, username=None, password=None):
        self.username = username
        self.password = password
        self.name = wine.get('name', '')
        self.code = wine.get('code', '')
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
        snooth = SnoothClient()
        bools = snooth._translate_bool(price, pairings, photos)
        response = snooth.wine_detail(
            wine_id=self.code,
            price=bools[0],
            country=country,
            zipcode=zipcode,
            pairings=bools[1],
            photos=bools[2],
            lat=lat,
            lng=lng,
            language=language,
            timeout=timeout
        )
        return response

    def rate(self, method='POST', username=None, password=None,
             rating=None, review=None, private=False, tags=None,
             wishlist=False, cellar_count=None, timeout=None):
        snooth = SnoothClient()
        username, password = snooth._get_credentials(username, password)
        bools = snooth._translate_bool(private, wishlist)
        response = snooth.wine_rate(
            username=username,
            password=password,
            wine_id=self.code,
            method=method,
            rating=rating,
            review=review,
            private=bools[0],
            tags=tags,
            wishlist=bools[1],
            cellar_count=cellar_count,
            timeout=timeout
        )
        return response

    def list(self, username=None, password=None, timeout=None):
        snooth = SnoothClient()
        username, password = self._get_credentials(username, password)
        response = snooth.wishlist(
            self.code,
            username=username,
            password=password,
            timeout=timeout
        )
        return response


class SnoothVendorBase(SnoothBaseObject):

    def __init__(self, vendor):
        self.name = vendor.get('name', '')
        self.address = vendor.get('address', '')
        self.city = vendor.get('city', '')
        self.state = vendor.get('state', '')
        self.country = vendor.get('country', '')
        self.id = vendor.get('id', '')
        self.email = vendor.get('email', '')
        self.url = vendor.get('url', '')
        self.phone = vendor.get('phone', '')
        self.num_wines = vendor.get('num_wines', '')
        if vendor.get('closed') == 1:
            self.closed = True
        else:
            self.closed = False


class WineStore(SnoothVendorBase):

    def __init__(self, store):
        super(WineStore, self).__init__(store)
        self.lat = store.get('lat', '')
        self.lng = store.get('lng', '')
        self.type = store.get('type', '')
        self.url_code = store.get('url_code', '')
        self.num_ratings = store.get('num_ratings', '')
        self.rating = store.get('rating', '')

    def detail(self, reviews=True, timeout=None):
        snooth = SnoothClient()
        bools = snooth._translate_bool(reviews)
        response = snooth.store_detail(
            self.id,
            reviews=bools[0],
            timeout=timeout
        )
        return response


class Winery(SnoothVendorBase):

    def __init__(self, winery):
        super(Winery, self).__init__(winery)
        self.zip = winery.get('zip', '')
        self.image = winery.get('image', '')
