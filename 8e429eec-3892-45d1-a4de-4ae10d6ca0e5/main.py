#Type code her
from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.technical_indicators import RSI, SMA, BB, MACD, ADX
from surmount.data import Ratios

class AdvancedTradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NFLX"]
        self.data_list = [Ratios(ticker) for ticker in self.tickers]

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
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        ohlcv = data.get("ohlcv")

        if not ohlcv:
            log("No OHLCV data available")
            return TargetAllocation(allocation_dict)

        # Initialize variables for each ticker
        for ticker in self.tickers:
            try:
                # Calculate technical indicators
                rsi = RSI(ticker, ohlcv, 14)
                sma_50 = SMA(ticker, ohlcv, 50)
                sma_200 = SMA(ticker, ohlcv, 200)
                bbands = BB(ticker, ohlcv, 20, 2)
                macd = MACD(ticker, ohlcv, 12, 26)
                adx = ADX(ticker, ohlcv, 14)

                # Get the latest values for the indicators
                current_price = ohlcv[-1][ticker]['close']
                rsi_latest = rsi[-1] if rsi else None
                sma_50_latest = sma_50[-1] if sma_50 else None
                sma_200_latest = sma_200[-1] if sma_200 else None
                bbands_upper = bbands['upper'][-1] if bbands else None
                bbands_lower = bbands['lower'][-1] if bbands else None
                macd_diff = macd['macd'][-1] - macd['signal'][-1] if macd else None
                adx_latest = adx[-1] if adx else None

                # Example conditions for trading signals
                if rsi_latest and rsi_latest < 30:
                    log(f"{ticker} is oversold (RSI < 30)")
                    allocation_dict[ticker] += 0.1
                
                if sma_50_latest and sma_200_latest and sma_50_latest > sma_200_latest:
                    log(f"{ticker} is showing bullish trend (SMA 50 > SMA 200)")
                    allocation_dict[ticker] += 0.1

                if current_price < bbands_lower:
                    log(f"{ticker} is at lower Bollinger Band")
                    allocation_dict[ticker] += 0.1
                
                if macd_diff and macd_diff > 0:
                    log(f"{ticker} MACD is positive")
                    allocation_dict[ticker] += 0.1

                if adx_latest and adx_latest > 25:
                    log(f"{ticker} is trending strongly (ADX > 25)")
                    allocation_dict[ticker] += 0.1

                # Implement a maximum allocation cap
                if allocation_dict[ticker] > 1:
                    allocation_dict[ticker] = 1

            except Exception as e:
                log(f"Error processing {ticker}: {e}")

        # Normalize allocation to sum up to 1
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 0:
            allocation_dict = {ticker: allocation / total_allocation for ticker, allocation in allocation_dict.items()}

        return TargetAllocation(allocation_dict)