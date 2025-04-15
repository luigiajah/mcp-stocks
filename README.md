# YFinance Trader MCP Tool

An MCP (Model Context Protocol) tool that provides stock market data and trading capabilities using the yfinance library.

## Features

- Real-time stock quotes
- Company information and financial metrics
- Historical price data
- Symbol search functionality
- Insider transaction tracking

## Setup

1. Ensure you have Python 3.10 or higher installed

2. Install dependencies:

```bash
pip install -r requirements.txt
# or using pyproject.toml
pip install .
```

## Integration with Cursor

1. In Cursor, go to Settings > MCP
2. Click "+ Add New MCP Server"
3. Fill in the form:
   - Name: "yfinance-trader" (or any name you prefer)
   - Command: `python3 /path/to/your/yfinance-trader/main.py`

Example command:

```
python3 /Users/username/projects/yfinance-trader/main.py
```

(Replace with your actual path to main.py)

4. Click "Add" and restart Cursor if needed

## Available Tools

### 1. get_stock_quote

Get real-time stock quote information:

```python
{
    "symbol": "AAPL",
    "price": 150.25,
    "change": 2.5,
    "changePercent": 1.67,
    "volume": 1234567,
    "timestamp": "2024-03-20T10:30:00"
}
```

### 2. get_company_overview

Get company information and key metrics:

```python
{
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "marketCap": 2500000000000,
    "peRatio": 25.4,
    "forwardPE": 24.2,
    "dividendYield": 0.65,
    "52WeekHigh": 182.94,
    "52WeekLow": 124.17
}
```

### 3. get_time_series_daily

Get historical daily price data:

```python
{
    "symbol": "AAPL",
    "timeSeriesDaily": [
        {
            "date": "2024-03-20T00:00:00",
            "open": 150.25,
            "high": 152.30,
            "low": 149.80,
            "close": 151.75,
            "volume": 12345678
        }
        // ... more data points
    ]
}
```

### 4. search_symbol

Search for stocks and other securities:

```python
{
    "results": [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "type": "EQUITY",
            "exchange": "NASDAQ"
        }
        // ... more results
    ]
}
```

### 5. get_recommendations

Get analyst recommendations for a stock:

```python
{
    "symbol": "AAPL",
    "recommendations": [
        {
            "period": "2024-03-15T00:00:00",
            "strongBuy": 15,
            "buy": 20,
            "hold": 8,
            "sell": 2,
            "strongSell": 0
        }
        // ... more periods
    ]
}
```

### 6. get_insider_transactions

Get insider trading information:

```python
{
    "symbol": "AAPL",
    "transactions": [
        {
            "date": "2024-03-15T00:00:00",
            "insider": "John Doe",
            "position": "Director",
            "transactionType": "Buy",
            "shares": 1000,
            "value": 150250.00,
            "url": "https://finance.yahoo.com/...",
            "text": "Purchase of 1000 shares",
            "startDate": "2024-03-15",
            "ownership": "Direct"
        }
        // ... more transactions
    ]
}
```

### 7. get_technical_indicators

Get advanced technical indicators for a stock (SMA, EMA, RSI, MACD, Stochastic, ATR, ADX, OBV, CCI, Supertrend, and more):

```python
{
    "symbol": "AAPL",
    "period": "3mo",
    "indicators": ["sma", "ema", "rsi", "macd", "stoch", "atr", "adx", "obv", "cci", "supertrend"]
}
```

Example response:

```python
{
    "sma_20": [...],
    "ema_20": [...],
    "rsi_14": [...],
    "macd": [...],
    "macd_signal": [...],
    "macd_hist": [...],
    "stoch_k": [...],
    "stoch_d": [...],
    "atr_14": [...],
    "adx_14": [...],
    "obv": [...],
    "cci_20": [...],
    "supertrend": [...],
    // ... more indicators
}
```

- If the `indicators` field is omitted, a comprehensive default set is returned.
- The endpoint works for Indian stocks (e.g., "TATAMOTORS") and will auto-resolve NSE/BSE symbols.

## Error Handling

All tools include proper error handling and will return an error message if something goes wrong:

```python
{
    "error": "Failed to fetch quote for INVALID_SYMBOL"
}
```

## Troubleshooting

If the MCP server is not working in Cursor:

1. Verify the path in your settings is correct and absolute
2. Make sure Python 3.10+ is in your system PATH
3. Check that all dependencies are installed
4. Try restarting Cursor
5. Check Cursor's logs for any error messages

## License

MIT License
