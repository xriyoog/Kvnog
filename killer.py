import telebot
from telebot.types import MessageEntity

TOKEN = "7461340238:AAFrz6L1eA5JR5jkYv6mPPlUiDRg1BjP_Ik"
bot = telebot.TeleBot(TOKEN)

# -------------------------------------------------
# Premium emoji IDs: (emoji, custom_emoji_id)
# -------------------------------------------------
PREMIUM_EMOJIS = [
    ("🔥", "5267500801240092311"),
    ("💳", "6206233180148603109"),
    ("💵", "6206155797722830770"),
    ("🚀", "6147654280112248427"),
    ("⭐️", "6206404510689007446"),
    ("💔", "5971992406923416087"),
    ("⚡", "6026367225466720832"),
    ("💳", "5800709991627232190"),
    ("💠", "5971837723676249096"),
    ("✅", "6298612102709909362"),
    ("❌", "5440681540541502133"),
    ("⚠️", "5420323339723881652"),
    ("💰", "6190336264940559752"),
    ("⏱", "5382194935057372936"),
    ("🛍️", "5456140674028019486"),
    ("⚡", "5229064374403998351"),
    ("👑", "5893473283696759404"),
    ("👤", "5895652322469482989"),
    ("⚙️", "5282843764451195532"),
    ("⏰", "5895713431264170680"),
    ("💻", "5222079954421818267"),
    ("⭐", "5042334757040423886"),
    ("⭐", "5039727497143387500"),
    ("⭐", "5042176294222037888"),
    ("⭐", "5042290883949495533"),
    ("⭐", "5041975203853239332"),
    ("⭐", "5042101437237036298"),
    ("⭐", "5427168083074628963"),
    ("⭐", "5039649904264217620"),
    ("⭐", "5042306247047513767"),
    ("⭐", "5039623284056917259"),
    ("⭐", "5042050649248760772"),
    ("⭐", "5042328396193864923"),
    ("⭐", "5040042498634810056"),
    ("⭐", "5039671744172917707"),
    ("⚡", "5879783483462655267"),
    ("✅", "5870702999180942496"),
    ("💳", "5855210601172705878"),
    ("🔗", "4958689671950369798"),
    ("💬", "5855024182412188879"),
    ("🏷", "5854776663446920778"),
    ("🏦", "5854957696318447867"),
    ("🌍", "5852982548233199026"),
    ("👽", "5343993902493895946"),
    ("👑", "5854931759010946555"),
    ("🌚", "6298678524379137990"),
    ("🟢", "5854964615510762741"),
]

# For the echo feature: first design wins when an emoji has multiple IDs
EMOJI_TO_ID = {}
for _e, _id in PREMIUM_EMOJIS:
    EMOJI_TO_ID.setdefault(_e, _id)


def utf16_len(s: str) -> int:
    """MessageEntity offset/length are counted in UTF-16 units."""
    return len(s.encode("utf-16-le")) // 2


def premium_entity(emoji: str, eid: str, offset: int) -> MessageEntity:
    return MessageEntity(
        type="custom_emoji",
        offset=offset,
        length=utf16_len(emoji),
        custom_emoji_id=eid,
    )


@bot.message_handler(commands=["start"])
def start(message):
    head = "Bot is live "
    emoji = "🔥"
    text = head + emoji + "\n\nSend me any supported emoji, or /all to see them all."
    bot.send_message(
        message.chat.id,
        text,
        entities=[premium_entity(emoji, EMOJI_TO_ID[emoji], utf16_len(head))],
    )


@bot.message_handler(commands=["all"])
def show_all(message):
    # chunked to stay safely under entity limits
    for i in range(0, len(PREMIUM_EMOJIS), 10):
        chunk = PREMIUM_EMOJIS[i:i + 10]
        text = ""
        entities = []
        for emoji, eid in chunk:
            entities.append(premium_entity(emoji, eid, utf16_len(text)))
            text += emoji + " "
        bot.send_message(message.chat.id, text, entities=entities)


@bot.message_handler(func=lambda m: m.text and m.text.strip() in EMOJI_TO_ID)
def echo_premium(message):
    emoji = message.text.strip()
    bot.send_message(
        message.chat.id,
        emoji,
        entities=[premium_entity(emoji, EMOJI_TO_ID[emoji], 0)],
    )


print("🔥 Premium emoji bot running...")
bot.infinity_polling()
