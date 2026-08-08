import telebot
from telebot.types import MessageEntity

# REPLACE THIS WITH YOUR NEW TOKEN FROM BOTFATHER
TOKEN = "7461340238:AAFrz6L1eA5JR5jkYv6mPPlUiDRg1BjP_Ik" 
bot = telebot.TeleBot(TOKEN)

# Clean dictionary of Premium Emojis (No indentation errors here)
PREMIUM_EMOJIS = {
    "fire": "5267500801240092311",
    "star1": "5427168083074628963",
    "star2": "5042334757040423886",
    "rocket": "6147654280112248427",
    "money": "6206155797722830770",
    "check": "6298612102709909362",
    "cross": "5440681540541502133"
}

@bot.message_handler(commands=['start'])
def start(message):
    text = "Bot is live 🔥"
    
    # Create the custom emoji entity
    entity = MessageEntity(
        type="custom_emoji",
        offset=12,  # Position of the emoji in the text
        length=2,   # Custom emojis are always length 2
        custom_emoji_id=PREMIUM_EMOJIS["fire"]
    )
    
    bot.send_message(
        message.chat.id,
        text,
        entities=[entity]
    )

@bot.message_handler(commands=['star'])
def send_star(message):
    text = "You got a star "
    
    entity = MessageEntity(
        type="custom_emoji",
        offset=13, 
        length=2,
        custom_emoji_id=PREMIUM_EMOJIS["star1"]
    )
    
    bot.send_message(
        message.chat.id,
        text,
        entities=[entity]
    )

print("Bot is running successfully!")
bot.infinity_polling()
