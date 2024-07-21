from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.data import get_ticker_correlation
from surmount.logging import log
import cvxpy as cp
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

    def calculate_momentum_scores(self, data):
        momentum_scores = {}
        for ticker in self.tickers:
            macd_indicator = MACD(ticker, data["ohlcv"], self.fast, self.slow)
            macd = macd_indicator['MACD'][-1]  # Latest MACD value
            signal = macd_indicator['signal'][-1]  # Latest signal value
            momentum_score = macd - signal
            momentum_scores[ticker] = momentum_score
        return momentum_scores

    def optimize_portfolio(self, returns, risks, correlation_matrix):
        n = len(returns)
        # Convert lists to numpy arrays
        returns = np.array(returns)
        risks = np.array(risks)
        correlation_matrix = np.array(correlation_matrix)

        # Create the covariance matrix from correlation and risks
        covariance_matrix = np.outer(risks, risks) * correlation_matrix

        # Define the optimization variables
        weights = cp.Variable(n)

        # Define the objective function: maximize returns for given risk (mean-variance optimization)
        objective = cp.Maximize(returns.T @ weights - cp.quad_form(weights, covariance_matrix))

        # Define the constraints: sum of weights is 1, weights are non-negative
        constraints = [cp.sum(weights) == 1, weights >= 0]

        # Formulate and solve the optimization problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        # Retrieve the optimized weights
        optimized_weights = weights.value
        return optimized_weights

    def run(self, data):
        returns = []
        risks = []

        momentum_scores = self.calculate_momentum_scores(data)

        for ticker in self.tickers:
            # Assuming data["fundamentals"] contains necessary return and risk data
            returns.append(data["fundamentals"][ticker]['return'])
            risks.append(data["fundamentals"][ticker]['risk'])

        # Get correlation matrix
        correlation_matrix = get_ticker_correlation(self.tickers)

        # Perform mean-variance optimization
        optimized_weights = self.optimize_portfolio(returns, risks, correlation_matrix)

        # Generate allocations based on optimized weights
        allocation_dict = {ticker: optimized_weights[i] for i, ticker in enumerate(self.tickers)}

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)