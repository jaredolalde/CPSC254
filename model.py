import csv
import json
import os
import pandas as pd
from datetime import datetime
from publisher_subscriber import Publisher

class DataModel(Publisher):
    def __init__(self, json_directory, data_adapter):
        super().__init__()
        self.json_directory = json_directory
        self.data_adapter = data_adapter

    def load_data(self, symbol):
        data = self.data_adapter.load_data(self.json_directory, symbol)
        if data is not None:
            df = pd.DataFrame(data)
            self.notify_subscribers("data_loaded", df)
        return pd.DataFrame(data)

    def calculate_sma(self, df, window):
        return df['Close'].rolling(window=window).mean()

    def get_latest_data(self, df):
        latest_row = df.iloc[-1]
        previous_row = df.iloc[-2]
        latest_date = latest_row['Date']
        latest_close = latest_row['Close']
        prev_close = previous_row['Close']
        change_percent = ((latest_close - prev_close) / prev_close) * 100
        return latest_date, latest_close, change_percent

    def save_trade_logs(self, trade_log, symbol, initial_balance, balance, filename='trade_log.csv'):
        total_gain_loss = balance - initial_balance
        percent_return = (total_gain_loss / initial_balance) * 100

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Symbol', 'Action', 'Price', 'Shares', 'Balance', 'Gain/Loss'])
            for trade in trade_log:
                formatted_trade = [
                    trade[1].strftime("%Y-%m-%d %H:%M:%S") if not isinstance(trade[1], str) else trade[1],
                    symbol,
                    trade[0],
                    f"${trade[3]:.2f}",
                    trade[2],
                    f"${trade[4]:.2f}",
                    f"${trade[5]:.2f}" if trade[5] != 'N/A' else 'N/A'
                ]
                writer.writerow(formatted_trade)
            writer.writerow([])
            writer.writerow(['Total Gain/Loss', 'Percent Return', 'Final Balance'])
            writer.writerow([f"${total_gain_loss:.2f}", f"{percent_return:.2f}%", f"${balance:.2f}"])

class DataAdapter:
    def load_data(self, directory, symbol):
        raise NotImplementedError("This method should be overridden by subclasses")