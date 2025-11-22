import os
import dotenv
from datetime import datetime, timedelta, timezone
import logging
from tqdm import tqdm
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

import module.utils as utils
from module.BinanceAPI import BinanceAPI


class TradingEngine:
    """
    BacktestEngine handles the execution simulation part of backtesting,
    including position management, order placement, and trade tracking.
    """
    def __init__(
        self, 
        symbol: str, 
        capital_per_order: float = 100, 
        fee_rate: float = 0.0005, 
        leverage: int = 1,
        api: BinanceAPI = None,
        logger: logging.Logger = None
    ) -> None:
        if capital_per_order <= 0:
            raise ValueError("❌ Backtest Error: Capital per order must be greater than 0.")
        if not 0 < fee_rate < 1:
            raise ValueError("❌ Backtest Error: Fee rate cannot be negative.")
        if leverage <= 0:
            raise ValueError("❌ Backtest Error: Leverage must be greater than 0.")
        
        
        # Trading parameters
        self.symbol = symbol
        self.capital_per_order = capital_per_order
        self.fee_rate = fee_rate
        self.leverage = leverage
        
        # Position tracking
        self.position = 0
        self.open_price = None
        self.entry_time = None
        self.stop_loss = None
        self.take_profit = None

        self.api = api if api is not None else BinanceAPI()
        self.price_precision = self.api.get_price_precision(self.symbol)
        self.quantity_precision = self.api.get_quantity_precision(self.symbol)

        self.logger = logger if logger is not None else self.__setup_logger(symbol)

        try:
            self.api.client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
            self.api.client.futures_change_margin_type(symbol=self.symbol, marginType="ISOLATED")
        except Exception as e:
            print(f"❌ Binance API Error: Error changing leverage for {symbol} {e}")

        
    def fetch_historical_data(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        """
        Fetch historical data from API.
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param interval: K-line interval, e.g. "1m, 5m, 15m, 1h, 4h, 1d"
        :param days: how many days of historical data to fetch
        :return: Pandas DataFrame containing K-line data with timestamps in ohlcv
        """
        return self.api.fetch_historical_data(symbol, interval, days)
    
    def open_long(self, timestamp: any, price: float, stop_loss: float = None, take_profit: float = None) -> None:
        """
        Simulating open a long position.
        
        :param timestamp: timestamp of the open order
        :param price: price of the open order
        :param(choose) stop_loss: stop loss price
        :param(choose) take_profit: take profit price   
        :return: None
        """
        self.__open_position("long", timestamp, price, stop_loss, take_profit)
        
    def open_short(self, timestamp: any, price: float, stop_loss: float = None, take_profit: float = None) -> None:
        """
        Simulating open a short position.
        
        :param timestamp: timestamp of the open order
        :param price: price of the open order
        :param(choose) stop_loss: stop loss price
        :param(choose) take_profit: take profit price
        :return None
        """
        self.__open_position("short", timestamp, price, stop_loss, take_profit)
    
    def close_long(self, timestamp: any, price: float) -> None:
        """
        Simulating close a long position.
        
        :param timestamp: timestamp of the close order
        :param price: price of the close order
        :return: None
        """
        self.__close_position("long", timestamp, price)
        
    def close_short(self, timestamp: any, price: float) -> None:
        """
        Simulating close a short position.
        
        :param timestamp: timestamp of the close order
        :param price: price of the close order
        :return None
        """
        self.__close_position("short", timestamp, price)
    
    def anaylze(self) -> None:
        """
        Analyze the backtest result.
        
        :return: None
        """
        utils.analyze(self.symbol, "backtest")
        
    def __reset_position_state(self) -> None:
        """
        Reset the position state to initial.
        
        :return: None
        """
        attributes = ['open_price', 'entry_time', 'stop_loss', 'take_profit']
        for attr in attributes:
            setattr(self, attr, None)
        self.position = 0
    
    def __open_position(self, position_type: str, timestamp: any, price: float, stop_loss: float = None, take_profit: float = None) -> None:
        """
        Abstract method to open a position.
        
        :param position_type: "long" or "short"
        :param timestamp: timestamp of the open order
        :param price: price of the open order
        :param(choose) stop_loss: stop loss price
        :param(choose) take_profit: take profit price
        :return: None
        """
        if self.position != 0:
            raise ValueError(f"❌ Backtest Error: Cannot open {position_type} position when another position is open.")

        # Calculate the position size based on the capital per order
        open_position = utils.calculate_position(self.capital_per_order, price, self.fee_rate, self.leverage)
        open_position = utils.truncate_to_precision(open_position, self.quantity_precision)

        # Save trading details
        self.position = open_position if position_type == "long" else -open_position
        self.open_price = price
        self.entry_time = timestamp
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        utc8 = utils.timestamp_to_utc(timestamp, 8)
        self.logger.info(f"📈 Opened {position_type} position: {self.position} at {price} on {utc8}")
        self.api.place_market_order(self.symbol, "BUY" if position_type == "long" else "SELL", abs(self.position), stop_loss=stop_loss, take_profit=take_profit)

    def __close_position(self, position_type: str, timestamp: any, price: float) -> None:
        """
        Abstract method to close a position.
        
        :param position_type: "long" or "short"
        :param timestamp: timestamp of the close order
        :param price: price of the close order
        :return: None
        """
        if position_type == "long" and self.position <= 0:
            raise ValueError("❌ Backtest Error: Cannot close long position when no long position is open.")
        elif position_type == "short" and self.position >= 0:
            raise ValueError("❌ Backtest Error: Cannot close short position when no short position is open.")

        open_fee = abs(self.position) * self.open_price * self.fee_rate
        close_fee = abs(self.position) * price * self.fee_rate

        profit = self.position * (price - self.open_price) - open_fee - close_fee
        profit = utils.truncate_to_precision(profit, 4)

        utc8 = utils.timestamp_to_utc(timestamp, 8)
        self.logger.info(f"📉 Closed {position_type} position: {self.position} at {price} on {utc8}, Profit: {profit}")
        self.api.place_market_order(self.symbol, "SELL" if position_type == "long" else "BUY", abs(self.position))
        self.api.cancel_open_orders(self.symbol)
        self.__reset_position_state()  

    def __setup_logger(self, symbol: str) -> logging.Logger:
        """
        Setup logger for backtest.
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: logger
        """
        log_dir = "./logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = f"{log_dir}/{symbol}_backtest.log"
        if os.path.exists(log_file):
            open(log_file, 'w').close()
        logger = logging.getLogger(symbol)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger  
    
from time import sleep
if __name__ == "__main__":
    engine = TradingEngine("ETHUSDT", capital_per_order=50, fee_rate=0.0005, leverage=1)

    engine.open_long(1, 2100, stop_loss=2000, take_profit=2200)
    sleep(3)
    engine.close_long(1, 2072)