# Quick Render Deployment Guide

## Step 1: Push to GitHub

```bash
cd /Users/harshitmittal/Desktop/lstm2/paper_trading_system

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Paper trading system with Telegram notifications"

# Create a new repository on GitHub:
# 1. Go to https://github.com/new
# 2. Name it: paper-trading-system
# 3. Don't initialize with README (we already have files)
# 4. Click "Create repository"

# Then run (replace YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/paper-trading-system.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. **Go to**: https://render.com
2. **Sign up** with your GitHub account
3. Click **"New +"** → **"Web Service"**
4. Click **"Connect account"** to link GitHub (if not already)
5. **Select** your `paper-trading-system` repository
6. Render will auto-detect `render.yaml` configuration

## Step 3: Configure Environment Variables

In the Render dashboard, before deploying:

1. Go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add these **secret** variables:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `7810438311:AAHs5m1v7jqNUA1LEcZiw2Qfp6LC1BsUyoY` |
| `TELEGRAM_CHAT_ID` | `1099769493` |

## Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Check logs to see system starting

## Step 5: Verify

You should receive a Telegram message:
```
🚀 Paper Trading System Started

📊 Exchange: binance
💱 Symbol: ETH/USDT
💰 Capital: $100.00
```

---

## 📊 Monitoring

- **Logs**: View in Render dashboard → Logs tab
- **Telegram**: All trade notifications on your phone
- **Restart**: Automatic on failure

---

## 🔄 Updating the System

```bash
# Make changes to your code
git add .
git commit -m "Update configuration"
git push

# Render auto-deploys on push!
```

---

## ⚠️ Important Notes

- **Free tier**: 750 hours/month (enough for 24/7)
- **Sleep mode**: May sleep after 15 min inactivity
  - Your bot will wake up when needed
  - Or use UptimeRobot to keep it awake
- **Logs**: Download from Render dashboard periodically

---

You're all set! 🚀
