import telebot
from telebot.types import MessageEntity

TOKEN = "7461340238:AAFrz6L1eA5JR5jkYv6mPPlUiDRg1BjP_Ik"
bot = telebot.TeleBot(TOKEN)

text = ("⚡ Speed 🔄 Sync\n"
        "🔗 Link 💳 Card 💰 Cash\n"
        "❌ Fail ✅ Success\n"
        "💎 Premium ⚠️ Warning\n"
        "👑 VIP")

emoji_map = [
    (0,  1, "6026367225466720832"),   # ⚡
    (8,  2, "5971837723676249096"),   # 🔄
    (16, 2, "4958689671950369798"),   # 🔗
    (24, 2, "5800709991627232190"),   # 💳
    (32, 2, "6190336264940559752"),   # 💰
    (40, 1, "5440681540541502133"),   # ❌
    (47, 1, "6298612102709909362"),   # ✅
    (57, 2, "5427168083074628963"),   # 💎
    (68, 1, "5420323339723881652"),   # ⚠️
    (79, 2, "5039727497143387500"),   # 👑
]

entities = [
    MessageEntity(type="custom_emoji", offset=off, length=length, custom_emoji_id=eid)
    for off, length, eid in emoji_map
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text, entities=entities)

bot.remove_webhook()   # clears any stuck session, prevents 409 conflicts
print("Bot running...")
bot.infinity_polling()
