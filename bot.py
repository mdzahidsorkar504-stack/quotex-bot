from flask import Flask
import threading
import telebot
import pandas as pd
import pandas_ta as ta
import yfinance as download
import matplotlib.pyplot as plt
from datetime import datetime
import os
import time

# --- Render Port Error ঠিক করার জন্য Flask অংশ ---
app = Flask('')
@app.route('/')
def home(): return "BOT IS ALIVE!"
def run_flask(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_flask).start()

# --- আপনার সেটিংস ---
TOKEN = "8358085571:AAE5YRznsq9FpoW_JI9hxqluXdK6uah8JO8"
CHAT_ID = "-1003401012164"
bot = telebot.TeleBot(TOKEN)

# দ্রুত সিগন্যালের জন্য RSI লেভেল পরিবর্তন (৩০ এবং ৭০)
RSI_BUY = 30 
RSI_SELL = 70

pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X',
    'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURCHF=X',
    'GBPCHF=X', 'NZDJPY=X', 'CADJPY=X', 'CHFJPY=X', 'AUDCAD=X', 'AUDCHF=X',]

def get_chart(pair, data):
    plt.figure(figsize=(6, 4))
    plt.plot(data['Close'].tail(20), color='#2196F3', linewidth=2)
    plt.title(f"{pair} Live Chart")
    path = f"{pair}.png"
    plt.savefig(path)
    plt.close()
    return path

def scanner_loop():
    while True:
        for pair in pairs:
            try:
                data = download.download(pair, period='1d', interval='1m', progress=False)
                if data.empty: continue
                
                data['RSI'] = ta.rsi(data['Close'], length=7)
                rsi_val = data['RSI'].iloc[-1]
                
                # সিগন্যাল কন্ডিশন চেক
                action = None
                if rsi_val <= RSI_BUY: action = "CALL (UP) ⬆️"
                elif rsi_val >= RSI_SELL: action = "PUT (DOWN) ⬇️"

                if action:
                    # ১. প্রথমে READY মেসেজ পাঠানো
                    bot.send_message(CHAT_ID, f"⏳ **READY FOR NEXT MINUTE!**\n📊 Asset: {pair.replace('=X', '')}\n🎯 Action: {action}\nপজিশন নেওয়ার জন্য প্রস্তুত হোন।")
                    time.sleep(50) # ১০ সেকেন্ড বাকি থাকতে সিগন্যাল দিবে

                    # ২. চার্টসহ মেইন সিgন্যাল পাঠানো
                    chart_path = get_chart(pair, data)
                    msg = (
                        f"🚀 **NEW SIGNAL ALERT** 🚀\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📊 Asset: {pair.replace('=X', '')}\n"
                        f"🎯 Action: {action}\n"
                        f"⌛ Expiry: 1 MIN\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    )
                    with open(chart_path, 'rb') as photo:
                        bot.send_photo(CHAT_ID, photo, caption=msg)
                    if os.path.exists(chart_path): os.remove(chart_path)
                    
                    time.sleep(120) # একই পেয়ারে বারবার সিগন্যাল এড়াতে ২ মিনিট বিরতি
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(10)

# বট চালু হওয়ার মেসেজ
try:
    bot.send_message(CHAT_ID, "✅ **ZM 24H MASTER BOT IS UPDATED!**\nএখন সিগন্যাল আরও দ্রুত আসবে এবং চার্ট ও রেডি মেসেজ দেখাবে।")
except: pass

threading.Thread(target=scanner_loop, daemon=True).start()
bot.polling(none_stop=True)
