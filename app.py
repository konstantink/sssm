# coding=UTF-8


from flask import Flask
from flask import render_template, request, make_response
from flask import json

from forms import StockRecordForm, TradeRecordForm
from models import StockRecord, Stock, Trade, TRADE_TYPE, StockRecordExistsError


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/stocks', methods=['GET'])
def get_stocks():
    """
    Return list of successful trades

    :return: Status code 200 and the list of trades
    """
    response = make_response(json.dumps({'status': 'ok',
                                         'stocks': [st.json() for st in Stock.get_instance()]}))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/stocks', methods=['POST'])
def create_stock():
    """
    Create stock record

    :return: Status code 201 and successfully created stock
             Status code 400 and list of errors if provided data is incorrect
             Status code 404 when update non-registered stock

    Request body should contain following fields:
    :param symbol: Stock symbol
    :param price: Price
    :param type: Type
    :param last_dividend: Last dividend
    :param fixed_dividend: Fixed dividend
    :param par_value: Par-value
    """
    if request.is_json:
        form = StockRecordForm(**request.get_json())
    else:
        form = StockRecordForm(request.data)
    if form.validate():
        try:
            stock = StockRecord(**form.data)
            Stock.get_instance().add(stock)
        except StockRecordExistsError as e:
            return make_response(json.dumps({'status': 'error',
                                             'errors': {'symbol': [str(e)]}}), 400)
        return make_response(json.dumps({'status': 'ok',
                                         'stock': stock.json()}), 201)
    response = make_response(json.dumps({'status': 'error',
                                         'errors': form.errors}), 400)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/stocks/<stock_symbol>', methods=['GET'])
def get_stock(stock_symbol):
    """
    Get certain stock information

    :param stock_symbol: Stock symbol
    :return: Status code 200 and stock information
             Status code 404 in case stock in not registered
    """
    stock = Stock.get_instance().get_stock_by_symbol(stock_symbol)
    if stock is None:
        response = make_response(json.dumps({'status': 'error',
                                             'text': 'Stock \'%s\' is not found' % stock_symbol}), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    response = make_response(json.dumps({'status': 'ok',
                                         'stock': stock.json()}))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/stocks/<stock_symbol>', methods=['PUT'])
def update_stock(stock_symbol):
    """
    Update stock information

    :param stock_symbol: Stock symbol
    :return: Status code 200 and successfully updated stock
             Status code 400 and list of errors if provided data is incorrect
             Status code 404 when update non-registered stock

    Request body should contain following fields:
    :param symbol: Stock symbol
    :param price: Price
    :param type: Type
    :param last_dividend: Last dividend
    :param fixed_dividend: Fixed dividend
    :param par_value: Par-value
    """
    stock = Stock.get_instance().get_stock_by_symbol(stock_symbol)
    if stock is None:
        return make_response(json.dumps({'status': 'error',
                                         'text': 'Stock \'%s\' is not found' % stock_symbol}), 404)

    form = StockRecordForm(**request.get_json())
    if form.validate():
        form.populate_obj(stock)
        Stock.get_instance().update(stock)
        response = make_response(json.dumps({'status': 'ok',
                                             'stock': stock.json()}))
        response.headers['Content-Type'] = 'application/json'
        return response
    response = make_response(json.dumps({'status': 'error',
                                         'errors': form.errors}), 400)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/trades', methods=['GET'])
def get_trades():
    """
    Return list of successful trades

    :return: Status code 200 and the list of trades
    """
    response = make_response(json.dumps({'status': 'ok',
                                         'trades': [tr.json() for tr in Trade.get_instance()]}))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/trades', methods=['POST'])
def trade_shares():
    """
    Perform a trade action on a certain stock

    :return: Status code 201 if trade was successful
             Status code 400 and list of errors if provided data is incorrect
             Status code 404 when perform trade action on non-registered stock

    Request body should contain following fields:
    :param symbol: Stock symbol
    :param price: Price for which share are bought/sold
    :param quantity: Shares quantity
    :param indicator: Buy or sell
    """
    data = request.get_json()
    stock_symbol = data['symbol']
    stock = Stock.get_instance().get_stock_by_symbol(stock_symbol)
    if stock is None:
        return make_response(json.dumps({'status': 'error',
                                         'text': 'Stock \'%s\' is not found' % stock_symbol}), 404)

    form = TradeRecordForm(**data)
    if form.validate():
        action = getattr(Trade.get_instance(), TRADE_TYPE[form.data['indicator']].lower())
        trade = action(symbol=form.data['symbol'],
                       price=form.data['price'],
                       quantity=form.data['quantity'])
        response = make_response(json.dumps({'status': 'ok',
                                             'trade': trade.json()}))
        response.headers['Content-Type'] = 'application/json'
        return response
    response = make_response(json.dumps({'status': 'error',
                                         'errors': form.errors}), 400)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.run()
