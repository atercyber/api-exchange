import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from firebase_config import save_api, delete_api, list_apis, create_key, delete_key, list_keys

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [8418684406]
BASE_URL = "https://api-exchange-c9vw.onrender.com"

# States
WAIT_API_NAME, WAIT_API_URL, WAIT_API_PARAM = range(3)
WAIT_KEY_NAME, WAIT_KEY_SERVICE, WAIT_KEY_EXPIRY, WAIT_KEY_LIMIT = range(3, 7)

def is_admin(update):
    return update.effective_user.id in ADMIN_IDS

async def show_main_menu(update):
    keyboard = [
        [InlineKeyboardButton("📡 API Manage", callback_data="api_menu")],
        [InlineKeyboardButton("🔑 Key Manage", callback_data="key_menu")],
    ]
    text = "👋 नमस्ते! Admin Panel\n\nकोई option चुनो:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ Access Denied")
        return
    await show_main_menu(update)

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await show_main_menu(update)

# ─────────────────────────────────────
# API MENU
# ─────────────────────────────────────

async def api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("➕ नई API Add करो", callback_data="addapi_start")],
        [InlineKeyboardButton("📋 सब APIs देखो", callback_data="listapi")],
        [InlineKeyboardButton("🗑 API हटाओ", callback_data="delapi_start")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    await update.callback_query.edit_message_text("📡 API Management:", reply_markup=InlineKeyboardMarkup(keyboard))

async def listapi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    apis = list_apis()
    text = "📋 सब APIs:\n\n" if apis else "❌ कोई API नहीं है"
    if apis:
        for name, data in apis.items():
            text += f"🔹 {name}\n   URL: {data['url']}\n   Param: {data['param']}\n\n"
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="api_menu")]]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def delapi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    apis = list_apis()
    if not apis:
        await update.callback_query.edit_message_text("❌ कोई API नहीं है")
        return
    keyboard = [[InlineKeyboardButton(f"🗑 {name}", callback_data=f"delapi_{name}")] for name in apis]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="api_menu")])
    await update.callback_query.edit_message_text("कौन सी API हटानी है?", reply_markup=InlineKeyboardMarkup(keyboard))

async def delapi_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    name = update.callback_query.data.replace("delapi_", "")
    delete_api(name)
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="api_menu")]]
    await update.callback_query.edit_message_text(f"✅ {name} API हटा दी!", reply_markup=InlineKeyboardMarkup(keyboard))

# ─────────────────────────────────────
# ADD API CONVERSATION
# ─────────────────────────────────────

async def addapi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("📡 नई API का नाम बताओ:\n\nExample: number, aadhar, ifsc")
    return WAIT_API_NAME

async def addapi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_name'] = update.message.text.lower()
    await update.message.reply_text(f"✅ नाम: {update.message.text}\n\n🔗 अब URL भेजो:\n\nExample: https://api.com/?key=xyz&term=")
    return WAIT_API_URL

async def addapi_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_url'] = update.message.text
    await update.message.reply_text("✅ URL set!\n\n🔧 अब Parameter नाम बताओ:\n\nExample: term, num, query")
    return WAIT_API_PARAM

async def addapi_param(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data['api_name']
    url = context.user_data['api_url']
    param = update.message.text
    save_api(name, url, param)
    keyboard = [
        [InlineKeyboardButton("➕ और API Add करो", callback_data="addapi_start")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    await update.message.reply_text(
        f"✅ API Add हो गई!\n\n🔹 Service: {name}\n🔹 URL: {url}\n🔹 Param: {param}\n\nअब क्या करना है?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

# ─────────────────────────────────────
# KEY MENU
# ─────────────────────────────────────

async def key_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("➕ नई Key बनाओ", callback_data="addkey_start")],
        [InlineKeyboardButton("📋 सब Keys देखो", callback_data="listkeys")],
        [InlineKeyboardButton("🗑 Key हटाओ", callback_data="delkey_start")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
    ]
    await update.callback_query.edit_message_text("🔑 Key Management:", reply_markup=InlineKeyboardMarkup(keyboard))

async def listkeys_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keys = list_keys()
    text = "🔑 सब Keys:\n\n" if keys else "❌ कोई Key नहीं है"
    if keys:
        for k, data in keys.items():
            text += f"🔹 {k}\n   Service: {data['service']}\n   Expiry: {data['expiry']}\n   Used: {data['used']}/{data['limit']}\n\n"
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="key_menu")]]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def delkey_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    keys = list_keys()
    if not keys:
        await update.callback_query.edit_message_text("❌ कोई Key नहीं है")
        return
    keyboard = [[InlineKeyboardButton(f"🗑 {k}", callback_data=f"delkey_{k}")] for k in keys]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="key_menu")])
    await update.callback_query.edit_message_text("कौन सी Key हटानी है?", reply_markup=InlineKeyboardMarkup(keyboard))

