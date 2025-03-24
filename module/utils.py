import math
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from datetime import datetime, timezone, timedelta
import re
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def rolling_sltf():
    pass

def rolloing_sltf_order():
    pass

def is_within_recommended_time(recommended_times, index):
    current_time = index.time()
    return any(start <= current_time <= end for start, end in recommended_times)

def timestamp_to_utc(timestamp: int, offset: int=8):
    """
    Calculate the UTC time from a timestamp with a given offset.
    
    Parameters:
    - timestamp (int): Timestamp to convert
    - offset (int): Timezone offset from UTC
    
    Returns:
    - str: UTC time in the format 'YYYY-MM-DD HH:MM:SS'
    """
    if type(timestamp) == str:
        return timestamp
    
    if timestamp > 10**10:
        timestamp /= 1000.0
        
    local_time = datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(hours=offset)
    utc_time = local_time.astimezone(timezone.utc)

    return utc_time.strftime('%Y-%m-%d %H:%M:%S')

def calculate_position(capital, price, fee_rate, leverage):
    """
    Calculate the position size based on capital, price, fees, and leverage.
    
    Parameters:
    - capital (float): Amount of capital to use
    - price (float): Current price
    - fee_rate (float): Trading fee rate (e.g., 0.0005 for 0.05%)
    - leverage (int): Trading leverage
    
    Returns:
    - float: Position size
    """
    # Account for fees in both opening and closing the position
    adjusted_capital = capital * leverage / (1 + 2 * fee_rate)
    position = adjusted_capital / price
    return position

def truncate_to_precision(number, precision):
    """
    Truncate a float to a specific number of decimal places.
    
    Parameters:
    - number (float): Number to truncate
    - precision (int): Number of decimal places
    
    Returns:
    - float: Truncated number
    """
    factor = 10 ** precision
    return math.floor(number * factor) / factor

def analyze(symbol, action):
    file_path = f"./logs/{symbol}_{action}.log"

    with open(file_path, "r") as f:
        logs = f.readlines()

    trade_pattern = re.compile(
        r"(Opened|Closed) (long|short) position: (-?\d+\.\d+) at ([\d.]+) on ([\d-]+ [\d:]+)"
    )
    profit_pattern = re.compile(r"Profit: ([\d.-]+)")

    trades = []
    for i in range(0, len(logs), 2):  # 每兩行為一組交易
        if i + 1 < len(logs):
            open_trade = trade_pattern.search(logs[i])
            close_trade = trade_pattern.search(logs[i + 1])
            profit_match = profit_pattern.search(logs[i + 1])

            if open_trade and close_trade and profit_match:
                action_type = open_trade.group(2)  # long or short
                open_price = float(open_trade.group(4))
                close_price = float(close_trade.group(4))
                open_time = open_trade.group(5)
                close_time = close_trade.group(5)
                profit = float(profit_match.group(1))

                trades.append({
                    "Type": action_type,
                    "Open Price": open_price,
                    "Close Price": close_price,
                    "Open Time": open_time,
                    "Close Time": close_time,
                    "Profit": profit
                })

    if not trades:
        print("No valid trades found.")
        return

    df = pd.DataFrame(trades)
    df = df.sort_values("Close Time").reset_index(drop=True)
    df["Open Hour"] = pd.to_datetime(df["Open Time"]).dt.hour

    df["Open Time Parsed"] = pd.to_datetime(df["Open Time"])
    df["Close Time Parsed"] = pd.to_datetime(df["Close Time"])
    df["Holding Time"] = (df["Close Time Parsed"] - df["Open Time Parsed"]).dt.total_seconds() / 60  # 單位為分鐘
    average_holding_minutes = df["Holding Time"].mean()

    df["Cumulative Profit"] = df["Profit"].cumsum()
    total_profit = df["Profit"].sum()
    total_trades = len(df)
    win_trades = df[df["Profit"] > 0].shape[0]
    loss_trades = df[df["Profit"] <= 0].shape[0]
    win_rate = win_trades / total_trades
    average_profit = df["Profit"].mean()
    total_gain = df[df["Profit"] > 0]["Profit"].sum()
    total_loss = abs(df[df["Profit"] < 0]["Profit"].sum())
    profit_factor = total_gain / total_loss if total_loss != 0 else float("inf")

    long_df = df[df["Type"] == "long"]
    long_trades = len(long_df)
    long_win_rate = (long_df["Profit"] > 0).sum() / long_trades if long_trades > 0 else 0
    long_profit = long_df["Profit"].sum()
    long_gain = long_df[long_df["Profit"] > 0]["Profit"].sum()
    long_loss = abs(long_df[long_df["Profit"] < 0]["Profit"].sum())
    long_profit_factor = long_gain / long_loss if long_loss != 0 else float("inf")

    short_df = df[df["Type"] == "short"]
    short_trades = len(short_df)
    short_win_rate = (short_df["Profit"] > 0).sum() / short_trades if short_trades > 0 else 0
    short_profit = short_df["Profit"].sum()
    short_gain = short_df[short_df["Profit"] > 0]["Profit"].sum()
    short_loss = abs(short_df[short_df["Profit"] < 0]["Profit"].sum())
    short_profit_factor = short_gain / short_loss if short_loss != 0 else float("inf")

    print("Strategy Metrics:")
    print(f"Total Profit: {total_profit:.4f}")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate * 100:.2f}%")
    print(f"Average Profit: {average_profit:.4f}")
    print(f"Profit Factor: {profit_factor:.4f}")
    print(f"Average Holding Time: {average_holding_minutes:.2f} minutes\n")

    print(f"Long Trades: {long_trades}")
    print(f"Long Win Rate: {long_win_rate * 100:.2f}%")
    print(f"Long Profit: {long_profit:.4f}")
    print(f"Long Profit Factor: {long_profit_factor:.4f}\n")

    print(f"Short Trades: {short_trades}")
    print(f"Short Win Rate: {short_win_rate * 100:.2f}%")
    print(f"Short Profit: {short_profit:.4f}")
    print(f"Short Profit Factor: {short_profit_factor:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].plot(range(1, total_trades + 1), df["Cumulative Profit"], color='orange')
    axes[0].set_title("Cumulative Profit Over Trades")
    axes[0].set_xlabel("Trade Number")
    axes[0].set_ylabel("Cumulative Profit")
    axes[0].grid(True)

    hours = np.arange(24)
    long_hourly = long_df.groupby("Open Hour")["Profit"].sum().reindex(hours, fill_value=0)
    short_hourly = short_df.groupby("Open Hour")["Profit"].sum().reindex(hours, fill_value=0)

    bar_width = 0.4
    axes[1].bar(hours - bar_width/2, long_hourly, width=bar_width, label='Long', alpha=0.7)
    axes[1].bar(hours + bar_width/2, short_hourly, width=bar_width, label='Short', alpha=0.7)
    axes[1].set_title("Hourly Profit by Position Type")
    axes[1].set_xlabel("Hour of Day")
    axes[1].set_ylabel("Profit")
    axes[1].xaxis.set_ticks(np.arange(0, 24, 3))
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()