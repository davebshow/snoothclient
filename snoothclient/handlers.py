# -*- coding: utf-8 -*-
import logging
from functools import wraps


class SnoothError(Exception):
    pass


def http_error(fn):
    def http_response_wrapper(self, *args, **kwargs):
        response = fn(self, *args, **kwargs)
        if response.status_code != 200:
            response.raise_for_status()
        return response
    return http_response_wrapper


def snooth_error(post=None):
    def snooth_error_handler(fn):
        def snooth_response_wrapper(self, *args, **kwargs):
            snooth_response = fn(self, *args, **kwargs)
            meta = snooth_response['meta']
            errmsg = meta['errmsg'].decode('utf-8')
            if errmsg:
                raise SnoothError(errmsg)
            if post and meta['status'] == 1:
                logging.warning('Successful post')
            elif post and meta['status'] == 0:
                logging.warning('Unsuccessful post')
            elif meta['results'] == 0:
                logging.warning('Unsuccessful query')
            return snooth_response
        return wraps(fn)(snooth_response_wrapper)
    return snooth_error_handler
