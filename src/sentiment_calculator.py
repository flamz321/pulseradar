def calculate_sentiment_score(current_price: float, prev_price: float, volume: float) -> float:
    return (current_price - prev_price) * volume
