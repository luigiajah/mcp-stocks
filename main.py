from typing import Any, Dict, List
import yfinance as yf
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import pandas_ta as ta

# Helper to resolve Indian stock symbols
INDIAN_SUFFIXES = ['.NS', '.BO']
def resolve_indian_symbol(symbol: str) -> str:
    # If already suffixed, return as is
    if any(symbol.endswith(sfx) for sfx in INDIAN_SUFFIXES):
        return symbol
    # Try NSE first
    test_symbol = symbol + '.NS'
    try:
        stock = yf.Ticker(test_symbol)
        info = stock.info
        if info.get('regularMarketPrice') is not None:
            return test_symbol
    except Exception:
        pass
    # Try BSE
    test_symbol = symbol + '.BO'
    try:
        stock = yf.Ticker(test_symbol)
        info = stock.info
        if info.get('regularMarketPrice') is not None:
            return test_symbol
    except Exception:
        pass
    # Return original if not found
    return symbol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("yfinance-trader")

@mcp.tool("get_stock_quote")
async def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """Get real-time stock quote information.
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
    
    Returns:
        Dict containing current stock price and related information
    """
    symbol = resolve_indian_symbol(symbol)
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "symbol": symbol,
            "price": info.get("regularMarketPrice", 0),
            "change": info.get("regularMarketChange", 0),
            "changePercent": info.get("regularMarketChangePercent", 0),
            "volume": info.get("regularMarketVolume", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch quote for {symbol}"}

@mcp.tool("get_company_overview")
async def get_company_overview(symbol: str) -> Dict[str, Any]:
    """Get company information, financial ratios, and other key metrics.
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
    
    Returns:
        Dict containing company information and key metrics
    """
    symbol = resolve_indian_symbol(symbol)
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "marketCap": info.get("marketCap", 0),
            "peRatio": info.get("trailingPE", 0),
            "forwardPE": info.get("forwardPE", 0),
            "dividendYield": info.get("dividendYield", 0),
            "52WeekHigh": info.get("fiftyTwoWeekHigh", 0),
            "52WeekLow": info.get("fiftyTwoWeekLow", 0)
        }
    except Exception as e:
        logger.error(f"Error fetching company overview for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch company overview for {symbol}"}

@mcp.tool("get_time_series_daily")
async def get_time_series_daily(symbol: str, outputsize: str = "compact") -> Dict[str, Any]:
    """Get daily time series stock data.
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
        outputsize (str): Output size: 'compact' (latest 100 data points) or 'full' (up to 20 years of data)
    
    Returns:
        Dict containing historical daily price data
    """
    symbol = resolve_indian_symbol(symbol)
    try:
        stock = yf.Ticker(symbol)
        period = "3mo" if outputsize == "compact" else "max"
        history = stock.history(period=period)
        
        data = []
        for date, row in history.iterrows():
            data.append({
                "date": date.isoformat(),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })
        
        return {
            "symbol": symbol,
            "timeSeriesDaily": data
        }
    except Exception as e:
        logger.error(f"Error fetching time series for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch time series for {symbol}"}

@mcp.tool("search_symbol")
async def search_symbol(keywords: str) -> Dict[str, Any]:
    """Search for stocks, ETFs, mutual funds, or other securities.
    
    Args:
        keywords (str): Keywords to search for (e.g., apple, microsoft, tech)
    
    Returns:
        Dict containing search results
    """
    # For search, try both .NS and .BO for each keyword
    try:
        results = []
        for symbol in keywords.split():
            found = False
            for sfx in INDIAN_SUFFIXES:
                test_symbol = symbol + sfx
                try:
                    info = yf.Ticker(test_symbol).info
                    if info.get("longName"):
                        results.append({
                            "symbol": test_symbol,
                            "name": info.get("longName", ""),
                            "type": info.get("quoteType", ""),
                            "exchange": info.get("exchange", "")
                        })
                        found = True
                        break
                except Exception:
                    continue
            if not found:
                # fallback to global
                try:
                    info = yf.Ticker(symbol).info
                    if info.get("longName"):
                        results.append({
                            "symbol": symbol,
                            "name": info.get("longName", ""),
                            "type": info.get("quoteType", ""),
                            "exchange": info.get("exchange", "")
                        })
                except Exception:
                    continue
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching for {keywords}: {str(e)}")
        return {"error": f"Failed to search for {keywords}"}

@mcp.tool("get_recommendations")
async def get_recommendations(symbol: str) -> Dict[str, Any]:
    """Get analyst recommendations for a stock.
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
    
    Returns:
        Dict containing analyst recommendations including strongBuy, buy, hold, sell, strongSell counts
    """
    symbol = resolve_indian_symbol(symbol)
    try:
        stock = yf.Ticker(symbol)
        recommendations = stock.recommendations
        
        if recommendations is None or recommendations.empty:
            return {
                "symbol": symbol,
                "recommendations": []
            }
            
        # Convert the recommendations DataFrame to a list of dictionaries
        recs = []
        for index, row in recommendations.iterrows():
            rec_data = {
                "period": row.get("period", index.isoformat() if hasattr(index, "isoformat") else str(index)),
                "strongBuy": int(row.get("strongBuy", 0)),
                "buy": int(row.get("buy", 0)),
                "hold": int(row.get("hold", 0)),
                "sell": int(row.get("sell", 0)),
                "strongSell": int(row.get("strongSell", 0))
            }
            recs.append(rec_data)
            
        return {
            "symbol": symbol,
            "recommendations": recs
        }
    except Exception as e:
        logger.error(f"Error fetching recommendations for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch recommendations for {symbol}"}

