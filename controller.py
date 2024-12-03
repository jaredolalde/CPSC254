from publisher_subscriber import Subscriber

class DataController(Subscriber):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.initial_balance = 100000.0
        self.balance = self.initial_balance
        self.shares = 0
        self.trade_log = []
        self.symbol = ""

        self.model.subscribe("data_loaded", self)

    def run(self):
        symbol = input("Enter the symbol (SOXL or SOXS): ").upper()
        if symbol not in ['SOXL', 'SOXS']:
            print("Invalid symbol. Please enter either SOXL or SOXS.")
            return

        self.symbol = symbol

        df = self.model.load_data(symbol)
        if df is None:
            return

        latest_date, latest_close, change_percent = self.model.get_latest_data(df)
        self.view.display_latest_data(latest_date, latest_close, change_percent)

        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")

        try:
            short_window = int(input("Enter the short-term SMA period (e.g., 10): "))
            long_window = int(input("Enter the long-term SMA period (e.g., 100): "))

            if short_window >= long_window:
                print("Short-term SMA period must be less than long-term SMA period.")
                return

            self.trading_strategy(df, short_window, long_window)
            self.view.plot_data(df, start_date, end_date)
            self.view.display_performance(self.trade_log, self.initial_balance, self.balance)
            self.model.save_trade_logs(self.trade_log, self.symbol, self.initial_balance, self.balance, filename=f'trade_log_{symbol}.csv')
        except Exception as e:
            print(f"Error: {e}")

    def trading_strategy(self, df, short_window, long_window):
        self.balance = self.initial_balance
        self.shares = 0
        self.trade_log = []

        df["SMA_short"] = self.model.calculate_sma(df, short_window)
        df["SMA_long"] = self.model.calculate_sma(df, long_window)
        df.dropna(inplace=True)

        for i in range(1, len(df)):
            if (
                df["SMA_short"].iloc[i] > df["SMA_long"].iloc[i]
                and df["SMA_short"].iloc[i - 1] <= df["SMA_long"].iloc[i - 1]
            ):
                if self.balance > 0:
                    shares_to_buy = self.balance // df["Close"].iloc[i]
                    if shares_to_buy > 0:
                        self.balance -= shares_to_buy * df["Close"].iloc[i]
                        self.shares += shares_to_buy
                        self.trade_log.append(
                            (
                                "Buy",
                                df["Date"].iloc[i],
                                shares_to_buy,
                                df["Close"].iloc[i],
                                self.balance,
                                'N/A'
                            )
                        )
            elif (
                df["SMA_short"].iloc[i] < df["SMA_long"].iloc[i]
                and df["SMA_short"].iloc[i - 1] >= df["SMA_long"].iloc[i - 1]
            ):
                if self.shares > 0:
                    gain_loss = (self.shares * df["Close"].iloc[i]) - (self.shares * df["Close"].iloc[i-1])
                    self.balance += self.shares * df["Close"].iloc[i]
                    self.trade_log.append(
                        (
                            "Sell",
                            df["Date"].iloc[i],
                            self.shares,
                            df["Close"].iloc[i],
                            self.balance,
                            gain_loss
                        )
                    )
                    self.shares = 0

    def update(self, event_type, data):
        if event_type == "data_loaded":
            # Handle the data_loaded event if needed
            pass