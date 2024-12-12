import os
import random
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

script_dir = os.path.dirname(os.path.abspath(__file__))
nasdaq_csv_path = os.path.join(script_dir, "nasdaq-listed.csv")
nyse_csv_path = os.path.join(script_dir, "nyse.csv")

try:
    nasdaq_tickers = pd.read_csv(nasdaq_csv_path)["Symbol"].dropna().tolist()
    nasdaq_tickers = [
        str(ticker) for ticker in nasdaq_tickers if isinstance(ticker, str)
    ]

    nyse_tickers = pd.read_csv(nyse_csv_path)["Symbol"].dropna().tolist()
    nyse_tickers = [str(ticker) for ticker in nyse_tickers if isinstance(ticker, str)]

    all_tickers = nasdaq_tickers + nyse_tickers
except FileNotFoundError as e:
    print(f"File not found: {e}")
    all_tickers = []


def fetch_ticker_suggestions(query):
    query = query.upper().strip()
    return [ticker for ticker in all_tickers if query in ticker]


def update_suggestions(*args):
    query = ticker_entry.get()  # Get the query from the ticker_entry field
    suggestions = fetch_ticker_suggestions(query)
    ticker_listbox.delete(0, tk.END)
    for ticker in suggestions:
        ticker_listbox.insert(tk.END, ticker)


def select_ticker(event):
    selection = ticker_listbox.curselection()
    if selection:  # Make sure something is actually selected
        selected_ticker = ticker_listbox.get(selection[0])
        ticker_entry.delete(0, tk.END)
        ticker_entry.insert(0, selected_ticker)


def get_data():

    try:
        ticker = ticker_entry.get().strip().upper()
        if not ticker:
            raise ValueError("Stock ticker cannot be empty.")

        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        if start_date >= end_date:
            raise ValueError("Start date must be before the end date.")

        if end_date > datetime.now().date():
            raise ValueError("End date cannot be in the future.")

        capital = float(capital_entry.get())
        if capital <= 0:
            raise ValueError("Starting capital must be greater than 0.")

        # Download stock data with adjusted end_date
        end_date_adjusted = end_date + timedelta(days=1)
        data = yf.download(ticker, start=start_date, end=end_date_adjusted)
        if data.empty:
            raise ValueError(
                f"No data found for ticker '{ticker}' between the specified dates."
            )

        # Ensure data covers the entire date range
        available_start = data.index.min().date()
        available_end = data.index.max().date()
        if start_date < available_start or end_date > available_end:
            raise ValueError(
                f"Data is only available from {available_start} to {available_end}."
            )

        # Simulate buying and selling with potential losses
        shares = 0
        buy_price = 0
        trades = 0
        wins = 0
        losses = 0
        total_profit = 0
        trade_history = []

        data = data.dropna()

        local_minima = data[
            (data["Close"] < data["Close"].shift(1))
            & (data["Close"] < data["Close"].shift(-1))
        ].dropna()
        local_maxima = data[
            (data["Close"] > data["Close"].shift(1))
            & (data["Close"] > data["Close"].shift(-1))
        ].dropna()

        last_buy_date = None
        stop_loss_threshold = 0.9  # Trigger stop-loss if price drops 10%

        for i in range(len(data.index)):
            date = data.index[i]
            price = data.loc[date, "Close"].item()

            if date in local_minima.index.tolist():
                if capital >= price and shares == 0 and random.random() < 0.7:  # Added randomness
                    shares = int(capital / price)
                    capital -= shares * price
                    buy_price = price
                    trades += 1
                    last_buy_date = date
                    trade_history.append(
                        {
                            "Ticker": ticker,
                            "Date": date,
                            "Action": "Buy",
                            "Price": price,
                            "Shares": shares,
                            "Capital": capital,
                        }
                    )

            # Sell if at a local maximum, stop-loss is triggered, or if holding till the end
            elif (
                date in local_maxima.index.tolist() and random.random() < 0.7  # Added randomness
                or (
                    last_buy_date is not None
                    and price < buy_price * stop_loss_threshold
                    and shares > 0
                )
                or (i == len(data.index) - 1 and shares > 0)  # Sell on the last day if still holding
            ):
                if shares > 0:
                    trade_profit = shares * (price - buy_price)
                    total_profit += trade_profit
                    capital += shares * price
                    if trade_profit > 0:
                        wins += 1
                    else:
                        losses += 1
                    trade_history.append(
                        {
                            "Ticker": ticker,
                            "Date": date,
                            "Action": "Sell",
                            "Price": price,
                            "Shares Sold": shares,
                            "Capital": capital,
                            "Profit/Loss": trade_profit,
                        }
                    )
                    shares = 0
                    last_buy_date = None

        # Generate CSV file
        df = pd.DataFrame(trade_history)
        df = df.round({"Price": 3, "Capital": 3, "Profit/Loss": 3})

        # Use concat instead of append
        df = pd.concat([df, pd.DataFrame([{"Profit/Loss": total_profit}])])

        filename = f"trade_history_{ticker}.csv"
        df.to_csv(filename, index=False)

        # Clear previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Create and embed plot
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data.index, data["Close"], label="Closing Price", color="blue")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        ax.set_xlabel("Date")
        ax.set_ylabel("Closing Price ($)")
        ax.set_title(f"{ticker} Stock Price")
        ax.grid(True)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Allow plot to expand

        # Display results
        result_label.config(
            text=f"Ending Capital: ${capital:.2f}\n"
            f"Profit/Loss: ${total_profit:.2f}\n"
            f"Trades Executed: {trades}\n"
            f"Wins: {wins}, Losses: {losses}",
            foreground="black",
        )
        error_label.config(text="")

    except ValueError as ve:
        error_label.config(text=f"Error: {ve}", foreground="red")
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        error_label.config(text=f"Unexpected error: {e}", foreground="red")
        print(error_details)


