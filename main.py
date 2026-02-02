import telebot
import requests
import html
import time
import threading
from flask import Flask

BOT_TOKEN = "8590059786:AAHHYSvKOJ-Pc1kvoeQTaoQs6-brwTbzn4Q"
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
RENDER_APP_URL = "https://genbot-ppjy.onrender.com" 

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    while True:
        try:
            time.sleep(1500)
            if RENDER_APP_URL != "আপনার_রেন্ডার_URL_এখানে_দিন":
                requests.get(RENDER_APP_URL)
        except:
            pass

def get_easy_code(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_instruction = (
        "You are an expert developer. Rule: Use ONLY the most popular and easiest-to-install libraries. "
        "1. For Python: Always use 'pyTelegramBotAPI' (telebot). "
        "2. For Cloudflare: Use standard Fetch API and ES Modules. "
        "3. Output ONLY raw code text. No markdown, no intro."
    )
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=60)
        return response.json()['choices'][0]['message']['content'].strip()
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ **সহজ কোড জেনারেটর রেডি!**\nএটি এখন Render-এ হোস্ট করা এবং Self-Ping মুডে আছে।")

@bot.message_handler(func=lambda message: True)
def handle(message):
    user_sessions[message.chat.id] = message.text
    wait = bot.send_message(message.chat.id, "🛠 কোড তৈরি করছি...")
    raw_code = get_easy_code(message.text)
    if raw_code:
        safe_code = html.escape(raw_code)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔄 রিজেনারেট", callback_data="regen"),
                   telebot.types.InlineKeyboardButton("🆙 আপডেট", callback_data="upd"))
        bot.delete_message(message.chat.id, wait.message_id)
        bot.send_message(message.chat.id, f"<pre><code>{safe_code}</code></pre>", parse_mode="HTML", reply_markup=markup)
    else:
        bot.edit_message_text("❌ সমস্যা হয়েছে, আবার চেষ্টা করুন।", message.chat.id, wait.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "regen":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        handle(call.message)
    elif call.data == "upd":
        msg = bot.send_message(call.message.chat.id, "কি ফিচার যোগ করতে চান?")
        bot.register_next_step_handler(msg, process_update, call.message.message_id)

def process_update(message, old_id):
    chat_id = message.chat.id
    new_prompt = f"Update this code: {message.text}. Context: {user_sessions.get(chat_id, '')}"
    try: bot.delete_message(chat_id, old_id)
    except: pass
    handle(message)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.infinity_polling()
      