async def delkey_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    key = update.callback_query.data.replace("delkey_", "")
    delete_key(key)
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="key_menu")]]
    await update.callback_query.edit_message_text(f"✅ Key {key} हटा दी!", reply_markup=InlineKeyboardMarkup(keyboard))

# ─────────────────────────────────────
# ADD KEY CONVERSATION
# ─────────────────────────────────────

async def addkey_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🔑 नई Key का नाम बताओ:\n\nExample: ANSH123, VIP456")
    return WAIT_KEY_NAME

async def addkey_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['key_name'] = update.message.text
    apis = list_apis()
    keyboard = [[InlineKeyboardButton(f"🔹 {name}", callback_data=f"keyservice_{name}")] for name in apis]
    keyboard.append([InlineKeyboardButton("🌟 All Services", callback_data="keyservice_all")])
    await update.message.reply_text(
        f"✅ Key: {update.message.text}\n\n🔧 कौन सी Service के लिए?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_KEY_SERVICE

async def addkey_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    service = update.callback_query.data.replace("keyservice_", "")
    context.user_data['key_service'] = service
    await update.callback_query.edit_message_text(f"✅ Service: {service}\n\n📅 कितने दिन valid रहेगी?\n\nExample: 30, 7, 1")
    return WAIT_KEY_EXPIRY

async def addkey_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['key_days'] = update.message.text
    await update.message.reply_text(f"✅ Days: {update.message.text}\n\n🔢 कितनी बार use हो सकती है?\n\nExample: 100, 500, 1000")
    return WAIT_KEY_LIMIT

async def addkey_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data['key_name']
    service = context.user_data['key_service']
    days = int(context.user_data['key_days'])
    limit = int(update.message.text)
    create_key(key, service, days, limit)

    api_url = f"{BASE_URL}/api/{service}?key={key}&query=VALUE"

    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]
    await update.message.reply_text(
        f"✅ Key बन गई!\n\n"
        f"🔑 Key: `{key}`\n"
        f"🔹 Service: {service}\n"
        f"📅 Days: {days}\n"
        f"🔢 Limit: {limit}\n\n"
        f"🔗 API URL:\n`{api_url}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    addapi_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(addapi_start, pattern="addapi_start")],
        states={
            WAIT_API_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_name)],
            WAIT_API_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_url)],
            WAIT_API_PARAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_param)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    addkey_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(addkey_start, pattern="addkey_start")],
        states={
            WAIT_KEY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, addkey_name)],
            WAIT_KEY_SERVICE: [CallbackQueryHandler(addkey_service, pattern="^keyservice_")],
            WAIT_KEY_EXPIRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, addkey_expiry)],
            WAIT_KEY_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, addkey_limit)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(addapi_conv)
    application.add_handler(addkey_conv)
    application.add_handler(CallbackQueryHandler(api_menu, pattern="^api_menu$"))
    application.add_handler(CallbackQueryHandler(listapi_callback, pattern="^listapi$"))
    application.add_handler(CallbackQueryHandler(delapi_start, pattern="^delapi_start$"))
    application.add_handler(CallbackQueryHandler(delapi_confirm, pattern="^delapi_(?!start)"))
    application.add_handler(CallbackQueryHandler(key_menu, pattern="^key_menu$"))
    application.add_handler(CallbackQueryHandler(listkeys_callback, pattern="^listkeys$"))
    application.add_handler(CallbackQueryHandler(delkey_start, pattern="^delkey_start$"))
    application.add_handler(CallbackQueryHandler(delkey_confirm, pattern="^delkey_(?!start)"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    print("✅ Bot चल रहा है...")
    application.run_polling()

if __name__ == '__main__':
    main()
