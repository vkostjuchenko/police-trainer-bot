from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import random

TOKEN = "import os
TOKEN = os.environ.get("BOT_TOKEN")
"

(
    START,
    STOP,
    CAR_CHECK,
    ALCOTEST,
    SEARCH,
    DETENTION,
) = range(6)


# --------- СТАРТ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["score"] = 0
    context.user_data["stress"] = 0
    context.user_data["officer_type"] = random.choice(
        ["Спокійний", "Формальний", "Жорсткий"]
    )

    keyboard = [["Почати тренування"]]
    await update.message.reply_text(
        "🛡️ Психологічний тренажер взаємодії з поліцією\n\n"
        "Тип інспектора сьогодні: "
        f"{context.user_data['officer_type']}\n\n"
        "Готові?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return START


# --------- ЗУПИНКА ----------
async def stop_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Спокійно привітатись"],
        ["Почати з претензій"],
    ]

    text = (
        "🚔 Інспектор:\n"
        "— Добрий день. Причина зупинки буде пояснена. Документи.\n\n"
        "Ваша реакція?"
    )

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return STOP


async def stop_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Спокійно привітатись":
        context.user_data["score"] += 2
    else:
        context.user_data["stress"] += 2
        context.user_data["score"] -= 1

    return await car_check(update, context)


# --------- ПЕРЕВІРКА АВТО ----------
async def car_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Погодитись відкрити авто"],
        ["Попросити законну підставу"],
    ]

    await update.message.reply_text(
        "👮 — Планова перевірка. Відкрийте багажник.\n\n"
        "Ваші дії?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return CAR_CHECK


async def car_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Попросити законну підставу":
        context.user_data["score"] += 3
    else:
        context.user_data["stress"] += 1

    return await alcotest(update, context)


# --------- АЛКОТЕСТЕР ----------
async def alcotest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Погодитись пройти тест"],
        ["Вимагати свідків або відеофіксацію"],
    ]

    await update.message.reply_text(
        "👮 — Є підозра на сп'яніння. Пройдемо алкотестер.\n\n"
        "Ваша реакція?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return ALCOTEST


async def alcotest_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Вимагати свідків або відеофіксацію":
        context.user_data["score"] += 2
    else:
        context.user_data["stress"] += 1

    return await search_scene(update, context)


# --------- ПОВЕРХНЕВИЙ ОГЛЯД ----------
async def search_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Не заперечувати, але фіксувати на відео"],
        ["Різко відмовитись"],
    ]

    await update.message.reply_text(
        "👮 — Проведемо поверхневий огляд.\n\n"
        "Що робите?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return SEARCH


async def search_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Не заперечувати, але фіксувати на відео":
        context.user_data["score"] += 2
    else:
        context.user_data["stress"] += 3

    return await detention_scene(update, context)


# --------- ЗАТРИМАННЯ ----------
async def detention_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stress = context.user_data["stress"]

    keyboard = [
        ["Викликати адвоката"],
        ["Почати конфліктувати"],
    ]

    if stress >= 5:
        text = "⚠️ Через напружену поведінку інспектор переходить до затримання."
    else:
        text = "Інспектор вагається. Ситуація напружена."

    await update.message.reply_text(
        text + "\n\nВаші дії?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return DETENTION


async def detention_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Викликати адвоката":
        context.user_data["score"] += 3
    else:
        context.user_data["score"] -= 3
        context.user_data["stress"] += 2

    return await finish(update, context)


# --------- ФІНАЛ ----------
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data["score"]
    stress = context.user_data["stress"]

    result = f"""
📊 Результат:
Бали: {score}
Стрес: {stress}/10

"""

    if score >= 8:
        result += "🟢 Високий рівень правової грамотності."
    elif score >= 3:
        result += "🟡 Середній рівень. Є що покращити."
    else:
        result += "🔴 Високий ризик конфлікту."

    await update.message.reply_text(
        result + "\n\n/start — пройти знову",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


# --------- ЗАПУСК ----------
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        START: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop_scene)],
        STOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop_response)],
        CAR_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_response)],
        ALCOTEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, alcotest_response)],
        SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_response)],
        DETENTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, detention_response)],
    },
    fallbacks=[],
)

app.add_handler(conv)
app.run_polling()

