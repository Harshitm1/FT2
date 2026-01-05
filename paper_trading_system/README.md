# Paper Trading Forward Testing System

Real-time paper trading system for the EMA-filtered Order Block strategy.

## 🎯 Features

- **Live Data Feed**: Fetches real-time 3-minute candles from Binance or Delta Exchange India
- **Order Block Detection**: Identifies bullish/bearish order blocks with trend and volume filtering
- **Paper Trading**: Simulates trades with realistic slippage (0.05%) and commission (0.06%)
- **EMA200 Filter**: Only "takes" trades when equity curve is above its 200-period EMA
- **Equity Tracking**: Maintains complete equity history for analysis
- **Telegram Notifications**: Real-time alerts for all trading events (optional)
- **Comprehensive Logging**: All trades and system events logged to CSV files

## 📁 Project Structure

```
paper_trading_system/
├── config.py                 # Configuration settings
├── live_data_feed.py         # CCXT data fetcher
├── orderblock_strategy.py    # Order block detection logic
├── paper_trading_engine.py   # Paper trading simulation
├── forward_tester.py         # Main orchestrator
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── data/                    # Historical data cache
├── logs/                    # Trade and system logs
└── state/                   # System state persistence
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd paper_trading_system
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env to change exchange or symbol
```

Default settings:
- Exchange: Binance
- Symbol: ETH/USDT
- Timeframe: 3 minutes
- Initial Capital: $100

### 3. Run the Forward Tester

```bash
python forward_tester.py
```

The system will:
1. Fetch 1 year of historical data
2. Run backtest to build initial equity curve
3. Start monitoring live market data
4. Simulate trades based on order block signals
5. Apply EMA200 filter to determine which trades to "take"

### 4. Setup Telegram Notifications (Optional)

Get real-time alerts on your phone! See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for detailed instructions.

**Quick setup**:
1. Create bot with @BotFather on Telegram
2. Get your chat ID from @userinfobot
3. Add to `.env`:
   ```bash
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## 📊 Output Files

- `logs/trades.csv` - All completed trades with PnL
- `logs/equity.csv` - Equity curve history
- `logs/system.log` - System events and errors

## ⚙️ Configuration

Edit `config.py` or use environment variables:

```python
# Exchange Settings
EXCHANGE = 'binance'  # or 'delta'
SYMBOL = 'ETH/USDT'   # or 'ETHUSD' for Delta
TIMEFRAME = '3m'

# Trading Parameters
INITIAL_CAPITAL = 100.0
RISK_PER_TRADE = 0.02  # 2%
SLIPPAGE = 0.0005      # 0.05%
COMMISSION = 0.0006    # 0.06%

# Strategy Parameters
EMA_PERIOD = 200
HISTORICAL_DAYS = 365
```

## 🔍 Monitoring

The system logs detailed information for each candle:

```
======================================================================
📊 New Candle: 2026-01-05 23:30:00 | Price: $3250.50
======================================================================
🔔 Signal detected: LONG
   Entry: $3250.50 | SL: $3200.00
   Current Equity: $125.50
   EMA200: $120.00
   Filter: ✅ PASS (Equity > EMA)
🟢 Position opened: LONG
   Entry: $3251.12 | SL: $3200.00

📈 Current Stats:
   Capital: $125.50
   Total Return: 25.50%
   Trades: 15 | Win Rate: 53.3%
```

## 🛑 Stopping the System

Press `Ctrl+C` to gracefully shutdown. The system will:
- Close any open positions
- Save all state to files
- Print final statistics

## 📈 Performance Analysis

After running for a period, analyze results:

```python
import pandas as pd

# Load trades
trades = pd.read_csv('logs/trades.csv')
print(f"Total Trades: {len(trades)}")
print(f"Win Rate: {(trades['pnl'] > 0).mean() * 100:.1f}%")
print(f"Total PnL: ${trades['pnl'].sum():.2f}")

# Load equity curve
equity = pd.read_csv('logs/equity.csv')
equity['timestamp'] = pd.to_datetime(equity['timestamp'])
equity.plot(x='timestamp', y='equity', title='Equity Curve')
```

## 🚢 Railway Deployment

See `railway.json` for deployment configuration.

## ⚠️ Important Notes

- This is **PAPER TRADING ONLY** - no real money is used
- Designed to validate strategy in current market conditions
- Run for minimum 1-2 weeks to collect meaningful data
- Compare results to backtest to validate strategy performance

## 📝 License

MIT
