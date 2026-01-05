"""
Test script to verify all components work correctly
"""
import logging
from datetime import datetime

from live_data_feed import LiveDataFeed
from orderblock_strategy import OrderBlockStrategy
from paper_trading_engine import PaperTradingEngine
import config

# Setup logging
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def test_data_feed():
    """Test live data feed"""
    print("\n" + "="*70)
    print("TEST 1: Live Data Feed")
    print("="*70)
    
    feed = LiveDataFeed()
    
    # Test historical data
    print("\n📊 Fetching 7 days of historical data...")
    df = feed.fetch_historical_data(days=7)
    print(f"✅ Fetched {len(df)} candles")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Test latest candle
    print("\n📊 Fetching latest candle...")
    latest = feed.fetch_latest_candle()
    if latest is not None:
        print(f"✅ Latest candle: {latest['timestamp']} | Close: ${latest['close']:.2f}")
    
    # Test current price
    print("\n📊 Fetching current price...")
    price = feed.get_current_price()
    if price:
        print(f"✅ Current price: ${price:.2f}")
    
    return df


def test_strategy(df):
    """Test order block strategy"""
    print("\n" + "="*70)
    print("TEST 2: Order Block Strategy")
    print("="*70)
    
    strategy = OrderBlockStrategy()
    
    # Calculate indicators
    print("\n📈 Calculating indicators...")
    df = strategy.calculate_indicators(df)
    print(f"✅ Indicators calculated")
    print(f"   Columns: {list(df.columns)}")
    
    # Detect signals
    print("\n🔍 Detecting signals...")
    signals = []
    for i in range(50, len(df)):
        signal = strategy.detect_signal(df, i)
        if signal:
            signals.append(signal)
    
    print(f"✅ Detected {len(signals)} signals in test data")
    if signals:
        print(f"   First signal: {signals[0]['type']} at ${signals[0]['entry_price']:.2f}")
    
    return signals


def test_paper_trading():
    """Test paper trading engine"""
    print("\n" + "="*70)
    print("TEST 3: Paper Trading Engine")
    print("="*70)
    
    engine = PaperTradingEngine(initial_capital=100)
    
    # Test opening a position
    print("\n🟢 Testing long position...")
    signal = {
        'type': 'long',
        'entry_price': 3000,
        'stop_loss': 2950,
        'timestamp': datetime.now()
    }
    
    position = engine.open_position(signal, datetime.now())
    print(f"✅ Position opened: {position['type']} at ${position['adj_entry_price']:.2f}")
    
    # Record equity
    engine.record_equity(datetime.now(), 3000)
    
    # Test price movement
    print("\n📈 Simulating price movement to $3050...")
    engine.update_position(3050, datetime.now())
    engine.record_equity(datetime.now(), 3050)
    
    # Close position
    print("\n🔴 Closing position...")
    trade = engine.close_position(3050, datetime.now(), 'manual')
    print(f"✅ Position closed: PnL ${trade['pnl']:.2f} ({trade['return_pct']:.2f}%)")
    
    # Test EMA calculation
    print("\n📊 Testing EMA calculation...")
    for i in range(200):
        engine.record_equity(datetime.now(), 3000 + i)
    
    ema = engine.calculate_ema_200()
    print(f"✅ EMA200 calculated: ${ema:.2f}")
    
    # Get stats
    stats = engine.get_stats()
    print(f"\n📈 Final Stats:")
    print(f"   Capital: ${stats['current_capital']:.2f}")
    print(f"   Return: {stats['total_return']:.2f}%")
    print(f"   Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']:.1f}%")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 PAPER TRADING SYSTEM - COMPONENT TESTS")
    print("="*70)
    print(f"Exchange: {config.EXCHANGE}")
    print(f"Symbol: {config.SYMBOL}")
    print(f"Timeframe: {config.TIMEFRAME}")
    print("="*70)
    
    try:
        # Test 1: Data Feed
        df = test_data_feed()
        
        # Test 2: Strategy
        signals = test_strategy(df)
        
        # Test 3: Paper Trading
        test_paper_trading()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\n🚀 System is ready to run!")
        print("   Execute: python forward_tester.py")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
