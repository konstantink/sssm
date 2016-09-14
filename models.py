# coding=UTF-8

import operator
import time


__author__ = 'Konstantin Kolesnikov'


STOCK_TYPE = {
    'common': 'Common',
    'preferred': 'Preferred'
}
TRADE_TYPE = {
    'buy': 'Buy',
    'sell': 'Sell'
}


class StockRecordExistsError(Exception):
    """
    Error indicates that stock with specified symbols is already registered

    :param: symbol: Duplicated stock symbol
    """

    def __init__(self, symbol):
        message = 'Stock symbol \'%s\' is already registered'
        super(StockRecordExistsError, self).__init__(message)
        self.symbol = symbol

    def __str__(self):
        return self.message % self.symbol


class StockRecord(object):
    """
    Class represents stock

    :param symbol: Stock symbol
    :param price: Stock symbol price
    :param type: Stock type ('Common' or 'Preferred')
    :param last_dividend: Stock last dividend
    :param fixed_dividend: Stock fixed dividend, applicable only to 'Preferred' stocks
    :param par_value: Stock Par-value
    """

    def __init__(self, symbol='', price=0.0, type=None, last_dividend=0, fixed_dividend=0.0, par_value=0):
        self.symbol = symbol
        self.price = price
        self.type = STOCK_TYPE.get(type, 'common')
        self.last_dividend = last_dividend
        self.fixed_dividend = fixed_dividend
        self.par_value = par_value
        self.timestamp = int(time.time())

    def __repr__(self):
        return 'StockRecord <symbol: %s; price: %s; type: %s; last_dividend: %s; fixed_divicdend: %s; par_value: %s>'\
               % (self.symbol, self.price, self.type, self.last_dividend, self.fixed_dividend, self.par_value)

    def json(self):
        obj = {
            'symbol': self.symbol,
            'price': self.price,
            'type': self.type,
            'last_dividend': self.last_dividend,
            'par_value': self.par_value,
            'dividend_yield': self.dividend_yield,
            'pe_ratio': self.pe_ratio,
            'vwsp': self.vwsp,
            'timestamp': self.timestamp,
            'url': self.url
        }
        if self.type == STOCK_TYPE['preferred']:
            obj['fixed_dividend'] = self.fixed_dividend
        return obj

    @property
    def url(self):
        return '/stocks/%s' % self.symbol

    @property
    def dividend_yield(self):
        """
        Stock dividend yield property

        :return: dividend yield calculated depending on the stock type
        """
        try:
            if self.type == STOCK_TYPE['preferred']:
                return float(self.last_dividend / self.price)
            return (self.fixed_dividend * self.par_value) / self.price
        except ZeroDivisionError:
            return 0.0

    @property
    def pe_ratio(self):
        """
        Stock P/E ratio property

        :return: P/E ratio calculated for the stock
        """
        try:
            return self.price / self.dividend_yield
        except ZeroDivisionError:
            return 0.0

    @property
    def vwsp(self):
        """
        Stock Volume Weighted Stock Price property

        :return: Volume Weighted Stock Price calculated for the stock
        """
        trades = Trade.get_instance().get_trades_for_symbol(self.symbol)
        try:
            return sum(tr.price * tr.quantity for tr in trades) / sum(tr.quantity for tr in trades)
        except ZeroDivisionError:
            return 0.0


class Stock(object):
    """
    Class represents Stock Market (singleton)

    :param _records: Dictionary includes all stocks added to the server
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '_instance') and getattr(cls, '_instance') is None:
            cls._instance = super(Stock, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._records = {}

    def __iter__(self):
        for _, v in self._records.iteritems():
            yield v

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Stock()
        return cls._instance

    def add(self, stock_record):
        """
        Add new stock record to the system

        :param stock_record: Stock Record instance to add
        :return: Nothing or raise StockRecordExistsError in case stock is already added to the system
        """
        if stock_record.symbol in self._records:
            raise StockRecordExistsError(stock_record.symbol)
        self._records[stock_record.symbol] = stock_record

    def update(self, stock_record):
        """
        Update stock record registered in the system

        :param stock_record: Stock Record instance to update
        :return: Nothing
        """
        self._records[stock_record.symbol] = stock_record

    def get_stock_by_symbol(self, symbol):
        return self._records.get(symbol)


class TradeStockRecord(object):
    """
    Class represents a trade record

    :param timestamp: Transaction timestamp
    :param indicator: Indicator 'Buy' or 'Sell'
    :param symbol: Stock symbol
    :param price: Traded price
    :param quantity: Shares quantity
    """

    def __init__(self, timestamp=None, indicator=None, symbol=None, price=0.0, quantity=0):
        self.timestamp = timestamp or int(time.time())
        self.indicator = TRADE_TYPE.get(indicator, 'buy')
        self.symbol = symbol or ''
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return 'TradeStockRecord <symbol: %s; price: %s; quantity: %s; indicator: %s; timestamp: %s>'\
               % (self.symbol, self.price, self.quantity, self.indicator, self.timestamp)

    def json(self):
        return {
            'timestamp': self.timestamp,
            'indicator': self.indicator,
            'symbol': self.symbol,
            'price': self.price,
            'quantity': self.quantity
        }


class Trade(object):
    """
    Class represents container of all trades

    :param _trades: List of all successful trades
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '_instance') and getattr(cls, '_instance') is None:
            cls._instance = super(Trade, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._trades = []

    def __iter__(self):
        for tr in self._trades:
            yield tr

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Trade()
        return cls._instance

    def _trade(self, symbol, price, quantity, indicator):
        trade = TradeStockRecord(symbol=symbol,
                                 price=price,
                                 quantity=quantity,
                                 indicator=indicator)
        self._trades.append(trade)
        return trade

    def buy(self, symbol, price, quantity):
        """
        Perform 'Buy' transaction

        :param symbol: Stock symbol
        :param price: Traded price
        :param quantity: Shares quantity
        :return: Successful Trade record
        """
        return self._trade(symbol, price, quantity, indicator='buy')

    def sell(self, symbol, price, quantity):
        """
        Perform 'Sell' transaction

        :param symbol: Stock symbol
        :param price: Traded price
        :param quantity: Shares quantity
        :return: Successful Trade record
        """
        return self._trade(symbol, price, quantity, indicator='sell')

    def get_trades_for_symbol(self, symbol, time_range=5):
        """
        Return list of trades for specified Stock Symbol for the last period (5 minutes by default)

        :param symbol: Stock symbol
        :param time_range: Period for the trades
        :return: List of trades
        """
        return [trade for trade in self
                if trade.symbol == symbol and (trade.timestamp > (int(time.time())-time_range*60))]

    @property
    def gbce_index(self):
        """
        Calculates GBCE All shares index

        :return: GBCE All shares index
        """
        stocks_vwsp = [Stock.get_instance().get_stock_by_symbol(tr.symbol).vwsp for tr in Trade.get_instance()]
        try:
            return (reduce(operator.mul, stocks_vwsp, 1)) ** (1.0/len(stocks_vwsp))
        except ZeroDivisionError:
            return 0.0

