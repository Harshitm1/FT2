"""
Paper Trading Engine
Simulates trades in real-time with equity tracking and EMA filtering
"""
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """
    Paper trading engine that simulates trades and tracks equity
    """
    
    def __init__(self, initial_capital: float = None, slippage: float = None, commission: float = None):
        """
        Initialize paper trading engine
        
        Args:
            initial_capital: Starting capital
            slippage: Slippage percentage (e.g., 0.0005 for 0.05%)
            commission: Commission percentage per trade
        """
        self.initial_capital = initial_capital or config.INITIAL_CAPITAL
        self.slippage = slippage or config.SLIPPAGE
        self.commission = commission or config.COMMISSION
        
        # Trading state
        self.capital = self.initial_capital
        self.position = None  # Current open position
        self.equity_history = []  # List of (timestamp, equity) tuples
        self.trades = []  # List of completed trades
        
        # EMA filter state
        self.ema_200 = None
        
        logger.info(f"Initialized PaperTradingEngine with ${self.initial_capital} capital")
    
    def get_current_equity(self, current_price: float = None) -> float:
        """
        Get current equity (mark-to-market if position open)
        
        Args:
            current_price: Current market price for mark-to-market
            
        Returns:
            Current equity value
        """
        if self.position is None:
            return self.capital
        
        if current_price is None:
            return self.capital
        
        # Calculate unrealized P&L
        entry_price = self.position['adj_entry_price']
        position_size = self.position['position_size']
        
        if self.position['type'] == 'long':
            # For long, unrealized exit price includes slippage
            unrealized_exit_price = current_price * (1 - self.slippage)
            return_multiplier = unrealized_exit_price / entry_price
        else:  # short
            # For short, unrealized exit price includes slippage
            unrealized_exit_price = current_price * (1 + self.slippage)
            return_multiplier = entry_price / unrealized_exit_price
        
        # Calculate equity including unrealized P&L
        equity = self.position['entry_capital'] * return_multiplier - self.position['entry_commission']
        return equity
    
    def calculate_ema_200(self) -> Optional[float]:
        """
        Calculate 200-period EMA on equity curve
        
        Returns:
            Current EMA value or None if not enough data
        """
        if len(self.equity_history) < 200:
            return None
        
        # Extract equity values
        equity_values = [eq for _, eq in self.equity_history]
        
        # Calculate EMA
        df = pd.DataFrame({'equity': equity_values})
        ema = df['equity'].ewm(span=config.EMA_PERIOD, adjust=False).mean().iloc[-1]
        
        return ema
    
    def should_take_trade(self) -> bool:
        """
        Check if we should take a trade based on EMA filter
        
        Returns:
            True if equity > EMA200 (or if not enough data for EMA)
        """
        self.ema_200 = self.calculate_ema_200()
        
        if self.ema_200 is None:
            # Not enough data for EMA, take all trades initially
            return True
        
        current_equity = self.get_current_equity()
        return current_equity > self.ema_200
    
    def open_position(self, signal: Dict, timestamp: datetime) -> Dict:
        """
        Open a new position based on signal
        
        Args:
            signal: Signal dictionary from strategy
            timestamp: Current timestamp
            
        Returns:
            Dictionary with trade details
        """
        if self.position is not None:
            logger.warning("Attempted to open position while one is already open")
            return None
        
        trade_type = signal['type']
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        
        # Apply slippage to entry
        if trade_type == 'long':
            adj_entry_price = entry_price * (1 + self.slippage)
            # Validate stop loss
            if adj_entry_price <= stop_loss:
                logger.warning(f"Invalid long trade: entry {adj_entry_price} <= SL {stop_loss}")
                return None
        else:  # short
            adj_entry_price = entry_price * (1 - self.slippage)
            # Validate stop loss
            if adj_entry_price >= stop_loss:
                logger.warning(f"Invalid short trade: entry {adj_entry_price} >= SL {stop_loss}")
                return None
        
        # Calculate position size (using full capital with 1x leverage)
        position_size = self.capital / adj_entry_price
        
        # Calculate entry commission
        entry_commission = position_size * adj_entry_price * self.commission
        
        # Deduct entry commission from capital
        capital_after_commission = self.capital - entry_commission
        
        # Calculate stop loss percentage and trailing stop
        if trade_type == 'long':
            sl_percentage = (adj_entry_price - stop_loss) / adj_entry_price
        else:
            sl_percentage = (stop_loss - adj_entry_price) / adj_entry_price
        
        trailing_stop_pct = sl_percentage * 0.75
        
        # Create position
        self.position = {
            'type': trade_type,
            'entry_price': entry_price,
            'adj_entry_price': adj_entry_price,
            'entry_time': timestamp,
            'entry_capital': self.capital,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'sl_percentage': sl_percentage,
            'trailing_stop_pct': trailing_stop_pct,
            'entry_commission': entry_commission
        }
        
        # Update capital
        self.capital = capital_after_commission
        
        logger.info(f"Opened {trade_type} position at ${adj_entry_price:.2f}, SL: ${stop_loss:.2f}")
        
        return self.position.copy()
    
    def update_position(self, current_price: float, timestamp: datetime) -> Optional[Dict]:
        """
        Update position and check for exit conditions
        
        Args:
            current_price: Current market price
            timestamp: Current timestamp
            
        Returns:
            Completed trade dictionary if position closed, None otherwise
        """
        if self.position is None:
            return None
        
        # Update trailing stop
        if self.position['type'] == 'long':
            trail_price = current_price * (1 - self.position['trailing_stop_pct'])
            if trail_price > self.position['stop_loss']:
                self.position['stop_loss'] = trail_price
            
            # Check if stop loss hit
            if current_price <= self.position['stop_loss']:
                return self.close_position(self.position['stop_loss'], timestamp, 'stop_loss')
        
        else:  # short
            trail_price = current_price * (1 + self.position['trailing_stop_pct'])
            if trail_price < self.position['stop_loss']:
                self.position['stop_loss'] = trail_price
            
            # Check if stop loss hit
            if current_price >= self.position['stop_loss']:
                return self.close_position(self.position['stop_loss'], timestamp, 'stop_loss')
        
        return None
    
    def close_position(self, exit_price: float, timestamp: datetime, reason: str = 'manual') -> Dict:
        """
        Close current position
        
        Args:
            exit_price: Exit price
            timestamp: Exit timestamp
            reason: Reason for exit
            
        Returns:
            Completed trade dictionary
        """
        if self.position is None:
            logger.warning("Attempted to close position when none is open")
            return None
        
        # Apply slippage to exit
        if self.position['type'] == 'long':
            adj_exit_price = exit_price * (1 - self.slippage)
            return_multiplier = adj_exit_price / self.position['adj_entry_price']
        else:  # short
            adj_exit_price = exit_price * (1 + self.slippage)
            return_multiplier = self.position['adj_entry_price'] / adj_exit_price
        
        # Calculate capital after price movement
        capital_after_slippage = self.position['entry_capital'] * return_multiplier
        
        # Calculate exit commission
        exit_commission = self.position['position_size'] * adj_exit_price * self.commission
        total_commission = self.position['entry_commission'] + exit_commission
        
        # Final capital after all costs
        final_capital = capital_after_slippage - exit_commission
        pnl = final_capital - self.position['entry_capital']
        
        # Update capital
        self.capital = final_capital
        
        # Create completed trade record
        trade = {
            **self.position,
            'exit_price': adj_exit_price,
            'exit_time': timestamp,
            'exit_capital': final_capital,
            'pnl': pnl,
            'return_pct': (pnl / self.position['entry_capital']) * 100,
            'return_multiplier': return_multiplier,
            'commission': total_commission,
            'exit_reason': reason
        }
        
        self.trades.append(trade)
        self.position = None
        
        logger.info(f"Closed {trade['type']} position at ${adj_exit_price:.2f}, PnL: ${pnl:.2f} ({trade['return_pct']:.2f}%)")
        
        return trade
    
    def record_equity(self, timestamp: datetime, current_price: float = None):
        """
        Record current equity to history
        
        Args:
            timestamp: Current timestamp
            current_price: Current price for mark-to-market
        """
        equity = self.get_current_equity(current_price)
        self.equity_history.append((timestamp, equity))
    
    def get_stats(self) -> Dict:
        """
        Get current trading statistics
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'current_capital': self.capital
            }
        
        trades_df = pd.DataFrame(self.trades)
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] < 0]
        
        return {
            'total_trades': len(self.trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(self.trades) * 100 if self.trades else 0,
            'avg_win': wins['pnl'].mean() if not wins.empty else 0,
            'avg_loss': losses['pnl'].mean() if not losses.empty else 0,
            'total_return': ((self.capital - self.initial_capital) / self.initial_capital) * 100,
            'current_capital': self.capital,
            'total_commission': trades_df['commission'].sum() if 'commission' in trades_df.columns else 0
        }


if __name__ == "__main__":
    # Test the paper trading engine
    logging.basicConfig(level=logging.INFO)
    
    engine = PaperTradingEngine(initial_capital=100)
    
    # Simulate some trades
    print("\n" + "="*70)
    print("Testing Paper Trading Engine")
    print("="*70)
    
    # Test long trade
    signal = {
        'type': 'long',
        'entry_price': 3000,
        'stop_loss': 2950,
        'timestamp': datetime.now()
    }
    
    engine.open_position(signal, datetime.now())
    engine.record_equity(datetime.now(), 3000)
    
    # Simulate price movement
    engine.update_position(3050, datetime.now())
    engine.record_equity(datetime.now(), 3050)
    
    # Close position
    engine.close_position(3050, datetime.now(), 'manual')
    engine.record_equity(datetime.now(), 3050)
    
    # Print stats
    stats = engine.get_stats()
    print("\n📊 Performance Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Test complete. Final capital: ${engine.capital:.2f}")
