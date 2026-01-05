"""
Order Block Detection Strategy
Extracted from deploy3.py for real-time use
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class OrderBlockStrategy:
    """
    Order block detection strategy with trend and volume filtering
    """
    
    def __init__(self, sensitivity=0.015, min_volume_percentile=50,
                 trend_period=20, min_trades_distance=10):
        """
        Initialize order block strategy
        
        Args:
            sensitivity: Price change sensitivity for signal generation
            min_volume_percentile: Minimum volume percentile for valid trades
            trend_period: Period for trend calculation
            min_trades_distance: Minimum bars between trades
        """
        self.sensitivity = sensitivity
        self.min_volume_percentile = min_volume_percentile
        self.trend_period = trend_period
        self.min_trades_distance = min_trades_distance
        self.last_trade_index = -self.min_trades_distance
        
        logger.info(f"Initialized OrderBlockStrategy with sensitivity={sensitivity}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all necessary indicators for the strategy
        Uses strictly causal (past-only) calculations to avoid look-ahead bias
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Percentage change over 4 bars for signal generation
        df['pc'] = (df['open'] - df['open'].shift(4)) / df['open'].shift(4) * 100
        
        # Volume moving average (past 20 candles)
        df['volume_ma'] = df['volume'].rolling(window=20).mean().shift(1)
        
        # Volume percentile using only PAST data
        def calc_volume_percentile(series):
            if len(series) < 2:
                return 50.0
            current_vol = series.iloc[-1]
            past_vols = series.iloc[:-1]
            return (current_vol > past_vols).mean() * 100
        
        df['volume_percentile'] = df['volume'].expanding().apply(calc_volume_percentile, raw=False)
        
        # Trend indicators using only past candles
        df['sma20'] = df['close'].rolling(window=self.trend_period).mean().shift(1)
        df['sma50'] = df['close'].rolling(window=50).mean().shift(1)
        
        # ATR for volatility filtering (causal)
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean().shift(1)
        
        # Expanding average of ATR using only PAST data
        df['expanding_avg_atr'] = df['atr'].expanding().apply(
            lambda x: x[:-1].mean() if len(x) > 1 else np.nan, raw=False
        )
        
        # Momentum indicator using lagged calculation (causal)
        df['roc'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100
        
        return df
    
    def is_valid_trade_condition(self, df: pd.DataFrame, idx: int, trade_type: str = 'long') -> bool:
        """
        Check if current conditions are valid for entering a new trade
        
        Args:
            df: DataFrame with indicators
            idx: Current index
            trade_type: 'long' or 'short'
            
        Returns:
            True if trade conditions are valid
        """
        # Check if enough distance from last trade
        if idx - self.last_trade_index < self.min_trades_distance:
            return False
        
        # Check volume conditions
        if pd.isna(df['volume_percentile'].iloc[idx]) or df['volume_percentile'].iloc[idx] < self.min_volume_percentile:
            return False
        
        # Check trend conditions based on trade type
        if trade_type == 'long':
            # For long, we want an uptrend and positive momentum
            if pd.isna(df['sma20'].iloc[idx]) or pd.isna(df['sma50'].iloc[idx]) or pd.isna(df['roc'].iloc[idx]):
                return False
            if not (df['sma20'].iloc[idx] > df['sma50'].iloc[idx] and df['roc'].iloc[idx] > 0):
                return False
        else:  # short
            # For short, we want a downtrend and negative momentum
            if pd.isna(df['sma20'].iloc[idx]) or pd.isna(df['sma50'].iloc[idx]) or pd.isna(df['roc'].iloc[idx]):
                return False
            if not (df['sma20'].iloc[idx] < df['sma50'].iloc[idx] and df['roc'].iloc[idx] < 0):
                return False
        
        # Volatility check: skip trades during excessively volatile periods
        if pd.isna(df['atr'].iloc[idx]) or pd.isna(df['expanding_avg_atr'].iloc[idx]):
            return False
        current_atr = df['atr'].iloc[idx]
        avg_atr = df['expanding_avg_atr'].iloc[idx]
        if current_atr > avg_atr * 1.5:
            return False
        
        return True
    
    def detect_signal(self, df: pd.DataFrame, idx: int) -> dict:
        """
        Detect order block signal at current index
        
        Args:
            df: DataFrame with indicators
            idx: Current index
            
        Returns:
            Dictionary with signal information or None if no signal
        """
        if idx < 50:  # Need enough history for indicators
            return None
        
        pc = df['pc'].iloc[idx]
        prev_pc = df['pc'].iloc[idx-1]
        
        # Check for long signal
        if self.is_valid_trade_condition(df, idx, 'long') and (prev_pc < self.sensitivity and pc >= self.sensitivity):
            # Find the order block (bearish candle in last 4-16 bars)
            for j in range(idx - 4, max(idx - 16, -1), -1):
                if df['close'].iloc[j] < df['open'].iloc[j]:
                    ob_low = df['low'].iloc[j]
                    current_price = df['close'].iloc[idx]
                    
                    if current_price > ob_low:
                        self.last_trade_index = idx
                        return {
                            'type': 'long',
                            'entry_price': current_price,
                            'stop_loss': ob_low,
                            'timestamp': df['timestamp'].iloc[idx],
                            'ob_index': j
                        }
        
        # Check for short signal
        elif self.is_valid_trade_condition(df, idx, 'short') and (prev_pc > -self.sensitivity and pc <= -self.sensitivity):
            # Find the order block (bullish candle in last 4-16 bars)
            for j in range(idx - 4, max(idx - 16, -1), -1):
                if df['close'].iloc[j] > df['open'].iloc[j]:
                    ob_high = df['high'].iloc[j]
                    current_price = df['close'].iloc[idx]
                    
                    if current_price < ob_high:
                        self.last_trade_index = idx
                        return {
                            'type': 'short',
                            'entry_price': current_price,
                            'stop_loss': ob_high,
                            'timestamp': df['timestamp'].iloc[idx],
                            'ob_index': j
                        }
        
        return None


if __name__ == "__main__":
    # Test the strategy
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='3min')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 102,
        'low': np.random.randn(1000).cumsum() + 98,
        'close': np.random.randn(1000).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 1000)
    })
    
    strategy = OrderBlockStrategy()
    df = strategy.calculate_indicators(df)
    
    print("\nIndicators calculated:")
    print(df[['timestamp', 'close', 'pc', 'sma20', 'sma50', 'roc']].tail())
    
    # Test signal detection
    signals = []
    for i in range(50, len(df)):
        signal = strategy.detect_signal(df, i)
        if signal:
            signals.append(signal)
    
    print(f"\n✅ Detected {len(signals)} signals in test data")
