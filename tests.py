
import unittest
import json

import requests
import requests_mock
from bs4 import BeautifulSoup

from scraper import GroceriesSite as gs

class GroceriesSiteTest(unittest.TestCase): 
    def setUp(self):
        self.gs  = gs()

    def test_get_method(self):
        url = 'http://test.com/'
        status_code = 200
        with requests_mock.Mocker() as m:
            m.get('http://test.com', status_code=200)
            self.assertEqual(status_code, self.gs._get(url).status_code)

    def test_b_to_kb_method(self):
        b = 1024
        kb = '1.00kb'
        self.assertEqual(kb, self.gs._b_to_kb(b))

    def test_get_title_method(self):
        title = 'Test'
        product = BeautifulSoup('<a>Test\n\n\n</a>', 'html.parser')
        self.assertEqual(title, self.gs._get_title(product))

    def test_get_size_method(self):
        size = '1.00kb'
        content = '*' * 1024
        self.assertEqual(size, self.gs._get_size(content))
        self.assertEqual('', self.gs._get_size(''))

    def test_get_unit_price_method(self):
        product = BeautifulSoup(
            '<div class="pricePerUnit">test1.654test</div>', 'html.parser')
        self.assertEqual(1.65, self.gs._get_unit_price(product))

    def test_get_description_method(self):
        product = '<div class="productText">\nTest\n</div>'
        description = 'Test'
        self.assertEqual(description, self.gs._get_description(product))

    def test_get_product_url_method(self):
        url = 'test.test.test'
        product = BeautifulSoup(
            '<a href="test.test.test">test</a>', 'html.parser')
        self.assertEqual(url, self.gs._get_product_url(product))

    def test_get_products_method(self):
        html_text = '<div class="product">test</div>'
        products = BeautifulSoup(html_text, 'html.parser').find_all(class_='product')
        html = BeautifulSoup(html_text, 'html.parser')
        self.assertEqual(products, self.gs._get_products(html))

    def test_scrape_method(self):
        response_json = json.dumps({
            'products': [{
                'title': 'Test',
                'size': '0.04kb',
                'unit_price': 3.54,
                'description': 'TestDescription'
            }],
            'total': 3.54,
        }, indent=4, sort_keys=True)
        self.gs._url = 'http://test.com'
        mock_response = '''
            <div class="product">
                <a href="http://test.com/product">Test</a>
                <div class="pricePerUnit">3.545</div>
            </div>
        ''' 
        product_mock_response = '<div class="productText">TestDescription</div>'
        with requests_mock.Mocker() as m:        
            m.get('http://test.com', text=mock_response)
            m.get('http://test.com/product', text=product_mock_response)
            self.assertEqual(self.gs.scrape(), response_json)

if __name__ == '__main__':
    unittest.main()