@mcp.tool("get_insider_transactions")
async def get_insider_transactions(symbol: str) -> Dict[str, Any]:
    """Get insider transactions for a company.
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
    
    Returns:
        Dict containing recent insider transactions
    """
    symbol = resolve_indian_symbol(symbol)
    try:
        stock = yf.Ticker(symbol)
        insider = stock.insider_transactions
        
        if insider is None or insider.empty:
            return {
                "symbol": symbol,
                "transactions": []
            }
            
        transactions = []
        for index, row in insider.iterrows():
            transaction = {
                "date": index.isoformat() if hasattr(index, "isoformat") else str(index),
                "insider": row.get("Insider", ""),
                "position": row.get("Position", ""),
                "transactionType": row.get("Transaction", ""),
                "shares": int(row.get("Shares", 0)),
                "value": float(row.get("Value", 0)),
                "url": row.get("URL", ""),
                "text": row.get("Text", ""),
                "startDate": row.get("Start Date", ""),
                "ownership": row.get("Ownership", "")
            }
            transactions.append(transaction)
            
        return {
            "symbol": symbol,
            "transactions": transactions
        }
    except Exception as e:
        logger.error(f"Error fetching insider transactions for {symbol}: {str(e)}")
        return {"error": f"Failed to fetch insider transactions for {symbol}"}

@mcp.tool("get_technical_indicators")
async def get_technical_indicators(symbol: str, period: str = "3mo", indicators: List[str] = None) -> Dict[str, Any]:
    """
    Get a wide set of technical indicators for a stock using pandas_ta.
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
        period (str): Period for historical data, e.g., "3mo", "1y"
        indicators (List[str], optional): List of indicators to compute. If None, computes a default set.
    Returns:
        Dict containing requested indicators as lists keyed by indicator name
    """
    symbol = resolve_indian_symbol(symbol)
    stock = yf.Ticker(symbol)
    history = stock.history(period=period)
    if history.empty:
        return {"error": f"No historical data for {symbol}"}

    # Default set of indicators if not specified
    default_indicators = [
        "sma", "ema", "wma", "hma", "rsi", "stoch", "macd", "bbands", "adx", "atr", "cci", "roc", "willr", "obv", "cmf", "mfi", "supertrend"
    ]
    if indicators is None:
        indicators = default_indicators

    result = {}
    close = history['Close']
    high = history['High']
    low = history['Low']
    volume = history['Volume']

    # Moving Averages
    if "sma" in indicators:
        result["sma_20"] = ta.sma(close, length=20).dropna().tolist()
    if "ema" in indicators:
        result["ema_20"] = ta.ema(close, length=20).dropna().tolist()
    if "wma" in indicators:
        result["wma_20"] = ta.wma(close, length=20).dropna().tolist()
    if "hma" in indicators:
        result["hma_20"] = ta.hma(close, length=20).dropna().tolist()

    # Momentum
    if "rsi" in indicators:
        result["rsi_14"] = ta.rsi(close, length=14).dropna().tolist()
    if "stoch" in indicators:
        stoch = ta.stoch(high, low, close)
        result["stoch_k"] = stoch['STOCHk_14_3_3'].dropna().tolist() if 'STOCHk_14_3_3' in stoch else []
        result["stoch_d"] = stoch['STOCHd_14_3_3'].dropna().tolist() if 'STOCHd_14_3_3' in stoch else []
    if "macd" in indicators:
        macd = ta.macd(close)
        result["macd"] = macd['MACD_12_26_9'].dropna().tolist() if 'MACD_12_26_9' in macd else []
        result["macd_signal"] = macd['MACDs_12_26_9'].dropna().tolist() if 'MACDs_12_26_9' in macd else []
        result["macd_hist"] = macd['MACDh_12_26_9'].dropna().tolist() if 'MACDh_12_26_9' in macd else []
    if "roc" in indicators:
        result["roc_10"] = ta.roc(close, length=10).dropna().tolist()
    if "willr" in indicators:
        result["willr_14"] = ta.willr(high, low, close, length=14).dropna().tolist()

    # Volatility
    if "bbands" in indicators:
        bb = ta.bbands(close)
        result["bbands_upper"] = bb['BBU_20_2.0'].dropna().tolist() if 'BBU_20_2.0' in bb else []
        result["bbands_middle"] = bb['BBM_20_2.0'].dropna().tolist() if 'BBM_20_2.0' in bb else []
        result["bbands_lower"] = bb['BBL_20_2.0'].dropna().tolist() if 'BBL_20_2.0' in bb else []
    if "atr" in indicators:
        result["atr_14"] = ta.atr(high, low, close, length=14).dropna().tolist()
    if "adx" in indicators:
        result["adx_14"] = ta.adx(high, low, close, length=14)['ADX_14'].dropna().tolist()

    # Volume
    if "obv" in indicators:
        result["obv"] = ta.obv(close, volume).dropna().tolist()
    if "cmf" in indicators:
        result["cmf_20"] = ta.cmf(high, low, close, volume, length=20).dropna().tolist()
    if "mfi" in indicators:
        result["mfi_14"] = ta.mfi(high, low, close, volume, length=14).dropna().tolist()

    # Trend
    if "supertrend" in indicators:
        st = ta.supertrend(high, low, close)
        result["supertrend"] = st['SUPERT_7_3.0'].dropna().tolist() if 'SUPERT_7_3.0' in st else []
    if "cci" in indicators:
        result["cci_20"] = ta.cci(high, low, close, length=20).dropna().tolist()

    return result

if __name__ == "__main__":
    mcp.run() 