import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry  # Ensure tkcalendar is installed
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf

def add_ticker():
    """Add a new ticker entry row."""
    row = len(ticker_widgets)
    label = ttk.Label(ticker_frame, text=f"Enter stock ticker {row + 1}:")
    label.grid(row=row, column=0, padx=5, pady=5)
    entry = ttk.Entry(ticker_frame)
    entry.grid(row=row, column=1, padx=5, pady=5)
    ticker_widgets.append((label, entry))

def remove_ticker():
    """Remove the last ticker entry row."""
    if ticker_widgets:  # Ensure there's at least one widget to remove
        label, entry = ticker_widgets.pop()
        label.destroy()  # Remove the label from the UI
        entry.destroy()  # Remove the entry from the UI

def get_data():
    """Fetches data for multiple stocks and displays them on the same graph."""
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
root.title("Dynamic Stock Data Viewer")

# Create a frame for ticker entries
ticker_frame = ttk.Frame(root)
ticker_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

# List to hold dynamically added ticker widgets
ticker_widgets = []

# Add initial tickers
for _ in range(2):
    add_ticker()

# Date inputs
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

# Plot button
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
