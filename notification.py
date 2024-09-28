import yfinance as yf
from twilio.rest import Client
import schedule
import time
from datetime import datetime
import os
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER') 
PHONE_NUMBER = os.getenv('PHONE_NUMBER') 


class NotificationSystem:
    def __init__(self, tickers):
        """
        Initializes the NotificationSystem with the stock tickers, sets up Twilio credentials,
        and initializes dictionaries to store stock prices and Twilio client.

        :param tickers: A list of stock ticker symbols to monitor.
        """
        # Set up tickers and stock price tracking
        self.tickers = tickers
        self.prev_close_prices = {}

        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.twilio_number = TWILIO_PHONE_NUMBER
        self.phone_number = PHONE_NUMBER

        # Initialize Twilio client
        self.client = Client(self.account_sid, self.auth_token)

    def get_prev_close_prices(self):
        """
        Fetches the previous day's close price for each stock ticker and stores it in prev_close_prices dictionary.
        """
        for ticker in self.tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')  # Get the last two days of historical data

            # Check if data was returned
            if hist.empty:
                print(f"No historical data available for {ticker}. Skipping...")
                continue  # Skip this ticker if no data is available

            # Check if we have at least two days of data
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[0]  # Fetch previous day's close price
            else:
                prev_close = hist['Close'].iloc[-1]  # If only one day's data is available, use that

            self.prev_close_prices[ticker] = prev_close

    def check_price(self):
        """
        Compares the current price of each stock to its previous close price. If the price fluctuates by more than 1%,
        a notification is sent.
        """
        for ticker in self.tickers:
            stock = yf.Ticker(ticker)
            try:
                current_price = stock.fast_info['last_price']  # Fetch the current stock price
            except KeyError:
                print(f"Unable to fetch the current price for {ticker}.")
                continue

            prev_close = self.prev_close_prices[ticker]
            pct_change = ((current_price - prev_close) / prev_close) * 100  # Calculate percentage change

            if abs(pct_change) >= 1:  # Check if price change is >= 1%
                direction = 'rise' if pct_change > 0 else 'drop'
                message = f"{ticker}: {direction} >= 1%, Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.send_sms(message)
                # print(message)

    def send_sms(self, message):
        """
        Sends an SMS with the provided message using the Twilio API.

        :param message: The message to be sent via SMS.
        """
        self.client.messages.create(
            body=message,
            from_=self.twilio_number,
            to=self.phone_number
        )

    def start_monitoring(self):
        """
        Starts the monitoring process. Fetches the previous day's close prices, then schedules price checks
        every minute using the schedule library.
        """
        self.get_prev_close_prices()
        schedule.every(1).minutes.do(self.check_price)  # Schedule price checks every minute

        # Main loop to keep the scheduled tasks running
        while True:
            schedule.run_pending()  # Run scheduled tasks
            time.sleep(1)  # Sleep to avoid busy-waiting


if __name__ == "__main__":
    # Define the stock tickers to monitor
    tickers_to_monitor = ['SPY', 'IWM', 'QQQ']

    # Initialize the notification system
    notification_system = NotificationSystem(tickers=tickers_to_monitor)

    # Start monitoring
    notification_system.start_monitoring()


    # account_sid = TWILIO_ACCOUNT_SID
    # auth_token = TWILIO_AUTH_TOKEN
    # twilio_number = TWILIO_PHONE_NUMBER
    # phone_number = PHONE_NUMBER


    # client = Client(account_sid, auth_token)
    # client.messages.create(
    #     to=phone_number,
    #     from_=twilio_number,
    #     body="Hello there!")

