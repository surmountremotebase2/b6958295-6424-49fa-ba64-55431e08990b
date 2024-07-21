from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from finvizfinance.quote import finvizfinance
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

class SentimentBasedTradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]  # Example tech stocks
        self.max_allocation_per_stock = 0.2  # Maximum 20% allocation per stock
        self.sentiment_threshold = 0.1  # Threshold for considering sentiment significant
        self.lookback_period = 5  # Number of days to average sentiment over

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocations = {}
        total_sentiment = 0
        valid_sentiment_count = 0

        for ticker in self.tickers:
            sentiment_scores = []
            for i in range(self.lookback_period):
                if f"sentiment_{ticker}_{i}" in data:
                    sentiment = data[f"sentiment_{ticker}_{i}"]
                    if sentiment is not None:
                        sentiment_scores.append(sentiment)

            if sentiment_scores:
                avg_sentiment = np.mean(sentiment_scores)
                if abs(avg_sentiment) > self.sentiment_threshold:
                    allocations[ticker] = avg_sentiment
                    total_sentiment += abs(avg_sentiment)
                    valid_sentiment_count += 1

        if valid_sentiment_count > 0:
            # Normalize allocations
            for ticker in allocations:
                allocations[ticker] = (allocations[ticker] / total_sentiment) * self.max_allocation_per_stock * valid_sentiment_count
                allocations[ticker] = max(0, min(allocations[ticker], self.max_allocation_per_stock))  # Ensure allocation is between 0 and max_allocation_per_stock
        
        log(f"Current allocations: {allocations}")
        return TargetAllocation(allocations)

    def warmup(self):
        # Request sentiment data for the lookback period
        return {f"sentiment_{ticker}_{i}": SentimentData(ticker=ticker, days_ago=i) for ticker in self.tickers for i in range(self.lookback_period)}

class SentimentData:
    def __init__(self, ticker, days_ago):
        self.ticker = ticker
        self.days_ago = days_ago

    def fetch(self):
        _, sentiment, _ = get_news_sentiment(self.ticker)
        return sentiment

def get_news_sentiment(ticker):
    try:
        stock = finvizfinance(ticker)
        outer_ratings_df = stock.ticker_outer_ratings()
        news_df = stock.ticker_news()
        top_news_df = news_df[['Title', 'Link']].head(10)
        top_outer = outer_ratings_df[['Date', 'Status', 'Outer', 'Rating', 'Price']].head(6)
        
        sia = SentimentIntensityAnalyzer()
        
        top_news_df['Sentiment'] = top_news_df['Title'].apply(lambda title: sia.polarity_scores(title)['compound'])
        filtered_df = top_news_df[top_news_df['Sentiment'] != 0]
        
        if not filtered_df.empty:
            average_sentiment = filtered_df['Sentiment'].mean()
        else:
            average_sentiment = 0
        
        top_news = filtered_df[['Title', 'Link']]
        return top_outer, average_sentiment, top_news
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None