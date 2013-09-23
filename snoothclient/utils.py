# -*- coding: utf-8 -*-
from structures import Wine


def wineify(wines):
    return [Wine(wine) for wine in wines]
