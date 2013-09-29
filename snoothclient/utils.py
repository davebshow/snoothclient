# -*- coding: utf-8 -*-
from structures import Wine


def wineify(wines):
    return [Wine(wine) for wine in wines]


def _translate_bool(*args):
    results = []
    for arg in args:
        if arg is False:
            arg = 0
        else:
            arg = 1
        results.append(arg)
    return results
