import os
import dotenv
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

from .base import ExchangeAPI

class BinanceAPI(ExchangeAPI):
    def __init__(self):
        load_dotenv()
        self.client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))

    def place_market_order(self, symbol: str, side: str, quantity: float, stop_loss: float = None, take_profit: float = None):
        """
        Places a market order with optional Stop-Loss and Take-Profit.
        Remember to remove SL/TP orders if the position is closed with 'cancel_open_orders'.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param quantity: Order quantity
        :param stop_loss: Stop-loss price (optional)
        :param take_profit: Take-profit price (optional)
        :return: Dictionary with order IDs: {"market_order_id": int, "sl_order_id": int|None, "tp_order_id": int|None}
        """
        try:
            # Get precision for this symbol
            price_precision = self.get_price_precision(symbol)
            qty_precision = self.get_quantity_precision(symbol)

            # Format quantity
            from . import utils
            formatted_qty = utils.truncate_to_precision(quantity, qty_precision)

            # Open market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=formatted_qty
            )

            result = {
                "market_order_id": order["orderId"],
                "sl_order_id": None,
                "tp_order_id": None
            }

            # Determine opposite direction for stop orders
            stop_side = "SELL" if side == "BUY" else "BUY"

            # Place Stop-Loss Order (STOP_MARKET)
            if stop_loss:
                formatted_sl = utils.truncate_to_precision(stop_loss, price_precision)
                sl_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=stop_side,
                    type="STOP_MARKET",
                    stopPrice=formatted_sl,
                    quantity=formatted_qty
                )
                result["sl_order_id"] = sl_order["orderId"]

            # Place Take-Profit Order (TAKE_PROFIT_MARKET)
            if take_profit:
                formatted_tp = utils.truncate_to_precision(take_profit, price_precision)
                tp_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=stop_side,
                    type="TAKE_PROFIT_MARKET",
                    stopPrice=formatted_tp,
                    quantity=formatted_qty
                )
                result["tp_order_id"] = tp_order["orderId"]

            return result

        except Exception as e:
            print(f"❌ Binance API Error: Error opening orders for {symbol} {e}")
            return None

    def cancel_open_orders(self, symbol: str):
        """
        Cancels all open SL/TP orders for a specific symbol.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        """
        try:
            open_orders = self.client.futures_get_open_orders(symbol=symbol)
            for order in open_orders:
                order_id = order["orderId"]
                self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
                print(f"✅ Canceled Order ID: {order_id} for {symbol}")

        except Exception as e:
            print(f"❌ Binance API Error: Error canceling orders for {symbol} {e}")

    def cancel_order(self, symbol: str, order_id: int):
        """
        Cancels a specific order by order ID.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        :param order_id: The order ID to cancel
        """
        try:
            self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            print(f"✅ Canceled Order ID: {order_id} for {symbol}")

        except Exception as e:
            print(f"❌ Binance API Error: Error canceling order {order_id} for {symbol}: {e}")

    def get_position(self, symbol: str) -> dict:
        """
        Checks if there is an open position for a given symbol.

        :param symbol: Trading pair, e.g. "BTCUSDT"
        :return: Dictionary with position information, e.g. {"status": "open", "positionAmt": 0.1, "entryPrice": 50000}, or {"status": "closed"}
        """
        try:
            positions = self.client.futures_position_information()
            for position in positions:
                if position["symbol"] == symbol:
                    position_amt = float(position["positionAmt"])
                    if position_amt != 0:  # A non-zero position means it's still open
                        return position_amt
            return 0  # No open position found

        except Exception as e:
            print(f"❌ Binance API Error: Error fetching position for {symbol} {e}")

    def get_price_precision(self, symbol):
        """
        Get the precision of the trading pair on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: number of decimal places
        """
        try:
            info = self.client.futures_exchange_info()
            
            for s in info['symbols']:
                if s['symbol'] == symbol:
                    tick_size = s['filters'][0]["tickSize"]
                    tick_size = tick_size.rstrip('0')
                    
                    if '.' in tick_size:
                        return len(tick_size.split('.')[1])
                    return 0
                    
            raise ValueError(f"Symbol \"{symbol}\" not found")

        except Exception as e:
            print(f"❌ Binance API Error: Error fetching info for {symbol} {e}")
    
    def get_quantity_precision(self, symbol):
        """
        Get the precision of the trading pair on Binance
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :return: number of decimal places
        """
        try:
            info = self.client.futures_exchange_info()
            
            for s in info['symbols']:
                if s['symbol'] == symbol:
                    return s['quantityPrecision']
                
            raise ValueError(f"Symbol \"{symbol}\" not found")

        except Exception as e:
            print(f"❌ Binance API Error:  Error fetching info for {symbol} {e}")
        
    
    def fetch_historical_data(self, symbol: str, interval: str, days: int) -> pd.DataFrame:
        """
        Fetch historical K-line data from Binance with timestamps in UTC+8
        
        :param symbol: trading pair, e.g. "BTCUSDT"
        :param interval: K-line interval, e.g. "1m, 5m, 15m, 1h, 4h, 1d"
        :param days: how many days of historical data to fetch
        :return: Pandas DataFrame containing K-line data with timestamps in UTC+8
        """
        try:
            interval_mapping = {
                "1m": Client.KLINE_INTERVAL_1MINUTE,
                "5m": Client.KLINE_INTERVAL_5MINUTE,
                "15m": Client.KLINE_INTERVAL_15MINUTE,
                "1h": Client.KLINE_INTERVAL_1HOUR,
                "2h": Client.KLINE_INTERVAL_2HOUR,
                "4h": Client.KLINE_INTERVAL_4HOUR,
                "6h": Client.KLINE_INTERVAL_6HOUR,
                "8h": Client.KLINE_INTERVAL_8HOUR,
                "1d": Client.KLINE_INTERVAL_1DAY,
            }
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)

            klines = self.client.get_historical_klines(
                symbol,
                interval_mapping.get(interval, Client.KLINE_INTERVAL_1HOUR),
                int(start_time.timestamp() * 1000),
                int(end_time.timestamp() * 1000),
            )

            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
            ])
            
            df.set_index("open_time", inplace=True)
            df = df[["open", "high", "low", "close", "volume"]]
            df = df.astype(float)
            return df
        
        except Exception as e:
            print(f"❌ Binance API Error:  Error fetching data for {symbol} {e}")

if __name__ == "__main__":
    load_dotenv()
    api = BinanceAPI()
    
    # Get the precision of the BTCUSDT trading pair
    precision = api.get_quantity_precision("BTCUSDT")
    
    # Fetch historical data for BTCUSDT on the 1h interval for the past 1 day
    historical_data = api.fetch_historical_data("BTCUSDT", "1h", 1)
    print(historical_data)    
    # Open a position with a stop-loss and take-profit
    api.place_market_order("BTCUSDT", "BUY", 0.001, 100000, 103500)
    
    # Close a long position
    api.place_market_order("BTCUSDT", "SELL", 0.001)
    
    # Check if there is an open position, and cancel all open orders
    if(api.get_position("BTCUSDT")["status"] == "close"):
        api.cancel_open_orders("BTCUSDT")