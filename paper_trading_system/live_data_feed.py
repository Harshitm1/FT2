"""
Live Data Feed using CCXT
Fetches real-time candles from exchange
"""
import ccxt
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import config

logger = logging.getLogger(__name__)


class LiveDataFeed:
    """Fetches live OHLCV data from exchange using CCXT"""
    
    def __init__(self, exchange_name: str = None, symbol: str = None, timeframe: str = None):
        """
        Initialize live data feed
        
        Args:
            exchange_name: Exchange to use (bybit, binance, etc.)
            symbol: Trading pair symbol
            timeframe: Candle timeframe (3m, 5m, etc.)
        """
        self.exchange_name = exchange_name or config.EXCHANGE
        self.symbol = symbol or config.SYMBOL
        self.timeframe = timeframe or config.TIMEFRAME
        
        # Initialize exchange
        exchange_class = getattr(ccxt, self.exchange_name)
        self.exchange = exchange_class({
            'enableRateLimit': True,
        })
        
        logger.info(f"Initialized {self.exchange_name} data feed for {self.symbol} {self.timeframe}")
        
    def fetch_historical_data(self, days: int = 365) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        
        Args:
            days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Fetching {days} days of historical data...")
        
        all_candles = []
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        # Fetch in batches
        batch_size = 30  # days per batch
        num_batches = (days + batch_size - 1) // batch_size
        
        for i in range(num_batches):
            batch_days = min(batch_size, days - i * batch_size)
            batch_since = int((datetime.now() - timedelta(days=days - i * batch_size)).timestamp() * 1000)
            
            logger.info(f"Fetching batch {i+1}/{num_batches} ({batch_days} days)...")
            
            retries = 0
            while retries < config.MAX_RETRIES:
                try:
                    candles = self.exchange.fetch_ohlcv(
                        self.symbol,
                        self.timeframe,
                        since=batch_since,
                        limit=1000
                    )
                    
                    if candles:
                        all_candles.extend(candles)
                        logger.info(f"Received {len(candles)} candles")
                    
                    time.sleep(self.exchange.rateLimit / 1000)  # Respect rate limits
                    break
                    
                except Exception as e:
                    retries += 1
                    logger.warning(f"Error fetching data (attempt {retries}/{config.MAX_RETRIES}): {e}")
                    if retries < config.MAX_RETRIES:
                        time.sleep(config.RETRY_DELAY)
                    else:
                        raise
        
        # Convert to DataFrame
        df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"✅ Loaded {len(df)} candles from {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return df
    
    def fetch_latest_candle(self) -> Optional[pd.Series]:
        """
        Fetch the most recent completed candle
        
        Returns:
            Series with OHLCV data or None if error
        """
        retries = 0
        while retries < config.MAX_RETRIES:
            try:
                candles = self.exchange.fetch_ohlcv(
                    self.symbol,
                    self.timeframe,
                    limit=2  # Get last 2 candles to ensure we have a completed one
                )
                
                if len(candles) >= 2:
                    # Return the second-to-last candle (most recent completed)
                    candle = candles[-2]
                    return pd.Series({
                        'timestamp': pd.to_datetime(candle[0], unit='ms'),
                        'open': candle[1],
                        'high': candle[2],
                        'low': candle[3],
                        'close': candle[4],
                        'volume': candle[5]
                    })
                    
            except Exception as e:
                retries += 1
                logger.warning(f"Error fetching latest candle (attempt {retries}/{config.MAX_RETRIES}): {e}")
                if retries < config.MAX_RETRIES:
                    time.sleep(config.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch latest candle after {config.MAX_RETRIES} attempts")
                    return None
        
        return None
    
    def get_current_price(self) -> Optional[float]:
        """
        Get current market price
        
        Returns:
            Current price or None if error
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return None


if __name__ == "__main__":
    # Test the data feed
    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT
    )
    
    feed = LiveDataFeed()
    
    # Test historical data
    print("\n" + "="*70)
    print("Testing Historical Data Fetch")
    print("="*70)
    df = feed.fetch_historical_data(days=7)
    print(f"\nFetched {len(df)} candles")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print("\nFirst 5 candles:")
    print(df.head())
    
    # Test latest candle
    print("\n" + "="*70)
    print("Testing Latest Candle Fetch")
    print("="*70)
    latest = feed.fetch_latest_candle()
    if latest is not None:
        print("\nLatest completed candle:")
        print(latest)
    
    # Test current price
    print("\n" + "="*70)
    print("Testing Current Price")
    print("="*70)
    price = feed.get_current_price()
    if price:
        print(f"\nCurrent {config.SYMBOL} price: ${price:,.2f}")
