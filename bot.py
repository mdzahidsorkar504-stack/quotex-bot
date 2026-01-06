from flask import Flask
import threading
import telebot
import pandas as pd
import pandas_ta as ta
import yfinance as download
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import time

# --- Render Port Error ঠিক করার জন্য Flask অংশ ---
app = Flask('')

@app.route('/')
def home():
    return "ZM 24H BOT IS ALIVE!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Flask ব্যাকগ্রাউন্ডে চালু করা
threading.Thread(target=run_flask).start()
# ---------------------------------------------

# আপনার দেওয়া টোকেন এবং প্রাইভেট চ্যানেল আইডি
TOKEN = "8358085571:AAE5YRznsq9FpoW_JI9hxqluXdK6uah8JO8"
CHAT_ID = "-1003401012164"

bot = telebot.TeleBot(TOKEN)

# মার্কেটের তালিকা
pairs = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X',
    'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURCHF=X',
    'GBPCHF=X', 'NZDJPY=X', 'CADJPY=X', 'CHFJPY=X', 'AUDCAD=X', 'AUDCHF=X',
    'AUDNZD=X', 'CADCHF=X', 'BTC-USD', 'ETH-USD', 'MSFT', 'AAPL', 'GOOGL',
    'FB', 'INTC', 'PFE', 'JNJ', 'BA', 'MCD'
]

def check_result(symbol, entry_price, action):
    time.sleep(62)
    try:
        data = download.download(symbol, period='1d', interval='1m', progress=False)
        exit_price = data.iloc[-1]['Close']
        win = (exit_price > entry_price) if "CALL" in action else (exit_price < entry_price)
        res_text = "✅ WIN (PROFIT)" if win else "❌ LOSS"
        bot.send_message(CHAT_ID, f"📊 **RESULT: {symbol.replace('=X', '')}**\n🏆 Status: {res_text}")
    except: pass

def send_auto_signal(pair, action, data):
    try:
        plt.figure(figsize=(6, 4))
        plt.plot(data['Close'].tail(30), color='#2196F3', linewidth=1.5)
        chart_path = "signal.png"
        plt.savefig(chart_path, dpi=80)
        plt.close()

        now = datetime.now()
        msg = (
            f"🚀 **ALL MARKET AUTO SIGNAL** 🚀\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 Asset: {pair.replace('=X', '')}\n"
            f"🎯 Action: {action}\n"
            f"⏰ Entry: {now.strftime('%H:%M:%S')}\n"
            f"⌛ Expiry: 1 MIN\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        with open(chart_path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=msg)
        if os.path.exists(chart_path): os.remove(chart_path)
        threading.Thread(target=check_result, args=(pair, data['Close'].iloc[-1], action)).start()
    except Exception as e: print(f"Signal Error: {e}")

def scanner_loop():
    while True:
        for pair in pairs:
            try:
                data = download.download(pair, period='1d', interval='1m', progress=False)
                if data.empty: continue
                data['RSI'] = ta.rsi(data['Close'], length=5)
                rsi_val = data['RSI'].iloc[-1]
                
                action = None
                if rsi_val < 15: action = "CALL (UP) ⬆️"
                elif rsi_val > 85: action = "PUT (DOWN) ⬇️"

                if action:
                    send_auto_signal(pair, action, data)
                    time.sleep(120) 
            except: continue
        time.sleep(30)

try:
    bot.send_message(CHAT_ID, "✅ **ZM 24H MASTER BOT IS ONLINE (FREE MODE)!**")
except: pass

threading.Thread(target=scanner_loop, daemon=True).start()
bot.polling(none_stop=True)
