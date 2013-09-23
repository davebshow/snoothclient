# -*- coding: utf-8 -*-


class Wine(object):

    def __init__(self, wine):
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
