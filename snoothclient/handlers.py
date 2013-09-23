# -*- coding: utf-8 -*-
import logging
from errors import (
    SnoothException, SnoothHTTPError, SnoothTypeError, SnoothValueError
)


def wine_search_handler(fn):
    def wine_search_response_wrapper(self, *args, **kwargs):
        response = fn(self, *args, **kwargs)
        if response.status_code != 200:
            if response.status_code == 500:
                raise SnoothHTTPError('500 Bad query params')
            response.raise_for_status()
        return response
    return wine_search_response_wrapper


def wine_search_client_handler(fn):
    def wine_search_python_response_wrapper(self, *args, **kwargs):
        python_response = fn(self, *args, **kwargs)
        meta = python_response['meta']
        if meta['errmsg']:
            err = meta['errmsg'].decode('utf-8')
            if err == 'minimum price (mp) is not numeric' or \
                    err == 'maximum price (xp) is not numeric':
                raise SnoothTypeError('Max/min price should be numeric')
            elif err == 'authentication key is wrong':
                raise SnoothValueError('Bad API key')
            raise SnoothException('Client Error')
        if meta['results'] == 0:
            logging.warning('No matches, check query')
        return python_response
    return wine_search_python_response_wrapper
