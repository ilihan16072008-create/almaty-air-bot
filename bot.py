from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")

# Список пользователей которые подписались на уведомления
# Здесь хранятся их chat_id — уникальный номер каждого пользователя
subscribers = set()


def get_advice(aqi):
    if aqi <= 50:
        return (
            "🟢 Хорошо\nВоздух чистый — отличный день для прогулки или спорта на улице!"
        )
    elif aqi <= 100:
        return "🟡 Умеренно\nВоздух приемлемый. Чувствительным людям лучше сократить время на улице."
    elif aqi <= 150:
        return "🟠 Вредно для чувствительных\nЛюдям с астмой или аллергией лучше остаться дома."
    elif aqi <= 200:
        return "🔴 Вредно\nВсем рекомендуется сократить время на улице. Закройте окна дома."
    elif aqi <= 300:
        return (
            "🟣 Очень вредно\nОставайтесь дома! Если нужно выйти — наденьте маску N95."
        )
    else:
        return "⚫ Опасно\nЧрезвычайная ситуация! Не выходите на улицу без крайней необходимости."


def get_aqi():
    url = f"http://api.airvisual.com/v2/city?city=Almaty&state=Almaty Oblysy&country=Kazakhstan&key={IQAIR_API_KEY}"
    response = requests.get(url)
    data = response.json()
    aqi = data["data"]["current"]["pollution"]["aqius"]
    return aqi


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот качества воздуха в Алматы.\n\n"
        "Команды:\n"
        "/air — узнать AQI прямо сейчас\n"
        "/subscribe — подписаться на утренние уведомления\n"
        "/unsubscribe — отписаться от уведомлений"
    )


async def air(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Получаю данные...")
    aqi = get_aqi()
    advice = get_advice(aqi)
    await update.message.reply_text(
        f"🌫 Качество воздуха в Алматы:\n" f"AQI: {aqi}\n\n" f"{advice}"
    )


# Когда пользователь пишет /subscribe — добавляем его chat_id в список
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id  # уникальный номер этого чата
    subscribers.add(chat_id)  # добавляем в список подписчиков
    await update.message.reply_text(
        "✅ Ты подписался на утренние уведомления!\n"
        "Каждый день в 8:00 я буду присылать тебе AQI Алматы."
    )


# Когда пользователь пишет /unsubscribe — убираем его из списка
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    subscribers.discard(chat_id)  # убираем из списка (discard не даёт ошибку если нет)
    await update.message.reply_text("❌ Ты отписался от уведомлений.")


# Эта функция запускается каждый день в 8:00 автоматически
async def send_morning_notification(app):
    aqi = get_aqi()
    advice = get_advice(aqi)
    message = (
        f"🌅 Доброе утро! Вот AQI Алматы на сегодня:\n" f"AQI: {aqi}\n\n" f"{advice}"
    )
    # Отправляем сообщение каждому подписчику
    for chat_id in subscribers:
        await app.bot.send_message(chat_id=chat_id, text=message)


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("air", air))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
    scheduler.add_job(
        send_morning_notification, trigger="cron", hour=8, minute=0, args=[app]
    )

    async with app:
        scheduler.start()
        await app.initialize()
        await app.start()
        print("Бот запущен!")
        await app.updater.start_polling()
        await asyncio.Event().wait()  # ждём бесконечно


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

if __name__ == "__main__":
    main()
