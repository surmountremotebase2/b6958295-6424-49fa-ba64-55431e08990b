from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log
import numpy as np

class TradingStrategy(Strategy):
    def __init__(self, tickers=None, fast=12, slow=26):
        # List of assets to trade
        self.tickers = tickers if tickers else ["AAPL", "MSFT", "GOOGL", "AMZN", "QQQ"]
        # MACD parameters
        self.fast = fast
        self.slow = slow

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # Additional data for MVO and correlation analysis
        return ["ohlcv", "fundamentals"]

    def get_data(self, data_type, start, end):
        # Implement a method to fetch data based on type
        # This is a placeholder implementation
        if data_type == "ohlcv":
            return self.fetch_ohlcv_data(start, end)
        elif data_type == "fundamentals":
            return self.fetch_fundamentals_data(start, end)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def fetch_ohlcv_data(self, start, end):
        # Placeholder for actual OHLCV data fetching logic
        pass

    def fetch_fundamentals_data(self, start, end):
        # Placeholder for actual fundamentals data fetching logic
        pass

    def calculate_momentum_scores(self, data):
        momentum_scores = {}
        for ticker in self.tickers:
            macd_indicator = MACD(ticker, data["ohlcv"], self.fast, self.slow)
            macd = macd_indicator['MACD'][-1]  # Latest MACD value
            signal = macd_indicator['signal'][-1]  # Latest signal value
            momentum_score = macd - signal
            momentum_scores[ticker] = momentum_score
        return momentum_scores

    def optimize_portfolio(self, returns, risks):
        n = len(returns)
        weights = np.ones(n) / n  # Start with equal weights
        max_iterations = 1000
        learning_rate = 0.01

        for _ in range(max_iterations):
            # Compute portfolio return and risk
            portfolio_return = np.dot(weights, returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(np.diag(risks**2), weights)))

            # Calculate gradient (simplified for illustrative purposes)
            grad_return = returns
            grad_risk = risks / portfolio_risk

            # Update weights
            weights += learning_rate * (grad_return - grad_risk)
            weights = np.maximum(weights, 0)  # Ensure weights are non-negative
            weights /= np.sum(weights)  # Normalize to ensure weights sum to 1

        return weights

    def run(self, data):
        returns = []
        risks = []

        momentum_scores = self.calculate_momentum_scores(data)

        for ticker in self.tickers:
            # Assuming data["fundamentals"] contains necessary return and risk data
            returns.append(data["fundamentals"][ticker]['return'])
            risks.append(data["fundamentals"][ticker]['risk'])

        # Perform basic optimization
        optimized_weights = self.optimize_portfolio(np.array(returns), np.array(risks))

        # Generate allocations based on optimized weights
        allocation_dict = {ticker: optimized_weights[i] for i, ticker in enumerate(self.tickers)}

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)