from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Ensure "^VIX" matches the representation in Surmount's data source
        self.tickers = ["^VIX"]
        self.data_list = [Asset(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocations = {}
        
        for asset in self.data_list:
            # Retrieve the data for each asset from the provided 'data' dictionary
            if asset.ticker not in data:
                log(f"No data available for {asset.ticker}")
                continue
            
            asset_data = data[asset.ticker]
            
            if not isinstance(asset_data, pd.DataFrame):
                log(f"Expected DataFrame for {asset.ticker}, but got {type(asset_data)}")
                continue
            
            # Ensure data has 'Close' column
            if 'Close' not in asset_data.columns:
                log(f"'Close' column missing for {asset.ticker}")
                continue
            
            # Calculate the SMA for the last 10 days
            vix_prices = asset_data["Close"].tail(10)
            sma_10 = vix_prices.mean()
            
            current_vix_price = vix_prices.iloc[-1]
            
            # Decision-making based on the VIX price and SMA
            if current_vix_price > sma_10 * 1.10:
                log("Market might be entering a fear stage. Considering reducing equity exposure.")
                # Placeholder for actual reallocation logic
                allocations[asset.ticker] = TargetAllocation(0.1)  # Example: Reduce to 10%
            elif current_vix_price < sma_10:
                log("Market might be complacent. Considering increasing equity exposure.")
                # Placeholder for actual reallocation logic
                allocations[asset.ticker] = TargetAllocation(0.5)  # Example: Increase to 50%

        return allocations

# Example usage:
# Initialize the strategy
# strategy = TradingStrategy()
# Run the strategy with historical data
# results = strategy.run(data)