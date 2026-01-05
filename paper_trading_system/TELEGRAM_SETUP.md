# Telegram Bot Setup Guide

## 🤖 Creating Your Telegram Bot

### Step 1: Create Bot with BotFather

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send command**: `/newbot`
4. **Choose a name**: e.g., "My Paper Trading Bot"
5. **Choose a username**: e.g., "my_paper_trading_bot" (must end with 'bot')
6. **Copy the token**: BotFather will give you a token like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Step 2: Get Your Chat ID

**Option A: Using a Bot**
1. Search for `@userinfobot` in Telegram
2. Start a chat with it
3. It will send you your chat ID (a number like `123456789`)

**Option B: Manual Method**
1. Send a message to your bot (the one you just created)
2. Visit this URL in browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` in the response
4. Copy that ID number

---

## 🔧 Configure the System

### For Local Testing

Create a `.env` file:
```bash
cd paper_trading_system
cp .env.example .env
```

Edit `.env` and add:
```bash
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### For Railway Deployment

In Railway dashboard:
1. Go to your project
2. Click **Variables** tab
3. Add these environment variables:
   - `TELEGRAM_ENABLED` = `true`
   - `TELEGRAM_BOT_TOKEN` = `your_bot_token_here`
   - `TELEGRAM_CHAT_ID` = `your_chat_id_here`

---

## 🧪 Test Telegram Integration

```bash
# Set environment variables
export TELEGRAM_ENABLED=true
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id

# Run test
python telegram_notifier.py
```

You should receive a test message on Telegram!

---

## 📱 What Notifications You'll Receive

### 1. System Startup
```
🚀 Paper Trading System Started

📊 Exchange: binance
💱 Symbol: ETH/USDT
💰 Capital: $100.00
⏰ Time: 2026-01-05 23:30:00

System is now monitoring live market data...
```

### 2. Signal Detected
```
🟢 Signal Detected: LONG

💵 Entry: $3250.50
🛑 Stop Loss: $3200.00
⏰ Time: 23:33:00

📊 Current Equity: $125.50
📈 EMA200: $120.00

✅ Trade will be executed
```

### 3. Position Opened
```
🟢 Position Opened: LONG

💵 Entry: $3250.66
🛑 Stop Loss: $3200.00
📊 Position Size: 0.0386
💰 Capital: $125.50
⏰ Time: 23:33:00
```

### 4. Position Closed
```
✅ Position Closed: LONG

💵 Entry: $3250.66
💵 Exit: $3298.50
📊 PnL: $1.85 (+1.47%)
💰 New Capital: $127.35
🔍 Reason: stop_loss
⏰ Duration: 45 min
```

### 5. Daily Summary (Sent at 00:00 UTC)
```
📊 Daily Summary

💰 Current Capital: $127.35
📈 Total Return: 27.35%

📊 Trades: 15
✅ Wins: 8 | ❌ Losses: 7
🎯 Win Rate: 53.3%

💵 Avg Win: $2.50
💵 Avg Loss: $-1.20
💸 Total Commission: $0.45

📈 Current Equity: $127.35
📈 EMA200: $120.50
🔍 Filter Status: ✅ ACTIVE

⏰ 2026-01-06 00:00:00
```

### 6. Errors (if any)
```
⚠️ System Error

Failed to fetch latest candle: Connection timeout

⏰ 2026-01-05 23:45:00
```

---

## 🔕 Disable Notifications

### Temporarily
Set in `.env` or Railway variables:
```bash
TELEGRAM_ENABLED=false
```

### Permanently
Remove the environment variables or leave them empty.

---

## 🔒 Security Notes

- **Never commit** your bot token to git (it's in `.gitignore`)
- **Keep your token private** - anyone with it can control your bot
- If token is compromised, use BotFather to generate a new one (`/revoke`)

---

## 🐛 Troubleshooting

### "Unauthorized" Error
- Check your bot token is correct
- Make sure you've started a chat with your bot first

### "Chat not found" Error
- Verify your chat ID is correct
- Send a message to your bot before running the system

### No Messages Received
- Check `TELEGRAM_ENABLED=true` is set
- Verify both token and chat ID are correct
- Check Railway logs for Telegram errors

---

## 📊 Notification Frequency

- **Startup**: Once when system starts
- **Signals**: Every time an order block is detected
- **Positions**: When opened/closed
- **Daily Summary**: Once per day at 00:00 UTC
- **Errors**: As they occur

You can customize notification frequency in `telegram_notifier.py` if needed.

---

Your Telegram bot is now ready to keep you updated 24/7! 📱
