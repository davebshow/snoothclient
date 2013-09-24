# -*- coding: utf-8 -*-
from requests import HTTPError


class SnoothError(Exception):
    pass


class SnoothTypeError(TypeError):
    pass


class SnoothValueError(ValueError):
    pass


class SnoothHTTPError(HTTPError):
    pass
