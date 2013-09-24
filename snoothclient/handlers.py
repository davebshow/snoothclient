# -*- coding: utf-8 -*-
import logging
from errors import (
    SnoothError, SnoothHTTPError, SnoothTypeError, SnoothValueError
)


def http_error_handler(fn):
    def http_response_wrapper(self, *args, **kwargs):
        response = fn(self, *args, **kwargs)
        if response.status_code != 200:
            if response.status_code == 500:
                raise SnoothHTTPError('500 Bad query params')
            response.raise_for_status()
        return response
    return http_response_wrapper


def snooth_error_handler(fn):
    def snooth_response_wrapper(self, *args, **kwargs):
        snooth_response = fn(self, *args, **kwargs)
        meta = snooth_response['meta']
        errmsg = meta['errmsg'].decode('utf-8')
        if errmsg:
            if errmsg == 'minimum price (mp) is not numeric' or \
                    errmsg == 'maximum price (xp) is not numeric':
                raise SnoothTypeError('Max/min price should be numeric')
            elif errmsg == 'authentication key is wrong':
                raise SnoothValueError('Bad API key')
            elif errmsg == 'invalid location identifier.':
                msg = ('Bad location identifier. Both country and zipcode or '
                       'lat, lng are required. Countries are formatted as 2 '
                       'letter codes.')
                raise SnoothValueError(msg)
            raise SnoothError('Client Error')
        if meta['results'] == 0:
            logging.warning('No matches, check query')
        return snooth_response
    return snooth_response_wrapper
