import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf

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
        tickers = [entry.get() for _, entry in ticker_widgets]
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()

        if not tickers or any(t == "" for t in tickers):
            raise ValueError("Please enter all ticker symbols.")

        # Fetch data and plot
        fig, ax = plt.subplots(figsize=(6, 4))
        for ticker in tickers:
            data = yf.download(ticker, start=start_date, end=end_date)
            ax.plot(data['Close'], label=ticker)

        # Format x-axis (dates)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()

        # Format y-axis (prices)
        ax.yaxis.set_major_formatter('${x:.2f}')

        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.title("Stock Prices")
        plt.grid(True)
        plt.legend()  # Add legend to identify the lines
        plt.tight_layout()

        # Embed the plot in the Tkinter window
        for widget in plot_frame.winfo_children():
            widget.destroy()  # Clear previous plot

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except Exception as e:
        error_label.config(text=f"Error: {e}")

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
add_button.grid(row=3, column=0, padx=5, pady=10, sticky="w")

remove_button = ttk.Button(root, text="Remove Ticker", command=remove_ticker)
remove_button.grid(row=3, column=1, padx=5, pady=10, sticky="e")

# Button to fetch data
plot_button = ttk.Button(root, text="Get Data", command=get_data)
plot_button.grid(row=4, column=0, columnspan=2, pady=10)

# Frame for displaying the plot
plot_frame = ttk.Frame(root)
plot_frame.grid(row=5, column=0, columnspan=2, pady=10)

# Error label
error_label = ttk.Label(root, text="", foreground="red")
error_label.grid(row=6, column=0, columnspan=2)

# Run the application
root.mainloop()
