#!/usr/bin/env python

"""
This file is the scraper of sainsbury's example products
You can run it by executing ./scraper.py or python scraper.py
I hope you like it :)
"""

from __future__ import division

import requests
import json
import re

from bs4 import BeautifulSoup


DEFAULT_URL = 'http://hiring-tests.s3-website-eu-west-1.amazonaws.com/2015_Developer_Scrape/5_products.html'


class GroceriesSite(object):
    """
    GroceriesSite scraper object to collect groceries from specific url
    """

    def __init__(self, url=DEFAULT_URL):
        self._url = url

    @property
    def url(self):
        '''
        This is the url we will get products from
        '''
        return self._url

    def _get(self, url):
        '''
        shorthand for requests.get(url)
        '''
        _response = requests.get(url)
        if _response.status_code == 200:
            return _response

    def _b_to_kb(self, size):
        '''
        function converts bytes to kilobytes
        '''
        return '{0:.2f}kb'.format(size/1024)

    def _get_title(self, product):
        '''
        get product title
        '''
        return str([string for string in product.find('a').stripped_strings][0])

    def _get_size(self, content):
        '''
        get product html size
        '''
        if content:
            return self._b_to_kb(len(content))
        return ''

    def _get_unit_price(self, product):
        '''
        get product unit price
        '''
        _price_text = product.find(class_='pricePerUnit').text
        _price = float(re.findall('\d+\.\d+', _price_text)[0])
        return float('{0:.2f}'.format(_price))

    def _get_description(self, content):
        '''
        get product description from product html
        '''
        if content:
            _html = BeautifulSoup(content, "html.parser")
            _description = [string for string in _html.find(class_='productText').stripped_strings][0]
            return str(_description)
        return ''

    def _get_product_url(self, product):
        return product.find('a').attrs.get('href', '')

    def _get_products(self, html):
        '''
        get products from base html
        '''
        return html.find_all(class_='product')

    def scrape(self):
        '''
        base scraping function
        '''
        response = self._get(self.url)
        if response:
            html = BeautifulSoup(response.content, "html.parser")
            products_list = list()
            total_price = float()

            products = self._get_products(html)
            for _product in products:
                _url = self._get_product_url(_product)
                _response = self._get(_url)

                _product_content = ''
                if _response:
                    _product_content = _response.content

                _prod = {
                    'title': self._get_title(_product),
                    'size': self._get_size(_product_content),
                    'unit_price': self._get_unit_price(_product),
                    'description': self._get_description(_product_content),
                }
                total_price += _prod.get('unit_price')
                products_list.append(_prod)
            return json.dumps({
                'products': products_list,
                'total': float('{0:.2f}'.format(total_price)),
            }, indent=4, sort_keys=True)
        return json.dumps({})


if __name__ == '__main__':
    groceries = GroceriesSite()
    print groceries.scrape()
