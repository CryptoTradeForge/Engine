from abc import ABC, abstractmethod

import pandas as pd

class Notifier(ABC):
    """
    Notifier abstract base class, ensuring all notifier implementations have a unified interface
    """
    @abstractmethod
    def send_message(self, msg: str):
        pass

class ExchangeAPI(ABC):
    """
    ExchangeAPI abstract base class, ensuring all exchange API implementations have a unified interface
    """

    @abstractmethod
    def place_market_order(self, symbol: str, side: str, quantity: float, stop_loss: float = None, take_profit: float = None):
        """
        Places a market order with optional Stop-Loss and Take-Profit.
        Remember to remove SL/TP orders if the position is closed with 'cancel_open_orders'.
        
        :param symbol: Trading pair, e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param quantity: Order quantity
        :param stop_loss: Stop-loss price (optional)
        :param take_profit: Take-profit price (optional)
        :return: Order information returned by Binance
        """
        pass

    @abstractmethod
    def fetch_historical_data(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        """
        Fetch historical K-line data from Binance with timestamps in UTC+8
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param interval: K-line interval, e.g. "1m, 5m, 15m, 1h, 4h, 1d"
        :param days: how many days of historical data to fetch
        :return: Pandas DataFrame containing K-line data with timestamps in UTC+8
        """
        pass
    
    @abstractmethod
    def place_market_order(self, symbol: str, side: str, quantity: float, stop_loss: float = None, take_profit: float = None):
        """
        Places a market order with optional Stop-Loss and Take-Profit.
        Remember to remove SL/TP orders if the position is closed with 'cancel_open_orders'.
        
        :param symbol: Trading pair, e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param quantity: Order quantity
        :param stop_loss: Stop-loss price (optional)
        :param take_profit: Take-profit price (optional)
        :return: Order information returned by Binance
        """
        pass

    @abstractmethod
    def cancel_open_orders(self, symbol: str):
        """
        Cancels all open SL/TP orders for a specific symbol.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        """
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> dict:
        """
        Checks if there is an open position for a given symbol.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        :return: Dictionary with position information, e.g. {"status": "open", "positionAmt": 0.1, "entryPrice": 50000}, or {"status": "closed"}
        """
        pass

    @abstractmethod
    def get_price_precision(self, symbol):
        """
        Get the precision of the trading pair on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: number of decimal places
        """
        pass
    
    @abstractmethod
    def get_quantity_precision(self, symbol):
        """
        Get the precision of the trading pair on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: number of decimal places
        """
        pass
  