# coding=UTF-8


import unittest

from werkzeug.datastructures import MultiDict

from forms import StockRecordForm, TradeRecordForm
from models import StockRecord, Stock


__author__ = 'Konstantin Kolesnikov'


class TestStockRecordForm(unittest.TestCase):

    def test__empty_stock_record_creation(self):
        data = {}
        error = ['This field is required.']
        expected_errors = {
            'symbol': error,
            'price': error,
            'par_value': error,
            'last_dividend': error,
            'type': error
        }
        form = StockRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertFalse(validation, 'Form is valid, but should be invalid')
        self.assertDictEqual(form.errors, expected_errors,
                             'All fields are required.')

    def test__create_common_stock(self):
        data = {
            'symbol': 'TEST',
            'price': 1.0,
            'par_value': 1.0,
            'last_dividend': 1,
            'type': 'common'
        }
        form = StockRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertTrue(validation, 'Form is invalid, but all the required data is provided.')

    def test__create_preferred_stock_without_fixed(self):
        data = {
            'symbol': 'TEST',
            'price': 1.0,
            'par_value': 1.0,
            'last_dividend': 1,
            'type': 'preferred'
        }
        expected_error = {
            'fixed_dividend': ['Fixed dividend should be defined for Preferred stock type']
        }

        form = StockRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertFalse(validation, 'Form is valid, but fixed dividend is not provided.')
        self.assertDictEqual(form.errors, expected_error,
                             'Fixed dividend is required for preferred stock')

    def test__create_preferred_stock_wit_fixed(self):
        data = {
            'symbol': 'TEST',
            'price': 1.0,
            'par_value': 1.0,
            'last_dividend': 1,
            'fixed_dividend': 0.02,
            'type': 'preferred'
        }
        expected_error = {
            'fixed_dividend': ['Fixed dividend should be defined for Preferred stock type']
        }

        form = StockRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertTrue(validation, 'Form is valid, but fixed dividend is not provided.')


class TestTradeRecordForm(unittest.TestCase):

    def test__empty_trade_record_creation(self):
        data = {}
        error = ['This field is required.']
        expected_errors = {
            'symbol': error,
            'price': error,
            'quantity': error,
            'indicator': error,
        }
        form = TradeRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertFalse(validation, 'Form is valid, but should be invalid')
        self.assertDictEqual(form.errors, expected_errors,
                             'All fields are required.')

    def test__create_trade_record_for_non_existing_symbol(self):
        non_existing_symbol = 'SYM'
        expected_error = {
            'symbol': ['Stock symbol is not registered at the market.']
        }
        data = {
            'symbol': non_existing_symbol,
            'indicator': 'buy',
            'price': 10.0,
            'quantity': 1
        }

        form = TradeRecordForm(MultiDict(mapping=data))
        validation = form.validate()

        self.assertFalse(validation, 'It is impossible to trade not registered stocks')
        self.assertDictEqual(form.errors, expected_error,
                             'Can\'t trade non-registered stocks.')

    def test__create_trade_record_0_quantity(self):
        expected_error = {
            'quantity': ['This field is required.']
        }
        stock_data = {
            'symbol': 'SYM1',
            'type': 'common',
            'price': 100.0,
            'last_dividend': 10.0,
            'par_value': 5.0
        }
        trade_data = {
            'symbol': 'SYM1',
            'price': 20.0,
            'indicator': 'buy',
            'quantity': 0
        }

        stock_form = StockRecordForm(MultiDict(mapping=stock_data))
        validation = stock_form.validate()

        self.assertTrue(validation, 'Stock is not registered')

        Stock.get_instance().add(StockRecord(**stock_form.data))

        trade_form = TradeRecordForm(MultiDict(mapping=trade_data))
        validation = trade_form.validate()

        self.assertFalse(validation, 'Can\'t trade 0 shares')
        self.assertDictEqual(trade_form.errors, expected_error,
                             'Should be greater than 0')



if __name__ == '__main__':
    unittest.main()
