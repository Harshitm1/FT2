# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))

---

## Step 1: Push Code to GitHub

```bash
cd /Users/harshitmittal/Desktop/lstm2/paper_trading_system

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Paper trading forward testing system"

# Create GitHub repository and push
# (Replace with your GitHub username and repo name)
git remote add origin https://github.com/YOUR_USERNAME/paper-trading-system.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Railway

### Option A: Deploy from GitHub (Recommended)

1. **Go to Railway**: https://railway.app
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `paper-trading-system`
5. **Railway auto-detects** `railway.json` and configures deployment

### Option B: Deploy with Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## Step 3: Configure Environment Variables (Optional)

In Railway dashboard, add these if you want to customize:

| Variable | Default | Options |
|----------|---------|---------|
| `EXCHANGE` | `binance` | `binance`, `delta` |
| `SYMBOL` | `ETH/USDT` | Any valid pair |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING` |
| `TELEGRAM_ENABLED` | `false` | `true`, `false` |

**Note**: No API keys needed for paper trading! System uses public data only.

---

## Step 4: Monitor Your Deployment

### View Logs
- Go to Railway dashboard
- Click on your project
- View **Logs** tab for real-time output

### Expected Logs
```
🚀 STARTING FORWARD TESTER
Exchange: binance
Symbol: ETH/USDT
Initial Capital: $100

📊 Bootstrapping with 365 days of historical data...
✅ Bootstrap complete. Equity curve has 175000 points
   Current capital: $254.16
   EMA200: $220.50

🔴 LIVE TRADING MODE ACTIVATED
```

### Download Trade Data

Railway provides persistent storage. To download your logs:

1. **Using Railway CLI**:
```bash
railway run cat logs/trades.csv > trades_backup.csv
railway run cat logs/equity.csv > equity_backup.csv
```

2. **Using Railway Dashboard**:
- Go to **Variables** tab
- Add a volume mount (if not auto-configured)
- Access files through Railway shell

---

## Step 5: Monitor Performance

### Check System Status

Railway dashboard shows:
- ✅ **Deployment Status**: Running/Stopped
- 📊 **Resource Usage**: CPU, Memory
- 📝 **Recent Logs**: Last 100 lines
- ⏱️ **Uptime**: How long it's been running

### Analyze Results (After 1-2 Weeks)

```bash
# Download logs
railway run cat logs/trades.csv > trades.csv
railway run cat logs/equity.csv > equity.csv

# Analyze in Python
python analyze_results.py
```

---

## 📊 What Happens on Railway

### Automatic Processes

1. **Startup** (takes ~2-3 minutes):
   - Installs dependencies from `requirements.txt`
   - Runs `forward_tester.py`
   - Fetches 1 year historical data
   - Builds initial equity curve

2. **Live Operation**:
   - Checks for new candles every 3 minutes
   - Detects order block signals
   - Applies EMA filter
   - Logs all trades to CSV
   - Runs 24/7 automatically

3. **Auto-Restart**:
   - If crash occurs, Railway restarts automatically
   - Max 10 retries (configured in `railway.json`)
   - State is preserved in log files

---

## 🛠️ Troubleshooting

### Issue: Deployment Failed

**Check**:
- `requirements.txt` is present
- `railway.json` is valid JSON
- Python version compatible (3.8+)

**Fix**: View deployment logs in Railway dashboard

### Issue: No Trades Logged

**Possible Reasons**:
1. Equity < EMA200 (filter blocking trades)
2. No order block signals in current market
3. Trend/volume filters blocking trades

**Check**: View logs for "Signal detected" and "Filter: SKIP" messages

### Issue: High Memory Usage

**Solution**: Railway provides sufficient resources, but if needed:
- Reduce `HISTORICAL_DAYS` from 365 to 180
- System will use less memory for bootstrap

---

## 💰 Railway Pricing

- **Free Tier**: $5 credit/month (sufficient for this app)
- **Usage**: ~$0.01-0.02/day for this system
- **Estimate**: Can run ~250 days on free tier

---

## 📥 Downloading Results

### Method 1: Railway CLI

```bash
# Download all logs
railway run tar -czf logs.tar.gz logs/
railway run cat logs.tar.gz > logs_backup.tar.gz
tar -xzf logs_backup.tar.gz
```

### Method 2: Add Download Endpoint (Optional)

I can add a simple web endpoint to download logs via browser if you want.

---

## 🔄 Updating the System

```bash
# Make changes locally
git add .
git commit -m "Update configuration"
git push

# Railway auto-deploys on push
```

---

## 📊 Expected Results

After **1 week** of running:
- ~3,360 candles processed (7 days × 480 candles/day)
- ~50-100 order block signals detected
- ~20-40 trades "taken" (after EMA filter)
- Complete equity curve for analysis

After **2 weeks**:
- Enough data to compare with backtest
- Can validate if EMA filter is working as expected
- Ready to make decision on real trading

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Deployment successful (check logs)
- [ ] System bootstrapped (1 year data loaded)
- [ ] Live trading mode activated
- [ ] First candle processed successfully
- [ ] Logs being written to files

---

## 🎯 Next Steps After Deployment

1. **Monitor for 24 hours** - Ensure no crashes
2. **Check logs daily** - Review trades and signals
3. **Download data weekly** - Backup trade history
4. **Analyze after 2 weeks** - Compare to backtest
5. **Decide on real trading** - Based on forward test results

---

## 📞 Support

If you encounter issues:
1. Check Railway logs first
2. Review `logs/system.log` for errors
3. Verify exchange API is accessible
4. Check if market is open (for Delta Exchange)

The system is designed to run autonomously on Railway 24/7! 🚀
