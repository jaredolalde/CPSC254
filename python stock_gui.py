import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

script_dir = os.path.dirname(os.path.abspath(__file__))
nasdaq_csv_path = os.path.join(script_dir, 'nasdaq-listed.csv')
nyse_csv_path = os.path.join(script_dir, 'nyse.csv')

try:
    nasdaq_tickers = pd.read_csv(nasdaq_csv_path)['Symbol'].dropna().tolist()
    nasdaq_tickers = [str(ticker) for ticker in nasdaq_tickers if isinstance(ticker, str)]
    
    nyse_tickers = pd.read_csv(nyse_csv_path)['Symbol'].dropna().tolist()
    nyse_tickers = [str(ticker) for ticker in nyse_tickers if isinstance(ticker, str)]
    
    all_tickers = nasdaq_tickers + nyse_tickers
except FileNotFoundError as e:
    print(f"File not found: {e}")
    all_tickers = []


def fetch_ticker_suggestions(query):
    query = query.upper().strip()
    return [ticker for ticker in all_tickers if query in ticker]

def update_suggestions(*args):
    query = ticker_search_var.get()
    suggestions = fetch_ticker_suggestions(query)
    ticker_listbox.delete(0, tk.END)
    for ticker in suggestions:
        ticker_listbox.insert(tk.END, ticker)

def select_ticker(event):
    selected_ticker = ticker_listbox.get(ticker_listbox.curselection())
    ticker1_entry.delete(0, tk.END)
    ticker1_entry.insert(0, selected_ticker)
    ticker_listbox.delete(0, tk.END)

def get_data():
    try:
        ticker1 = ticker1_entry.get()
        ticker2 = ticker2_entry.get()
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()

        data1 = yf.download(ticker1, start=start_date, end=end_date)
        data2 = yf.download(ticker2, start=start_date, end=end_date)

        if data1.empty or data2.empty:
            error_label.config(text="Error: No data available for one or both tickers.")
            return

        # Create Matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data1['Close'], label=ticker1)
        ax.plot(data2['Close'], label=ticker2)

        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()

        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.title(f"{ticker1} vs {ticker2} Stock Price")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10)
    except Exception as e:
        error_label.config(text=f"Error: {e}")

# Create main window
root = tk.Tk()
root.title("Stock Price Viewer")

# Create StringVar for search
ticker_search_var = tk.StringVar()
ticker_search_var.trace_add("write", update_suggestions)

# Create a search entry box
search_label = ttk.Label(root, text="Search for a ticker: \n[Disclaimer: only stocks from the NASDAG and NYSE are included]")
search_label.grid(row=0, column=2, padx=5, pady=5)
search_entry = ttk.Entry(root, textvariable=ticker_search_var)
search_entry.grid(row=0, column=3, padx=5, pady=5)

# Create a Listbox to display suggestions
ticker_listbox = tk.Listbox(root, height=5)
ticker_listbox.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
ticker_listbox.bind("<<ListboxSelect>>", select_ticker)

# Ticker 1 input
ticker1_label = ttk.Label(root, text="Enter stock ticker 1:")
ticker1_label.grid(row=0, column=0, padx=5, pady=5)
ticker1_entry = ttk.Entry(root)
ticker1_entry.grid(row=0, column=1, padx=5, pady=5)

# Ticker 2 input
ticker2_label = ttk.Label(root, text="Enter stock ticker 2:")
ticker2_label.grid(row=1, column=0, padx=5, pady=5)
ticker2_entry = ttk.Entry(root)
ticker2_entry.grid(row=1, column=1, padx=5, pady=5)

# Start date input
start_date_label = ttk.Label(root, text="Start date:")
start_date_label.grid(row=2, column=0, padx=5, pady=5)
start_date_entry = DateEntry(root)
start_date_entry.grid(row=2, column=1, padx=5, pady=5)

# End date input
end_date_label = ttk.Label(root, text="End date:")
end_date_label.grid(row=3, column=0, padx=5, pady=5)
end_date_entry = DateEntry(root)
end_date_entry.grid(row=3, column=1, padx=5, pady=5)

# Button to fetch data
get_data_button = ttk.Button(root, text="Get Data", command=get_data)
get_data_button.grid(row=4, column=0, columnspan=2, pady=10)

# Error label
error_label = ttk.Label(root, text="", foreground="red")
error_label.grid(row=5, column=0, columnspan=2, pady=5)

root.mainloop()
