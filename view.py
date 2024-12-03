import matplotlib.pyplot as plt
import pandas as pd
from publisher_subscriber import Subscriber

class DataView(Subscriber):
    def update(self, event_type, data):
        if event_type == "data_loaded":
            self.plot_data(data)

    @staticmethod
    def display_latest_data(latest_date, latest_close, change_percent):
        print(f"Latest Market Date: {latest_date}")
        print(f"Latest Closing Price: ${latest_close:.2f}")
        print(f"% Change (compared to previous date): {change_percent:.2f}%")

    @staticmethod
    def plot_data(df, start_date=None, end_date=None):
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_convert(None)
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            df = df.loc[mask]

        plt.figure(figsize=(10, 5))
        plt.plot(df['Date'], df['Close'], label='Close Price')
        plt.plot(df['Date'], df['SMA_short'], label='Short-term SMA', linestyle='--')
        plt.plot(df['Date'], df['SMA_long'], label='Long-term SMA', linestyle='--')
        plt.title(f'Price History from {start_date.date()} to {end_date.date()}')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.legend()
        plt.grid(True)
        plt.show()

    @staticmethod
    def display_performance(trade_log, initial_balance, balance):
        total_trades = len(trade_log)
        total_gain_loss = balance - initial_balance
        percent_return = (total_gain_loss / initial_balance) * 100

        print("\nPerformance Evaluation:")
        print(f"Total Trades: {total_trades}")
        print(f"Total Gain/Loss: ${total_gain_loss:.2f}")
        print(f"Percent Return: {percent_return:.2f}%")

        trade_details = pd.DataFrame(
            trade_log, columns=["Action", "Date", "Shares", "Price", "Balance", "Gain/Loss"]
        )
        trade_details["Price ($)"] = trade_details["Price"].apply(lambda x: f"${x:.2f}")
        trade_details["Balance ($)"] = trade_details["Balance"].apply(lambda x: f"${x:.2f}")
        trade_details["Gain/Loss ($)"] = trade_details["Gain/Loss"].apply(lambda x: f"${x:.2f}" if x != 'N/A' else 'N/A')

        print("\nTrade Details:")
        print(trade_details[["Action", "Date", "Shares", "Price ($)", "Balance ($)", "Gain/Loss ($)"]].to_string(index=False))