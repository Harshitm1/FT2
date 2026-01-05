"""
Main Forward Tester
Orchestrates the entire paper trading system
"""
import time
import logging
import signal
import sys
from datetime import datetime, time as dt_time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import config
from live_data_feed import LiveDataFeed
from orderblock_strategy import OrderBlockStrategy
from paper_trading_engine import PaperTradingEngine
from telegram_notifier import TelegramNotifier

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.SYSTEM_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForwardTester:
    """
    Main forward testing orchestrator
    """
    
    def __init__(self):
        """Initialize the forward tester"""
        self.running = False
        
        # Initialize components
        logger.info("Initializing Forward Tester...")
        self.data_feed = LiveDataFeed(
            exchange_name=config.EXCHANGE,
            symbol=config.SYMBOL,
            timeframe=config.TIMEFRAME
        )
        self.strategy = OrderBlockStrategy()
        self.engine = PaperTradingEngine()
        self.telegram = TelegramNotifier()
        
        # Data buffer
        self.df = None
        self.last_candle_time = None
        self.last_daily_summary = None  # Track last daily summary time
        
        logger.info("✅ Forward Tester initialized")
    
    def bootstrap_historical_data(self):
        """
        Load historical data to bootstrap the system
        """
        logger.info(f"📊 Bootstrapping with {config.HISTORICAL_DAYS} days of historical data...")
        
        # Fetch historical data
        self.df = self.data_feed.fetch_historical_data(days=config.HISTORICAL_DAYS)
        
        if self.df.empty:
            raise Exception("Failed to fetch historical data")
        
        # Calculate indicators
        logger.info("📈 Calculating indicators...")
        self.df = self.strategy.calculate_indicators(self.df)
        
        # Run initial backtest to build equity curve
        logger.info("🔄 Running initial backtest to build equity curve...")
        self._run_historical_backtest()
        
        # Set last candle time
        self.last_candle_time = self.df['timestamp'].iloc[-1]
        
        logger.info(f"✅ Bootstrap complete. Equity curve has {len(self.engine.equity_history)} points")
        logger.info(f"   Current capital: ${self.engine.capital:.2f}")
        logger.info(f"   EMA200: ${self.engine.ema_200:.2f}" if self.engine.ema_200 else "   EMA200: Not enough data")
    
    def _run_historical_backtest(self):
        """
        Run backtest on historical data to build initial equity curve
        """
        for i in range(50, len(self.df)):
            current_price = self.df['close'].iloc[i]
            timestamp = self.df['timestamp'].iloc[i]
            
            # Update existing position
            if self.engine.position is not None:
                closed_trade = self.engine.update_position(current_price, timestamp)
                if closed_trade:
                    logger.info(f"   Historical trade closed: {closed_trade['type']} PnL: ${closed_trade['pnl']:.2f}")
            
            # Check for new signals
            if self.engine.position is None:
                signal = self.strategy.detect_signal(self.df, i)
                if signal:
                    # Open position (no EMA filter during bootstrap)
                    self.engine.open_position(signal, timestamp)
            
            # Record equity
            self.engine.record_equity(timestamp, current_price)
    
    def process_new_candle(self, new_candle: pd.Series):
        """
        Process a new candle from live data
        
        Args:
            new_candle: New candle data
        """
        # Add new candle to dataframe
        self.df = pd.concat([self.df, new_candle.to_frame().T], ignore_index=True)
        
        # Recalculate indicators (only for recent data)
        self.df = self.strategy.calculate_indicators(self.df)
        
        current_idx = len(self.df) - 1
        current_price = self.df['close'].iloc[current_idx]
        timestamp = self.df['timestamp'].iloc[current_idx]
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 New Candle: {timestamp} | Price: ${current_price:.2f}")
        logger.info(f"{'='*70}")
        
        # Update existing position
        if self.engine.position is not None:
            logger.info(f"📍 Open {self.engine.position['type']} position from ${self.engine.position['adj_entry_price']:.2f}")
            closed_trade = self.engine.update_position(current_price, timestamp)
            
            if closed_trade:
                logger.info(f"🔴 Position closed: {closed_trade['exit_reason']}")
                logger.info(f"   PnL: ${closed_trade['pnl']:.2f} ({closed_trade['return_pct']:.2f}%)")
                self._log_trade(closed_trade)
                
                # Send Telegram notification
                self.telegram.send_position_closed(closed_trade)
        
        # Check for new signals
        if self.engine.position is None:
            signal = self.strategy.detect_signal(self.df, current_idx)
            
            if signal:
                logger.info(f"🔔 Signal detected: {signal['type'].upper()}")
                logger.info(f"   Entry: ${signal['entry_price']:.2f} | SL: ${signal['stop_loss']:.2f}")
                
                # Check EMA filter
                should_trade = self.engine.should_take_trade()
                current_equity = self.engine.get_current_equity(current_price)
                
                logger.info(f"   Current Equity: ${current_equity:.2f}")
                if self.engine.ema_200:
                    logger.info(f"   EMA200: ${self.engine.ema_200:.2f}")
                    logger.info(f"   Filter: {'✅ PASS' if should_trade else '❌ SKIP'} (Equity {'>' if should_trade else '<'} EMA)")
                else:
                    logger.info(f"   Filter: ✅ PASS (Not enough data for EMA)")
                
                # Send Telegram notification
                self.telegram.send_signal_detected(signal, current_equity, self.engine.ema_200, should_trade)
                
                if should_trade:
                    # Open position
                    position = self.engine.open_position(signal, timestamp)
                    if position:
                        logger.info(f"🟢 Position opened: {position['type'].upper()}")
                        logger.info(f"   Entry: ${position['adj_entry_price']:.2f} | SL: ${position['stop_loss']:.2f}")
                        
                        # Send Telegram notification
                        self.telegram.send_position_opened(position)
                else:
                    logger.info(f"⏭️  Trade skipped due to EMA filter")
        
        # Record equity
        self.engine.record_equity(timestamp, current_price)
        
        # Check if we should send daily summary (at 00:00 UTC)
        current_date = timestamp.date()
        if self.last_daily_summary is None or current_date > self.last_daily_summary:
            stats = self.engine.get_stats()
            current_equity = self.engine.get_current_equity(current_price)
            self.telegram.send_daily_summary(stats, current_equity, self.engine.ema_200)
            self.last_daily_summary = current_date
            logger.info("📊 Daily summary sent")
        
        # Log current stats
        stats = self.engine.get_stats()
        logger.info(f"\n📈 Current Stats:")
        logger.info(f"   Capital: ${stats['current_capital']:.2f}")
        logger.info(f"   Total Return: {stats['total_return']:.2f}%")
        logger.info(f"   Trades: {stats['total_trades']} | Win Rate: {stats['win_rate']:.1f}%")
        
        # Save state
        self._save_state()
    
    def _log_trade(self, trade: dict):
        """
        Log trade to CSV
        
        Args:
            trade: Trade dictionary
        """
        # Append to trades log
        trade_df = pd.DataFrame([trade])
        
        if config.TRADES_LOG.exists():
            trade_df.to_csv(config.TRADES_LOG, mode='a', header=False, index=False)
        else:
            trade_df.to_csv(config.TRADES_LOG, index=False)
    
    def _save_state(self):
        """Save current state to file"""
        # Save equity history
        equity_df = pd.DataFrame(self.engine.equity_history, columns=['timestamp', 'equity'])
        equity_df.to_csv(config.EQUITY_LOG, index=False)
        
        logger.debug("💾 State saved")
    
    def run(self):
        """
        Main run loop
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING FORWARD TESTER")
        logger.info("="*70)
        logger.info(f"Exchange: {config.EXCHANGE}")
        logger.info(f"Symbol: {config.SYMBOL}")
        logger.info(f"Timeframe: {config.TIMEFRAME}")
        logger.info(f"Initial Capital: ${config.INITIAL_CAPITAL}")
        logger.info("="*70 + "\n")
        
        # Bootstrap with historical data
        self.bootstrap_historical_data()
        
        # Send startup notification
        self.telegram.send_startup_message(config.EXCHANGE, config.SYMBOL, config.INITIAL_CAPITAL)
        
        # Start live trading loop
        self.running = True
        logger.info("\n🔴 LIVE TRADING MODE ACTIVATED")
        logger.info(f"Checking for new candles every {config.UPDATE_INTERVAL} seconds...\n")
        
        while self.running:
            try:
                # Fetch latest candle
                latest_candle = self.data_feed.fetch_latest_candle()
                
                if latest_candle is not None:
                    # Check if this is a new candle
                    if self.last_candle_time is None or latest_candle['timestamp'] > self.last_candle_time:
                        self.last_candle_time = latest_candle['timestamp']
                        self.process_new_candle(latest_candle)
                    else:
                        logger.debug(f"⏳ Waiting for new candle... (last: {self.last_candle_time})")
                
                # Wait for next update
                time.sleep(config.UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️  Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                time.sleep(config.RETRY_DELAY)
        
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("\n" + "="*70)
        logger.info("🛑 SHUTTING DOWN FORWARD TESTER")
        logger.info("="*70)
        
        # Close any open positions
        if self.engine.position is not None:
            current_price = self.data_feed.get_current_price()
            if current_price:
                closed_trade = self.engine.close_position(current_price, datetime.now(), 'shutdown')
                logger.info(f"Closed open position: PnL ${closed_trade['pnl']:.2f}")
        
        # Save final state
        self._save_state()
        
        # Print final stats
        stats = self.engine.get_stats()
        logger.info(f"\n📊 FINAL STATISTICS:")
        logger.info(f"   Initial Capital: ${config.INITIAL_CAPITAL:.2f}")
        logger.info(f"   Final Capital: ${stats['current_capital']:.2f}")
        logger.info(f"   Total Return: {stats['total_return']:.2f}%")
        logger.info(f"   Total Trades: {stats['total_trades']}")
        logger.info(f"   Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"   Total Commission: ${stats['total_commission']:.2f}")
        
        # Send shutdown notification
        self.telegram.send_shutdown(stats)
        
        logger.info("\n✅ Shutdown complete")
        logger.info("="*70 + "\n")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("\n⚠️  Shutdown signal received")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run forward tester
    tester = ForwardTester()
    tester.run()
