"""
Telegram Notifications Module
Sends real-time alerts for trades and system events
"""
import logging
from typing import Optional
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Sends notifications via Telegram bot
    """
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.enabled = config.TELEGRAM_ENABLED
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        
        if self.enabled and self.bot_token and self.chat_id:
            self.bot = Bot(token=self.bot_token)
            logger.info("✅ Telegram notifications enabled")
        else:
            self.bot = None
            logger.info("ℹ️  Telegram notifications disabled")
    
    def _send_sync(self, message: str):
        """
        Send message synchronously (for use in sync context)
        
        Args:
            message: Message to send
        """
        if not self.enabled or not self.bot:
            return
        
        try:
            # Run async send in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            ))
            loop.close()
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def send_startup_message(self, exchange: str, symbol: str, capital: float):
        """
        Send system startup notification
        
        Args:
            exchange: Exchange name
            symbol: Trading symbol
            capital: Initial capital
        """
        message = (
            "🚀 <b>Paper Trading System Started</b>\n\n"
            f"📊 Exchange: {exchange}\n"
            f"💱 Symbol: {symbol}\n"
            f"💰 Capital: ${capital:.2f}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "System is now monitoring live market data..."
        )
        self._send_sync(message)
    
    def send_signal_detected(self, signal: dict, equity: float, ema: Optional[float], will_trade: bool):
        """
        Send signal detection notification
        
        Args:
            signal: Signal dictionary
            equity: Current equity
            ema: Current EMA200 value
            will_trade: Whether trade will be executed
        """
        signal_type = signal['type'].upper()
        emoji = "🟢" if signal_type == "LONG" else "🔴"
        
        message = (
            f"{emoji} <b>Signal Detected: {signal_type}</b>\n\n"
            f"💵 Entry: ${signal['entry_price']:.2f}\n"
            f"🛑 Stop Loss: ${signal['stop_loss']:.2f}\n"
            f"⏰ Time: {signal['timestamp'].strftime('%H:%M:%S')}\n\n"
            f"📊 Current Equity: ${equity:.2f}\n"
        )
        
        if ema:
            message += f"📈 EMA200: ${ema:.2f}\n"
        
        if will_trade:
            message += "\n✅ <b>Trade will be executed</b>"
        else:
            message += "\n⏭️ <b>Trade skipped</b> (Equity < EMA200)"
        
        self._send_sync(message)
    
    def send_position_opened(self, position: dict):
        """
        Send position opened notification
        
        Args:
            position: Position dictionary
        """
        pos_type = position['type'].upper()
        emoji = "🟢" if pos_type == "LONG" else "🔴"
        
        message = (
            f"{emoji} <b>Position Opened: {pos_type}</b>\n\n"
            f"💵 Entry: ${position['adj_entry_price']:.2f}\n"
            f"🛑 Stop Loss: ${position['stop_loss']:.2f}\n"
            f"📊 Position Size: {position['position_size']:.4f}\n"
            f"💰 Capital: ${position['entry_capital']:.2f}\n"
            f"⏰ Time: {position['entry_time'].strftime('%H:%M:%S')}\n"
        )
        self._send_sync(message)
    
    def send_position_closed(self, trade: dict):
        """
        Send position closed notification
        
        Args:
            trade: Completed trade dictionary
        """
        is_win = trade['pnl'] > 0
        emoji = "✅" if is_win else "❌"
        
        message = (
            f"{emoji} <b>Position Closed: {trade['type'].upper()}</b>\n\n"
            f"💵 Entry: ${trade['adj_entry_price']:.2f}\n"
            f"💵 Exit: ${trade['exit_price']:.2f}\n"
            f"📊 PnL: ${trade['pnl']:.2f} ({trade['return_pct']:+.2f}%)\n"
            f"💰 New Capital: ${trade['exit_capital']:.2f}\n"
            f"🔍 Reason: {trade['exit_reason']}\n"
            f"⏰ Duration: {(trade['exit_time'] - trade['entry_time']).total_seconds() / 60:.0f} min\n"
        )
        self._send_sync(message)
    
    def send_daily_summary(self, stats: dict, equity: float, ema: Optional[float]):
        """
        Send daily performance summary
        
        Args:
            stats: Performance statistics
            equity: Current equity
            ema: Current EMA200
        """
        message = (
            "📊 <b>Daily Summary</b>\n\n"
            f"💰 Current Capital: ${stats['current_capital']:.2f}\n"
            f"📈 Total Return: {stats['total_return']:.2f}%\n\n"
            f"📊 Trades: {stats['total_trades']}\n"
            f"✅ Wins: {stats['wins']} | ❌ Losses: {stats['losses']}\n"
            f"🎯 Win Rate: {stats['win_rate']:.1f}%\n\n"
        )
        
        if stats['total_trades'] > 0:
            message += (
                f"💵 Avg Win: ${stats['avg_win']:.2f}\n"
                f"💵 Avg Loss: ${stats['avg_loss']:.2f}\n"
                f"💸 Total Commission: ${stats['total_commission']:.2f}\n\n"
            )
        
        if ema:
            filter_status = "✅ ACTIVE" if equity > ema else "⏸️ PAUSED"
            message += (
                f"📈 Current Equity: ${equity:.2f}\n"
                f"📈 EMA200: ${ema:.2f}\n"
                f"🔍 Filter Status: {filter_status}\n"
            )
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_sync(message)
    
    def send_error(self, error_msg: str):
        """
        Send error notification
        
        Args:
            error_msg: Error message
        """
        message = (
            "⚠️ <b>System Error</b>\n\n"
            f"{error_msg}\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_sync(message)
    
    def send_shutdown(self, final_stats: dict):
        """
        Send system shutdown notification
        
        Args:
            final_stats: Final performance statistics
        """
        message = (
            "🛑 <b>System Shutdown</b>\n\n"
            f"💰 Final Capital: ${final_stats['current_capital']:.2f}\n"
            f"📈 Total Return: {final_stats['total_return']:.2f}%\n"
            f"📊 Total Trades: {final_stats['total_trades']}\n"
            f"🎯 Win Rate: {final_stats['win_rate']:.1f}%\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_sync(message)


if __name__ == "__main__":
    # Test Telegram notifications
    import os
    
    print("\n" + "="*70)
    print("🧪 TELEGRAM NOTIFIER TEST")
    print("="*70)
    
    # Check if credentials are set
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("\n⚠️  Telegram credentials not set")
        print("\nTo test, set environment variables:")
        print("  export TELEGRAM_ENABLED=true")
        print("  export TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  export TELEGRAM_CHAT_ID=your_chat_id")
        print("\nSee TELEGRAM_SETUP.md for instructions")
    else:
        notifier = TelegramNotifier()
        
        print("\n📤 Sending test message...")
        notifier.send_startup_message('binance', 'ETH/USDT', 100.0)
        print("✅ Test message sent!")
        print("\nCheck your Telegram to verify delivery")
    
    print("\n" + "="*70 + "\n")
