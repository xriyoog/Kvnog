        target, days = int(context.args[0]), int(context.args[1])
        db.ensure_user(target)
        db.add_plan_days(target, days)
        await update.message.reply_text(
            f"✅ Granted <b>{days}</b> days to <code>{target}</code>",
            parse_mode=ParseMode.HTML)
        try:
            await context.bot.send_message(target,
                f"👑 <b>{days}</b> days added to your plan!",
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
            f"✅ Granted <b>{creds}</b> kill credits to <code>{target}</code>",
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
        await update.message.reply_text(
            f"{box_title('✅ KEY REDEEMED ✅')}\n\n"
            f"📅 𝗗𝗮𝘆𝘀    ▸ <b>{days}</b>\n"
            f"⏱️ 𝗘𝘅𝗽𝗶𝗿𝗲𝘀 ▸ <code>{user.plan_expiry[:10] if user.plan_expiry else 'N/A'}</code>\n"
            f"{sep_mini()}\n"
            f"🔥 Unlimited access while active!",
            parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ Invalid or already redeemed key.")

async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    rows = db._exec("SELECT user_id, username FROM users WHERE is_banned = 1")
    if not rows:
        await update.message.reply_text("No banned users.")
        return
    msg = f"{box_title('🚫 BANLIST 🚫')}\n\n"
    for r in rows:
        msg += f"• <code>{r[0]}</code> — {r[1] or 'N/A'}\n"
    msg += sep_mini()
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
    progress = await update.message.reply_text(
        f"📢 Broadcasting to {len(rows)} users...\n✅ {sent} | ❌ {failed}",
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
                    f"📢 Broadcasting to {len(rows)} users...\n✅ {sent} | ❌ {failed}",
                    parse_mode=ParseMode.HTML)
            except:
                pass
        await asyncio.sleep(0.05)
    await progress.edit_text(
        f"{box_title('📢 BROADCAST DONE 📢')}\n\n"
        f"✅ 𝗦𝗲𝗻𝘁   ▸ <code>{sent}</code>\n"
        f"❌ 𝗙𝗮𝗶𝗹𝗲𝗱 ▸ <code>{failed}</code>\n"
        f"👥 𝗧𝗼𝘁𝗮𝗹 ▸ <code>{len(rows)}</code>\n{sep_mini()}",
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
    total_kills = db._exec("SELECT SUM(kill_count) FROM users")[0][0] or 0
    total_credits = db._exec("SELECT SUM(kill_credits) FROM users")[0][0] or 0
    total_approved = db._exec("SELECT SUM(total_approved) FROM users")[0][0] or 0
    pa = await proxy_pool.count_active()
    pt = await proxy_pool.count_total()
    await update.message.reply_text(
        f"{box_title(f'📊 BOT STATS 📊')}\n\n"
        f"👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀  ▸ <code>{s['users']}</code>\n"
        f"✅ 𝗔𝗰𝘁𝗶𝘃𝗲      ▸ <code>{active_u}</code>\n"
        f"🚫 𝗕𝗮𝗻𝗻𝗲𝗱    ▸ <code>{banned_u}</code>\n"
        f"👑 𝗪𝗶𝘁𝗵 𝗣𝗹𝗮𝗻   ▸ <code>{with_plan}</code>\n"
        f"{sep_mid()}\n"
        f"🔍 𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗲𝗰𝗸𝘀 ▸ <code>{s['checks']}</code>\n"
        f"💎 𝗟𝗶𝘃𝗲𝘀      ▸ <code>{s['lives']}</code>\n"
        f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱   ▸ <code>{total_approved}</code>\n"
        f"💀 𝗧𝗼𝘁𝗮𝗹 𝗞𝗶𝗹𝗹𝘀 ▸ <code>{total_kills}</code>\n"
        f"💰 𝗖𝗿𝗲𝗱𝗶𝘁𝘀    ▸ <code>{total_credits}</code>\n"
        f"{sep_mid()}\n"
        f"🌐 𝗣𝗿𝗼𝘅𝗶𝗲𝘀    ▸ <code>{pa}/{pt}</code> active\n"
        f"{sep_mini()}",
        parse_mode=ParseMode.HTML)

async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Owner only.")
        return
    await proxy_pool.reload()
    count = await proxy_pool.count_active()
    await update.message.reply_text(
        f"{box_title('🔄 RELOADED 🔄')}\n\n"
        f"🌐 𝗔𝗰𝘁𝗶𝘃𝗲 𝗣𝗿𝗼𝘅𝗶𝗲𝘀 ▸ <code>{count}</code>\n{sep_mini()}",
        parse_mode=ParseMode.HTML)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document or not document.file_name.endswith(".txt"):
        return
    await mst(update, context)

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

    # Check commands
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("check", chk))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("mst", mst))
    app.add_handler(CommandHandler("mass", mst))
    app.add_handler(CommandHandler("stop", stop_mass))

    # Tool commands
    app.add_handler(CommandHandler("bin", bin_cmd))
    app.add_handler(CommandHandler("gen", gen_cmd))
    app.add_handler(CommandHandler("me", profile_cmd))
    app.add_handler(CommandHandler("id", id_cmd))

    # User commands
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("mystats", mystats))
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

    # Callback + Document handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_document))
    app.add_error_handler(error_handler)

    logger.info("═══════════════════════════════════════")
    logger.info(f"  ⚡ KVN Killer v{VERSION} — {CODENAME}")
    logger.info("  Dataclass Architecture · Smart Proxies")
    logger.info("  Rate Limiting · Card Gen · BIN Lookup")
    logger.info("  Session Pooling · Retry Engine · ETA")
    logger.info("═══════════════════════════════════════")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port:
        threading.Thread(target=run_health_server, daemon=True).start()
    logger.info(f"Starting KVN Killer v{VERSION} {CODENAME}...")
    main()
