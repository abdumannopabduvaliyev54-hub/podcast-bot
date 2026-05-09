from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
 
TOKEN = "8356202668:AAF06xHerY0ehuO8HsiRsbs3A1v3kP47NEA"
 
kliplar = {"motivatsiya": [], "ielts": [], "universitetlar": [], "sport": [], "biznes": []}
TOPICS = {"motivatsiya": "🔥 Motivatsiya", "ielts": "📚 IELTS", "universitetlar": "🎓 Universitetlar", "sport": "💪 Sport", "biznes": "💡 Biznes"}
 
pending = {}
 
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(v, callback_data=k)] for k, v in TOPICS.items()])
    await update.message.reply_text("Assalomu alaykum! 🎧\nQaysi topic qiziqtiradi?", reply_markup=kb)
 
async def topic(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    t = q.data
    if t not in TOPICS:
        return
    if not kliplar[t]:
        await q.edit_message_text(TOPICS[t] + "\n\nHali klip yoq. Tez orada! 🚀", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]]))
        return
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎧 " + k["nomi"], callback_data="k_" + t + "_" + str(i))] for i, k in enumerate(kliplar[t])] + [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]])
    await q.edit_message_text(TOPICS[t] + " — " + str(len(kliplar[t])) + " ta klip:", reply_markup=kb)
 
async def send_clip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(v, callback_data=k)] for k, v in TOPICS.items()])
        await q.edit_message_text("Qaysi topic qiziqtiradi?", reply_markup=kb)
        return
    p = q.data.split("_", 2)
    t, i = p[1], int(p[2])
    klip = kliplar[t][i]
    await q.message.reply_audio(audio=klip["file_id"], title=klip["nomi"])
 
async def media_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
 
    uid = msg.from_user.id
 
    # Fayl keldi
    file_id = None
    if msg.audio:
        file_id = msg.audio.file_id
    elif msg.voice:
        file_id = msg.voice.file_id
    elif msg.document:
        file_id = msg.document.file_id
 
    if file_id:
        caption = msg.caption or ""
        parts = caption.strip().split(" ", 1)
        if len(parts) >= 2 and parts[0] in kliplar:
            # Caption bilan birga keldi
            t, nomi = parts[0], parts[1]
            kliplar[t].append({"nomi": nomi, "file_id": file_id})
            await msg.reply_text("✅ Qoshildi: " + nomi + " — " + TOPICS[t])
        else:
            # Caption yoq — keyingi xabarda nom kutamiz
            pending[uid] = file_id
            await msg.reply_text("✅ Fayl qabul qilindi!\n\nEndi yozing:\n<topic> <nom>\n\nMisol:\nmotivatsiya Abdukarim klip\n\nTopiclar: motivatsiya, ielts, universitetlar, sport, biznes")
        return
 
    # Matn keldi — pending fayl bormi?
    if msg.text and uid in pending:
        parts = msg.text.strip().split(" ", 1)
        if len(parts) < 2 or parts[0] not in kliplar:
            await msg.reply_text("Format: <topic> <nom>\nMisol: motivatsiya Abdukarim klip")
            return
        t, nomi = parts[0], parts[1]
        file_id = pending.pop(uid)
        kliplar[t].append({"nomi": nomi, "file_id": file_id})
        await msg.reply_text("✅ Qoshildi: " + nomi + " — " + TOPICS[t])
 
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(send_clip, pattern="^k_"))
app.add_handler(CallbackQueryHandler(topic))
app.add_handler(MessageHandler(filters.ALL, media_handler))
print("Bot ishlamoqda...")
app.run_polling()
