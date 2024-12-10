import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import random
from datetime import datetime, timedelta

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

active_entry = None

def fetch_ticker_suggestions(query):
    query = query.upper().strip()
    return [ticker for ticker in all_tickers if query in ticker]

def update_suggestions(*args):
    query = ticker_search_var.get()
    suggestions = fetch_ticker_suggestions(query)
    ticker_listbox.delete(0, tk.END)
    for ticker in suggestions:
        ticker_listbox.insert(tk.END, ticker)

def set_active_entry(entry_name):
    global active_entry
    active_entry = entry_name.widget

def select_ticker(event):
    global active_entry
    selected_ticker = ticker_listbox.get(ticker_listbox.curselection())
    if active_entry:
        active_entry.delete(0, tk.END)
        active_entry.insert(0, selected_ticker)

def add_ticker():
    row = len(ticker_widgets)
    label = ttk.Label(ticker_frame, text=f"Enter stock ticker {row + 1}:")
    label.grid(row=row, column=0, padx=5, pady=5)
    entry = ttk.Entry(ticker_frame)
    entry.grid(row=row, column=1, padx=5, pady=5)
    entry.bind("<FocusIn>", set_active_entry)
    ticker_widgets.append((label, entry))

def remove_ticker():
    if ticker_widgets:  # Ensure there's at least one widget to remove
        label, entry = ticker_widgets.pop()
        label.destroy()  # Remove the label from the UI
        entry.destroy()  # Remove the entry from the UI

def get_data():
    try:
        tickers = [entry.get().strip().upper() for _, entry in ticker_widgets if entry.get().strip()]
        if not tickers:
            raise ValueError("At least one stock ticker must be entered.")

        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        if start_date >= end_date:
            raise ValueError("Start date must be before the end date.")

        if end_date > datetime.now().date():
            raise ValueError("End date cannot be in the future.")

        capital = float(capital_entry.get())
        if capital <= 0:
            raise ValueError("Starting capital must be greater than 0.")

        # Prepare for combined plotting
        fig, ax = plt.subplots(figsize=(8, 5))
        total_profit_loss = 0
        all_trade_history = []

        for ticker in tickers:
            try:
                # Download stock data
                end_date_adjusted = end_date + timedelta(days=1)
                data = yf.download(ticker, start=start_date, end=end_date_adjusted)
                if data.empty:
                    raise ValueError(
                        f"No data found for ticker '{ticker}' between the specified dates."
                    )

                # Simulation variables
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
                stop_loss_threshold = 0.9  # Stop-loss threshold (10% drop)

                for i in range(len(data.index)):
                    date = data.index[i]
                    price = data.loc[date, "Close"].item()

                    # Buy at local minima with some randomness
                    if date in local_minima.index.tolist() and shares == 0 and random.random() < 0.7:
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

                    # Sell at local maxima, stop-loss, or last day
                    elif (
                        (date in local_maxima.index.tolist() and random.random() < 0.7)
                        or (
                            last_buy_date is not None
                            and price < buy_price * stop_loss_threshold
                            and shares > 0
                        )
                        or (i == len(data.index) - 1 and shares > 0)
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

                # Save trade history for this ticker
                df = pd.DataFrame(trade_history)
                df = df.round({"Price": 3, "Capital": 3, "Profit/Loss": 3})
                filename = f"trade_history_{ticker}.csv"
                df.to_csv(filename, index=False)

                # Add this ticker's profit/loss to total
                total_profit_loss += total_profit
                all_trade_history.append({"Ticker": ticker, "Profit/Loss": total_profit})

                # Plot data for this ticker
                ax.plot(data.index, data["Close"], label=f"{ticker} (Profit: ${total_profit:.2f})")

            except Exception as e:
                print(f"Skipping {ticker} due to error: {e}")

        # Finalize plot
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        ax.set_xlabel("Date")
        ax.set_ylabel("Closing Price ($)")
        ax.set_title("Stock Price Simulation")
        ax.grid(True)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display combined results
        result_text = "\n".join([f"{t['Ticker']}: ${t['Profit/Loss']:.2f}" for t in all_trade_history])
        result_label.config(
            text=f"Total Profit/Loss: ${total_profit_loss:.2f}\n"
            f"Per Ticker Results:\n{result_text}",
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


# Create the main application window
root = tk.Tk()
root.title("Stock Price Viewer")

# Create a frame for ticker entries
ticker_frame = ttk.Frame(root)
ticker_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

# List to hold dynamically added ticker widgets
ticker_widgets = []

# Add initial tickers
for _ in range(2):
    add_ticker()

# Create StringVar for search
ticker_search_var = tk.StringVar()
ticker_search_var.trace_add("write", update_suggestions)

# Create a search entry box
search_label = ttk.Label(root, text="Search for a ticker, click on the ticker text box you wish to fill then click the ticker in the list you'd like: \n[Disclaimer: only stocks from the NASDAQ and NYSE are included]")
search_label.grid(row=0, column=2, padx=5, pady=5)
search_entry = ttk.Entry(root, textvariable=ticker_search_var)
search_entry.grid(row=0, column=3, padx=5, pady=5)

# Create a Listbox to display suggestions
ticker_listbox = tk.Listbox(root, height=5)
ticker_listbox.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
ticker_listbox.bind("<<ListboxSelect>>", select_ticker)

# Dates
start_date_label = ttk.Label(root, text="Start date:")
start_date_label.grid(row=1, column=0, padx=5, pady=5)
start_date_entry = DateEntry(root)
start_date_entry.grid(row=1, column=1, padx=5, pady=5)

end_date_label = ttk.Label(root, text="End date:")
end_date_label.grid(row=2, column=0, padx=5, pady=5)
end_date_entry = DateEntry(root)
end_date_entry.grid(row=2, column=1, padx=5, pady=5)

# Add and Remove buttons
add_button = ttk.Button(root, text="Add Ticker", command=add_ticker)
add_button.grid(row=4, column=0, padx=5, pady=10, sticky="w")

remove_button = ttk.Button(root, text="Remove Ticker", command=remove_ticker)
remove_button.grid(row=4, column=1, padx=5, pady=10, sticky="e")

# Add a label for Starting Capital
capital_label = ttk.Label(root, text="Starting Capital:")
capital_label.grid(row=3, column=0, padx=5, pady=5)

# Entry for Starting Capital
capital_entry = ttk.Entry(root)
capital_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Add some padding above the "Get Data" button
get_data_button = ttk.Button(root, text="Get Data", command=get_data)
get_data_button.grid(row=4, column=0, columnspan=2, pady=(15, 10))  # Extra padding above

# Error label
error_label = ttk.Label(root, text="", foreground="red")
error_label.grid(row=5, column=0, columnspan=4, pady=5, sticky="ew")

# Result label
result_label = ttk.Label(root, text="", justify="left")
result_label.grid(row=6, column=0, columnspan=4, pady=5, sticky="ew")

# Plot frame
plot_frame = ttk.Frame(root)
plot_frame.grid(row=7, column=0, columnspan=4, pady=10, sticky="nsew")

# Adjust grid weights for dynamic resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(7, weight=1)  # Allow plot_frame to expand dynamically

# Run the application
root.mainloop()
