from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # List of assets to trade
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
        # No additional data required for this example
        return []

    def run(self, data):
        allocation_dict = {}
        total_momentum_score = 0
        momentum_scores = {}

        for ticker in self.tickers:
            macd_indicator = MACD(ticker, data["ohlcv"], self.fast, self.slow)
            macd = macd_indicator['MACD'][-1]  # Latest MACD value
            signal = macd_indicator['signal'][-1]  # Latest signal value
            momentum_score = macd - signal

            momentum_scores[ticker] = momentum_score
            total_momentum_score += abs(momentum_score)

        # Generate allocations based on momentum scores
        for ticker, momentum in momentum_scores.items():
            if total_momentum_score != 0:
                # Allocation based on how high the momentum score is relative to the total
                allocation_dict[ticker] = abs(momentum) / total_momentum_score
            else:
                # Even distribution if there's no momentum
                allocation_dict[ticker] = 1 / len(self.tickers)

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)