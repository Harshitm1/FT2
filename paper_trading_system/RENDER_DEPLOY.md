# Render.com Deployment Guide

## 🚀 Deploy to Render (Free)

Render.com offers a generous free tier perfect for this application.

### Step 1: Push to GitHub

```bash
cd /Users/harshitmittal/Desktop/lstm2/paper_trading_system

# Initialize git (if not done)
git init
git add .
git commit -m "Paper trading system"

# Create GitHub repo and push
# (Create repo on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/paper-trading-system.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to**: https://render.com
2. **Sign up** with GitHub
3. **New** → **Web Service**
4. **Connect** your GitHub repository
5. Render auto-detects `render.yaml`

### Step 3: Add Telegram Credentials

In Render dashboard:
1. Go to **Environment** tab
2. Add secret environment variables:
   - `TELEGRAM_BOT_TOKEN` = `7810438311:AAHs5m1v7jqNUA1LEcZiw2Qfp6LC1BsUyoY`
   - `TELEGRAM_CHAT_ID` = `1099769493`

### Step 4: Deploy

Click **Deploy** and wait ~2-3 minutes.

---

## 📊 Monitoring

- **Logs**: View in Render dashboard
- **Telegram**: Get notifications on your phone
- **Restart**: Auto-restarts on failure

---

## 💰 Free Tier Limits

- **Hours**: 750 hours/month (31 days = 744 hours) ✅
- **Memory**: 512 MB (sufficient)
- **Bandwidth**: 100 GB/month (more than enough)
- **Sleep**: Service sleeps after 15 min inactivity
  - **Solution**: Add a keep-alive ping (optional)

---

## 🔄 Keep Service Awake (Optional)

If Render puts your service to sleep, add this to `forward_tester.py`:

```python
# At the top
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# In __main__:
threading.Thread(target=run_flask, daemon=True).start()
```

Then use a service like UptimeRobot to ping your service every 5 minutes.

---

## ✅ Advantages Over Railway

- ✅ Truly free (no credit card required initially)
- ✅ 750 hours/month (enough for 24/7)
- ✅ Easy GitHub integration
- ✅ Auto-deploy on push
- ✅ Good logging interface

---

Your system will run 24/7 and send you Telegram notifications! 🎉