# GUI Code
root = tk.Tk()
root.title("Stock Price Viewer")
root.geometry("700x800")
root.columnconfigure(0, weight=1)  # Column 0 expands horizontally
root.columnconfigure(1, weight=1)  # Column 1 expands horizontally
root.columnconfigure(2, weight=1)  # Column 2 expands horizontally
root.columnconfigure(3, weight=1)  # Column 3 expands horizontally
root.rowconfigure(7, weight=1)  # Row 7 expands vertically


# Create a Listbox to display suggestions
ticker_listbox = tk.Listbox(root, height=5)
ticker_listbox.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

# Bind the select_ticker function to the Listbox
ticker_listbox.bind("<<ListboxSelect>>", select_ticker)

# Ticker input
ttk.Label(root, text="Enter stock ticker:").grid(
    row=0, column=0, padx=5, pady=5, sticky="e"
)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ticker_entry.bind("<KeyRelease>", update_suggestions)  # Bind to KeyRelease event

# Start date input
ttk.Label(root, text="Start date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
start_date_entry = DateEntry(
    root, width=12, background="darkblue", foreground="white", borderwidth=2
)
start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# End date input
ttk.Label(root, text="End date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
end_date_entry = DateEntry(
    root, width=12, background="darkblue", foreground="white", borderwidth=2
)
end_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Starting capital input
ttk.Label(root, text="Starting Capital:").grid(
    row=3, column=0, padx=5, pady=5, sticky="e"
)
capital_entry = ttk.Entry(root)
capital_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Get data button
get_data_button = ttk.Button(root, text="Get Data", command=get_data)
get_data_button.grid(row=4, column=0, columnspan=2, pady=10)

# Error label
error_label = ttk.Label(root, text="", foreground="red")
error_label.grid(row=5, column=0, columnspan=4, pady=5, sticky="ew")

# Result label
result_label = ttk.Label(root, text="", justify="left")
result_label.grid(row=6, column=0, columnspan=4, pady=5, sticky="ew")

# Plot frame
plot_frame = ttk.Frame(root)
plot_frame.grid(row=7, column=0, columnspan=4, pady=10, sticky="nsew")

root.mainloop()