import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_data():
    """Fetches data for two stocks and displays them on the same graph."""
    try:
        ticker1 = ticker1_entry.get()
        ticker2 = ticker2_entry.get()
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()

        data1 = yf.download(ticker1, start=start_date, end=end_date)
        data2 = yf.download(ticker2, start=start_date, end=end_date)

        # Create Matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data1['Close'], label=ticker1)
        ax.plot(data2['Close'], label=ticker2)

        # Format x-axis (dates)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()

        # Format y-axis (prices)
        ax.yaxis.set_major_formatter('${x:.2f}')

        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        plt.title(f"{ticker1} vs {ticker2} Stock Price")
        plt.grid(True)
        plt.legend()  # Add legend to identify the lines
        plt.tight_layout()

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10)

    except Exception as e:
        error_label.config(text=f"Error: {e}")

# Create main window
root = tk.Tk()
root.title("Stock Price Viewer")

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