"""
Simple analysis script for forward test results
Run this locally after downloading logs from Railway
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_trades():
    """Analyze trade results"""
    trades_file = Path('logs/trades.csv')
    
    if not trades_file.exists():
        print("❌ No trades.csv found. Download from Railway first.")
        return
    
    trades = pd.read_csv(trades_file)
    
    print("\n" + "="*70)
    print("📊 FORWARD TEST RESULTS ANALYSIS")
    print("="*70)
    
    print(f"\n📈 Overall Performance:")
    print(f"   Total Trades: {len(trades)}")
    
    if len(trades) > 0:
        wins = trades[trades['pnl'] > 0]
        losses = trades[trades['pnl'] < 0]
        
        print(f"   Wins: {len(wins)} | Losses: {len(losses)}")
        print(f"   Win Rate: {len(wins)/len(trades)*100:.1f}%")
        print(f"   Total PnL: ${trades['pnl'].sum():.2f}")
        print(f"   Avg Win: ${wins['pnl'].mean():.2f}" if not wins.empty else "   Avg Win: $0.00")
        print(f"   Avg Loss: ${losses['pnl'].mean():.2f}" if not losses.empty else "   Avg Loss: $0.00")
        
        # Calculate final capital
        initial_capital = trades['entry_capital'].iloc[0]
        final_capital = trades['exit_capital'].iloc[-1]
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        print(f"\n💰 Capital:")
        print(f"   Initial: ${initial_capital:.2f}")
        print(f"   Final: ${final_capital:.2f}")
        print(f"   Total Return: {total_return:.2f}%")
        
        # Trade distribution
        print(f"\n📊 Trade Distribution:")
        print(f"   Long Trades: {len(trades[trades['type']=='long'])}")
        print(f"   Short Trades: {len(trades[trades['type']=='short'])}")
        
        # Time analysis
        trades['entry_time'] = pd.to_datetime(trades['entry_time'])
        trades['exit_time'] = pd.to_datetime(trades['exit_time'])
        trades['duration'] = (trades['exit_time'] - trades['entry_time']).dt.total_seconds() / 60
        
        print(f"\n⏱️  Trade Duration:")
        print(f"   Avg Duration: {trades['duration'].mean():.1f} minutes")
        print(f"   Min Duration: {trades['duration'].min():.1f} minutes")
        print(f"   Max Duration: {trades['duration'].max():.1f} minutes")


def analyze_equity():
    """Analyze equity curve"""
    equity_file = Path('logs/equity.csv')
    
    if not equity_file.exists():
        print("\n❌ No equity.csv found. Download from Railway first.")
        return
    
    equity = pd.read_csv(equity_file)
    equity['timestamp'] = pd.to_datetime(equity['timestamp'])
    
    print("\n" + "="*70)
    print("📈 EQUITY CURVE ANALYSIS")
    print("="*70)
    
    print(f"\n📊 Equity Statistics:")
    print(f"   Data Points: {len(equity)}")
    print(f"   Start Date: {equity['timestamp'].min()}")
    print(f"   End Date: {equity['timestamp'].max()}")
    print(f"   Duration: {(equity['timestamp'].max() - equity['timestamp'].min()).days} days")
    
    # Calculate drawdown
    equity['peak'] = equity['equity'].expanding().max()
    equity['drawdown'] = (equity['equity'] - equity['peak']) / equity['peak'] * 100
    max_drawdown = equity['drawdown'].min()
    
    print(f"\n📉 Risk Metrics:")
    print(f"   Max Drawdown: {max_drawdown:.2f}%")
    print(f"   Current Equity: ${equity['equity'].iloc[-1]:.2f}")
    print(f"   Peak Equity: ${equity['peak'].iloc[-1]:.2f}")
    
    # Plot equity curve
    plt.figure(figsize=(15, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(equity['timestamp'], equity['equity'], label='Equity', linewidth=2)
    plt.plot(equity['timestamp'], equity['peak'], label='Peak', linestyle='--', alpha=0.5)
    plt.title('Equity Curve', fontsize=14, fontweight='bold')
    plt.ylabel('Equity ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.fill_between(equity['timestamp'], equity['drawdown'], 0, alpha=0.3, color='red')
    plt.plot(equity['timestamp'], equity['drawdown'], color='red', linewidth=2)
    plt.title('Drawdown', fontsize=14, fontweight='bold')
    plt.ylabel('Drawdown (%)')
    plt.xlabel('Date')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('equity_analysis.png', dpi=150)
    print(f"\n💾 Chart saved to: equity_analysis.png")


def compare_to_backtest():
    """Compare forward test to backtest results"""
    print("\n" + "="*70)
    print("🔍 BACKTEST vs FORWARD TEST COMPARISON")
    print("="*70)
    
    # Backtest results (from ema_filtered_backtest.py)
    backtest = {
        'return': 365.07,
        'trades': 729,
        'win_rate': 43.5,
        'avg_pnl': 0.50
    }
    
    trades_file = Path('logs/trades.csv')
    if not trades_file.exists():
        print("\n⚠️  No forward test data yet")
        return
    
    trades = pd.read_csv(trades_file)
    
    if len(trades) == 0:
        print("\n⚠️  No trades completed yet")
        return
    
    # Forward test results
    initial = trades['entry_capital'].iloc[0]
    final = trades['exit_capital'].iloc[-1]
    forward_return = (final - initial) / initial * 100
    forward_win_rate = (trades['pnl'] > 0).mean() * 100
    
    print(f"\n📊 Comparison:")
    print(f"   {'Metric':<20} {'Backtest':<15} {'Forward Test':<15} {'Difference'}")
    print(f"   {'-'*70}")
    print(f"   {'Total Return':<20} {backtest['return']:.2f}%{'':<10} {forward_return:.2f}%{'':<10} {forward_return - backtest['return']:+.2f}%")
    print(f"   {'Win Rate':<20} {backtest['win_rate']:.1f}%{'':<10} {forward_win_rate:.1f}%{'':<10} {forward_win_rate - backtest['win_rate']:+.1f}%")
    print(f"   {'Total Trades':<20} {backtest['trades']:<15} {len(trades):<15}")
    
    print(f"\n💡 Insights:")
    if abs(forward_win_rate - backtest['win_rate']) < 5:
        print("   ✅ Win rate is consistent with backtest")
    else:
        print("   ⚠️  Win rate differs from backtest - may need more data")
    
    if len(trades) < 50:
        print("   ⏳ Not enough trades yet for statistical significance")
    else:
        print("   ✅ Sufficient trades for initial validation")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔬 FORWARD TEST ANALYSIS TOOL")
    print("="*70)
    
    analyze_trades()
    analyze_equity()
    compare_to_backtest()
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70 + "\n")
