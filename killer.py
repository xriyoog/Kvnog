import telebot
from telebot.types import MessageEntity

TOKEN = "7461340238:AAFrz6L1eA5JR5jkYv6mPPlUiDRg1BjP_Ik"
bot = telebot.TeleBot(TOKEN)

text = "💎 Balance ✅\n💳 Card 💰 Funds\n🏧 ATM ⏳ Pending\n📊 Stats"

emoji_map = [
    (0,  2, "5462902520215002477"),   # 💎
    (11, 1, "6298612102709909362"),   # ✅
    (13, 2, "5472250091332993630"),   # 💳
    (21, 2, "6190336264940559752"),   # 💰
    (30, 2, "4967738760021148319"),   # 🏧
    (37, 1, "5325583469344989152"),   # ⏳
    (47, 2, "5971837723676249096"),   # 📊
]

entities = [
    MessageEntity(type="custom_emoji", offset=off, length=length, custom_emoji_id=eid)
    for off, length, eid in emoji_map
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text, entities=entities)

print("Bot running...")
bot.infinity_polling()
