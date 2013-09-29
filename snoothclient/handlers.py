# -*- coding: utf-8 -*-
import logging
from errors import SnoothError


def http_error_handler(fn):
    def http_response_wrapper(self, *args, **kwargs):
        response = fn(self, *args, **kwargs)
        if response.status_code != 200:
            response.raise_for_status()
        return response
    return http_response_wrapper


def snooth_error_handler(fn):
    def snooth_response_wrapper(self, *args, **kwargs):
        snooth_response = fn(self, *args, **kwargs)
        meta = snooth_response['meta']
        errmsg = meta['errmsg'].decode('utf-8')
        if errmsg:
            raise SnoothError(errmsg)
        if meta['results'] == 0:
            logging.warning('No matches, check query')
        return snooth_response
    return snooth_response_wrapper
