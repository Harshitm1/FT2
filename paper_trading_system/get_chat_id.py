#!/usr/bin/env python3
"""
Helper script to get your Telegram Chat ID
"""
import sys
import requests

def get_chat_id(bot_token):
    """Get chat ID from Telegram bot"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Error: {data.get('description', 'Unknown error')}")
            return None
        
        updates = data.get('result', [])
        
        if not updates:
            print("\n⚠️  No messages found!")
            print("\n📱 Please:")
            print("   1. Open Telegram")
            print("   2. Search for your bot: @FT_1305_bot")
            print("   3. Start a chat and send any message")
            print("   4. Run this script again")
            return None
        
        # Get the most recent chat
        latest_update = updates[-1]
        chat_id = latest_update['message']['chat']['id']
        
        print("\n" + "="*70)
        print("✅ CHAT ID FOUND!")
        print("="*70)
        print(f"\nYour Chat ID: {chat_id}")
        print("\n📝 Add this to your .env file:")
        print(f"\nTELEGRAM_ENABLED=true")
        print(f"TELEGRAM_BOT_TOKEN={bot_token}")
        print(f"TELEGRAM_CHAT_ID={chat_id}")
        print("\n" + "="*70 + "\n")
        
        return chat_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    bot_token = "7810438311:AAHs5m1v7jqNUA1LEcZiw2Qfp6LC1BsUyoY"
    
    print("\n" + "="*70)
    print("🤖 TELEGRAM CHAT ID FINDER")
    print("="*70)
    print(f"\nBot: @FT_1305_bot")
    print(f"Token: {bot_token[:20]}...")
    
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        print("🎉 Setup complete! You can now enable Telegram notifications.")
