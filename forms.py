# coding=UTF-8


from wtforms import Form, IntegerField, FloatField, StringField, SelectField, validators

from models import STOCK_TYPE, TRADE_TYPE


__author__ = 'Konstantin Kolesnikov'


class StockRecordForm(Form):
    """
    Stock record form provides incoming data validation

    :param symbol: string field, may be between 3 to 5 characters length
    :param type: string field, should one of the the following - 'Common', 'Preferred'
    :param last_dividend: integer field, should be greater or equal to 0
    :param fixed_dividend: float field, should be provided only when type is 'Preferred, value between 0.0 an 1.0
    :param par_value: integer field should be greater or equal to 0
    """
    symbol = StringField('Stock Symbol', [validators.Length(min=3, max=5), validators.InputRequired()])
    type = SelectField('Type', [validators.InputRequired()], choices=list(enumerate(STOCK_TYPE)), coerce=int)
    last_dividend = IntegerField('Last dividend', [validators.NumberRange(min=0), validators.InputRequired()])
    fixed_dividend = FloatField('Fixed dividend', [validators.NumberRange(min=0.0, max=1.0)],
                                default=0.0)
    par_value = IntegerField('Par value', [validators.NumberRange(min=0), validators.InputRequired()])
    price = FloatField('Stock price', [validators.NumberRange(min=0.0), validators.InputRequired()])


class TradeRecordForm(Form):
    """
    Trade record form provides incoming data validation

    :param symbol: string field, may be between 3 to 5 characters length
    :param type: string field, should one of the the following - 'Common', 'Preferred'
    :param last_dividend: integer field, should be greater or equal to 0
    :param fixed_dividend: float field, should be provided only when type is 'Preferred, value between 0.0 an 1.0
    """
    symbol = StringField('Stock Symbol', [validators.Length(min=3, max=5), validators.InputRequired()])
    price = FloatField('Traded price', [validators.NumberRange(min=0.0), validators.InputRequired()])
    quantity = IntegerField('Share quantity', [validators.NumberRange(min=1), validators.InputRequired()])
    indicator = SelectField('Indicator', [validators.InputRequired()], choices=list(enumerate(TRADE_TYPE)), coerce=int)
