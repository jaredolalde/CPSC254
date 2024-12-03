import yfinance as yf
import json
from datetime import datetime
import os

class DataFetcher:
    def __init__(self, symbols, start_date, end_date):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self):
        for symbol in self.symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=self.start_date, end=self.end_date)
            data = hist.reset_index().to_dict(orient='records')
            filename = f'{symbol.lower()}_data_{self.start_date}_{self.end_date}.json'
            os.makedirs('data', exist_ok=True)  # Ensure the data directory exists
            filepath = os.path.join('data', filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, default=str)
            print(f"Data for {symbol} saved to {filepath}")

# Example usage
if __name__ == "__main__":
    fetcher = DataFetcher(['SOXL', 'SOXS'], '2021-01-01', str(datetime.now().date()))
    fetcher.fetch_data()