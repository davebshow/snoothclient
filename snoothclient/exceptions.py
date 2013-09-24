# -*- coding: utf-8 -*-
from requests import HTTPError


class SnoothException(Exception):
    pass


class SnoothTypeError(TypeError):
    pass


class SnoothValueError(ValueError):
    pass


class SnoothHTTPError(HTTPError):
    pass
