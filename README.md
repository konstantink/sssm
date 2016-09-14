# Super Simple Stock Market

Super Simple Stock Market is a part of technical interview

### Requirements

1. The Global Beverage Corporation Exchange is a new stock market trading in drinks companies.
    - Your company is building the object-oriented system to run that trading.
    - You have been assigned to build part of the core object model for a limited phase 1
2. Provide the source code for an application that will:-
    * For a given stock,
        - Given any price as input, calculate the dividend yield
        - Given any price as input, calculate the P/E Ratio
        - Record a trade, with timestamp, quantity, buy or sell indicator and price
        - Calculate Volume Weighted Stock Price based on trades in past 5 minutes
    * Calculate the GBCE All Share Index using the geometric mean of the Volume Weighted Stock Price for all stocks
    
### Solution

The problem solution is represented with the REST service. The list of server endpoints:
- **/** - implements method **GET**. Home page - entry point to the application
- **/stocks** - implements methods **GET** and **POST**. Returns the list of registered stocks in system or create a new stock record in the system respectively.
- **/stocks/<stock_symbol>** - implements method **PUT**. Updates the existing stock record and return it.
- **/trades** - implements methods **GET** and **POST**. For method **GET** server returns the list of successful trades for all stocks. For method **POST** server creates a new trade record and return it to the client.

The back-end part has next entities: `StockRecord`, `TradeRecord`, `Stock`, `Trade`.

- `StockRecord` - represents a single record about certain stock in the system. Among the input parameters it also includes dynamic properties such as `dividend_yield`, `pe_ratio` and `vwsp` which are recalculated every time the client requests the information about stock.
- `Stock` - represents a container for the `StockRecord` objects. It is implemented as a singleton. Also this class allows to iterate over all registered in the service stocks.
- `TradeRecord` - respresnsts a single record about deal on certain stock. It stores time when the deal happened, what stock, how many shares and at what price the deal was closed.
- `Trade` - represents a container for the `TradeRecord` objects. It is also (like `Stock` entity) implemented as a singleton and allows iteration over trading deals. It has a method called `get_trades_by_symbol` that returns the list of trades for the last period of time (defaults to 5 minutes), it is used to calculate Volume Weighted Stock Price. 

Forms for validating the input data are the next: `StockRecordForm`, `TradeRecordForm`. Forms check that the input data type corresponds to required, that values are correct and satisfies requirements. In case of any violation forms return the list of errors, so that client can fix his input data. 

### How to install

For Ubuntu:
```
$ sudo apt-get install python-pip
$ sudo pip install virtualenv
$ virtualenv --no-site-packages --python=python2.7 $VENV_PATH  #VENV_PATH - path where to install python virtual environment
```

Then:
```
$ git clone <url>
$ source $VENV_PATH/bin/activate
$ pip install -r requirements.txt
$ python app.py
```

By default the server works 127.0.0.1:5000. After starting the server you can open a new web page in the browser and write in the address line http://127.0.0.1:5000 