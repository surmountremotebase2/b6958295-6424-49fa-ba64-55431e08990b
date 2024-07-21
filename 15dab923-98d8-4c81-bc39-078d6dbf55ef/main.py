from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.optimization import MeanVarianceOptimizer
from surmount.data import get_ticker_correlation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self, tickers=None):
        # List of assets to trade
        if tickers:
            self.tickers = tickers
        else:
            self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "QQQ"]
        # MACD parameters
        self.fast = 12
        self.slow = 26

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

    def run(self, data):
        allocation_dict = {}
        momentum_scores = {}
        returns = []
        risks = []
        tickers_data = []

        for ticker in self.tickers:
            macd_indicator = MACD(ticker, data["ohlcv"], self.fast, self.slow)
            macd = macd_indicator['MACD'][-1]  # Latest MACD value
            signal = macd_indicator['signal'][-1]  # Latest signal value
            momentum_score = macd - signal

            momentum_scores[ticker] = momentum_score
            tickers_data.append(data["ohlcv"][ticker])
            # Assuming data["fundamentals"] contains necessary return and risk data
            returns.append(data["fundamentals"][ticker]['return'])
            risks.append(data["fundamentals"][ticker]['risk'])

        # Get correlation matrix
        correlation_matrix = get_ticker_correlation(tickers_data)

        # Perform mean-variance optimization
        mvo = MeanVarianceOptimizer(returns, risks, correlation_matrix)
        optimized_weights = mvo.optimize()

        # Generate allocations based on optimized weights
        for i, ticker in enumerate(self.tickers):
            allocation_dict[ticker] = optimized_weights[i]

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)