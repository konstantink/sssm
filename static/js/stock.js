/**
 * Created by user on 9/10/16.
 */

$(function() {
    var StockRecord = Backbone.Model.extend({
        // idAttribute: 'symbol',

        parse: function(response) {
            if (_.isUndefined(response.stock))
                return response;
            return response.stock;
        },

        toJSON: function () {
            return {
                symbol: this.get('symbol'),
                price: this.get('price'),
                type: this.get('type'),
                last_dividend: this.get('last_dividend'),
                fixed_dividend: this.get('fixed_dividend'),
                par_value: this.get('par_value')
            };
        }
    });

    var Stock = Backbone.Collection.extend({
        url: '/stocks',
        model: StockRecord,
        sortedField: 'timestamp',

        comparator: function(left, right) {
            var leftTimestamp = left.get(this.sortedField),
                rightTimestamp = right.get(this.sortedField);

            return leftTimestamp > rightTimestamp ? 1 : -1;
        },

        getBySymbol: function(symbol) {
            return this.findWhere({'symbol': symbol});
        },

        parse: function (response) {
            return response.stocks;
        }
    });

    var TradeRecord = Backbone.Model.extend({
        // idAttribute: 'symbol',

        parse: function(response) {
            if (_.isUndefined(response.trade))
                return response;
            return response.trade;
        },

        toJSON: function () {
            return {
                symbol: this.get('symbol'),
                price: this.get('price'),
                indicator: this.get('indicator'),
                quantity: this.get('quantity'),
                timestamp: moment.unix(this.get('timestamp')).format('DD/MM/YYYY HH:mm:ss')
            };
        }
    });

    var Trade = Backbone.Collection.extend({
        url: '/trades',
        model: TradeRecord,
        sortedField: 'timestamp',

        comparator: function(left, right) {
            var leftTimestamp = left.get(this.sortedField),
                rightTimestamp = right.get(this.sortedField);

            return leftTimestamp > rightTimestamp ? 1 : -1;
        },

        getBySymbol: function(symbol) {
            return this.findWhere({'symbol': symbol});
        },

        parse: function (response) {
            return response.trades;
        }
    });

    var StockItemView = Backbone.View.extend({
        tagName: 'tr',

        attributes: {
            "data-toggle": "popover",
            "data-container": "body"
        },

        tooltipTemplate: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',

        initialize: function() {
            _.bindAll(this, 'render');
        },

        render: function() {
            var tpl = Handlebars.compile($('#stock-item_tpl').html());
            $(this.el).html(tpl(this.model.toJSON()));
            $(this.el).popover({
                container: 'body',
                delay: 500,
                html: true,
                trigger: 'hover',
                template: this.tooltipTemplate,
                title: 'Hello',
                content: $.proxy(function() {
                    return "<b>Dividend yield:</b> " + (this.model.get('dividend_yield')*100).toFixed(2) + "%<br>" +
                           "<b>P/E Ratio:</b> " + this.model.get('pe_ratio').toFixed(2) + "<br>" +
                           "<b>VWSP:</b> " + this.model.get('vwsp').toFixed(2)
                }, this)
            });

            return this;
        }
    });

    var StockView = Backbone.View.extend({
        el: $('#stocks'),
        tradeIndicator: {
            'buy': 0,
            'sell': 1
        },

        events: _.defaults({
            'click #id_add-stock_btn': 'handleStockModal',
            'click #id_buy_btn': 'handleTradeModal',
            'click #id_sell_btn': 'handleTradeModal',
            'click #id_show-deals_btn': 'handleDealsModal'
        }, Backbone.View.prototype.events),

        handleStockModal: function() {
            this.renderStockModal();
            $('#id_stock-record_modal').modal('show');
        },

        handleTradeModal: function(e) {
            this.renderTradeModal($(e.target).data('action'));
            $('#id_trade_modal').modal('show');
        },

        handleDealsModal: function() {
            this.renderDealsModal();
            $('#id_deals_modal').modal('show');
        },

        renderStockModal: function() {
            var tpl = Handlebars.compile($('#stock-record_tpl').html()),
                $placeholder = $('#id_stock-record_modal');

            $placeholder.empty();
            $placeholder.append(tpl());
            $('#id_stock-record_modal #id_add-record_btn').on('click', this.submit);
            $('#id_stock-record_modal :input').on('change', this.updateAddStockButtonState);
            $('#id_stock-record_modal :input').on('keypress', this.hideErrors);
            this.initStockModalFields();
        },

        renderTradeModal: function(action) {
            var tpl = Handlebars.compile($('#trade_tpl').html()),
                $placeholder = $('#id_trade_modal');

            $placeholder.empty();
            $placeholder.append(tpl({
                action: action,
                indicator: this.tradeIndicator[action],
                stocks: this.collection.toJSON()
            }));
            $('#id_trade_modal #id_add-trade_btn').on('click', this.trade);
            $('#id_trade_modal :input').on('change', this.updateAddTradeButtonState);
            $('#id_trade_modal :input').on('keypress', this.hideErrors);
            this.initTradeModalFields();
        },

        renderDealsModal: function() {
            var tpl = Handlebars.compile($('#deals_tpl').html()),
                $placeholder = $('#id_deals_modal');

            this.tradeCollection.fetch();
            $placeholder.empty();
            $placeholder.append(tpl({
                trades: this.tradeCollection.toJSON()
            }));
        },

        initialize: function() {
            _.bindAll(this, 'render', 'handleStockModal', 'getCurrentStockValues', 'getRequiredFieldsState',
                      'updateAddStockButtonState', 'updateAddTradeButtonState', 'updatePriceField', 'submit', 'trade');

            this.collection = new Stock();
            this.collection.bind('add', this.appendItem);

            this.tradeCollection = new Trade();

            this.render();
        },

        render: function() {
            this.collection.fetch();
            this.tradeCollection.fetch();

            this.$el.html(Handlebars.compile($('#stocks_tpl').html())());
            this.$el.find('#id_stocks_list').html(Handlebars.compile($('#stock-table_tpl').html())());
            // this.delegateEvents();

            return this;
        },

        appendItem: function(item) {
            var itemView = new StockItemView({
                model: item
            });
            $('table tbody').append(itemView.render().el);
        },

        getCurrentStockValues: function() {
            var params = {};
            params.symbol = $.trim(this.stockFields.symbol.val());
            params.type = parseInt(this.stockFields.type.val());
            params.price = parseFloat(this.stockFields.price.val());
            params.last_dividend = parseInt(this.stockFields.last_dividend.val());
            if(params.type)
                params.fixed_dividend = parseFloat(this.stockFields.fixed_dividend.val());
            params.par_value = parseFloat(this.stockFields.par_value.val());

            return params;
        },

        getRequiredFieldsState: function() {
            var params = this.getCurrentStockValues();

            return params.par_value && params.symbol && params.price && ((params.type && params.fixed_dividend) ||
                !params.type) && params.last_dividend;
        },

        getCurrentTradeValues: function() {
            var params = {};
            params.symbol = $.trim(this.tradeFields.symbol.val());
            params.price = parseFloat(this.tradeFields.price.val());
            params.quantity = parseInt(this.tradeFields.quantity.val());
            params.indicator = parseInt(this.tradeFields.indicator.val());

            return params;
        },

        getTradeRequiredFields: function() {
            var params = this.getCurrentTradeValues();

            return params.quantity && params.symbol && params.price;
        },

        updateAddStockButtonState: function(e) {
            e.preventDefault();

            if (this.getRequiredFieldsState())
                $('#id_add-record_btn').removeClass('disabled');
            else
                $('#id_add-record_btn').addClass('disabled');
        },

        updateAddTradeButtonState: function(e) {
            e.preventDefault();

            if (this.getTradeRequiredFields())
                $('#id_add-trade_btn').removeClass('disabled');
            else
                $('#id_add-trade_btn').addClass('disabled');
        },

        hideErrors: function(e) {
            if ($(e.target).parents('.has-error')) {
                $(e.target).parents('.has-error').removeClass('has-error');
                $(e.target).siblings('.help-block').addClass('hidden');
            }
        },

        initStockModalFields: function() {
            this.stockFields = {
                symbol: $('#id_stock-symbol_input'),
                type: $('#id_type_input'),
                price: $('#id_price_input'),
                last_dividend: $('#id_last-dividend_input'),
                fixed_dividend: $('#id_fixed-dividend_input'),
                par_value: $('#id_par-value_input')
            };

            $('#id_type_input').on('change', function(e) {
                e.preventDefault();
                if ($(e.target).val())
                    $('#id_fixed-dividend_input').attr('disabled', false);
                else
                    $('#id_fixed-dividend_input').attr('disabled', true);
            });

            $('#id_price_input, #id_fixed-dividend_input, #id_par-value_input').on('keypress', function(e) {
                var v = $.trim($(e.target).val()) + e.key;
                if (/^\d+\.?(\d+)?$/.test(v))
                    return true;
                e.preventDefault();
            });
        },

        initTradeModalFields: function() {
            this.tradeFields = {
                symbol: $('#id_stock_input'),
                price: $('#id_share-price_input'),
                quantity: $('#id_share-quantity_input'),
                indicator: $('#id_indicator_input')
            };

            this.tradeFields.symbol.on('change', this.updatePriceField);
            this.tradeFields.symbol.change();
        },

        updatePriceField: function(e) {
            var val = $(e.target).val(),
                stock = this.collection.getBySymbol(val);

            if (!_.isUndefined(stock))
                this.tradeFields.price.val(stock.get('price'));
        },

        submit: function(e) {
            e.preventDefault();

            if ($(e.target).hasClass('disabled'))
                return false;

            console.log('continue');
            var params = this.getCurrentStockValues();

            this.collection.create(params, {
                wait: true,
                success: function(model, response) {
                    $('#id_stock-record_modal').modal('hide');
                },
                error: function(model, response) {
                    console.log(model, response);
                    var errors = response.responseJSON.errors;

                    _.each(_.keys(errors), function(field) {
                        var $spanBlock = $('[data-error-'+field+']'),
                            $field = $('[data-form-field-'+field+']');
                        if (field === '__all__') {
                            $spanBlock = $('[data-error-all]');
                            $field = $('[data-form-field-all]');
                        }
                        $field.addClass('has-error');
                        $spanBlock.html(errors[field].join('<br>'));
                        $spanBlock.removeClass('hidden');
                    });
                }
            })
        },

        trade: function(e) {
            e.preventDefault();

            if ($(e.target).hasClass('disabled'))
                return false;

            console.log('continue');
            var params = this.getCurrentTradeValues();

            this.tradeCollection.create(params, {
                wait: true,
                success: $.proxy(function(model, response) {
                    $('#id_trade_modal').modal('hide');
                    var stock = this.collection.getBySymbol(params.symbol);
                    stock.fetch({
                        url: stock.get('url')
                    });
                    $('#id_gbce').html(parseFloat(response.gbce_index).toFixed(2))
                }, this),
                error: function(model, response) {
                    console.log(model, response);
                    var errors = response.responseJSON.errors;

                    _.each(_.keys(errors), function(field) {
                        var $spanBlock = $('[data-error-'+field+']'),
                            $field = $('[data-form-field-'+field+']');
                        if (field === '__all__') {
                            $spanBlock = $('[data-error-all]');
                            $field = $('[data-form-field-all]');
                        }
                        $field.addClass('has-error');
                        $spanBlock.html(errors[field].join('<br>'));
                        $spanBlock.removeClass('hidden');
                    });
                }
            })

        }
    });

    window.view = new StockView();
});
