import logging
import asyncio
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = '7646239186:AAG0Eu6ssWtUn563VJnbJ1qlVbe5GZaawx0'
SOURCE_CHANNEL_USERNAME = 'rodast_omiddana'
TARGET_CHANNEL_USERNAME = '@roodast_news'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

media_group_cache = {}

async def check_and_send_media_group(application):
    while True:
        for group_id, messages in list(media_group_cache.items()):
            if len(messages) > 0:
                media = []
                for msg in sorted(messages, key=lambda x: x.message_id):
                    if msg.photo:
                        media.append(
                            InputMediaPhoto(
                                media=msg.photo[-1].file_id,
                                caption=msg.caption or ""
                            )
                        )
                    elif msg.video:
                        media.append(
                            InputMediaVideo(
                                media=msg.video.file_id,
                                caption=msg.caption or ""
                            )
                        )

                try:
                    await application.bot.send_media_group(
                        chat_id=TARGET_CHANNEL_USERNAME,
                        media=media
                    )
                    logging.info("✅ آلبوم فوروارد شد.")
                except Exception as e:
                    logging.error(f"❌ خطا در فوروارد آلبوم: {e}")

                del media_group_cache[group_id]

        await asyncio.sleep(2)

async def forward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg:
        return

    if msg.chat.username != SOURCE_CHANNEL_USERNAME:
        return

    if msg.media_group_id:
        media_group_cache.setdefault(msg.media_group_id, []).append(msg)
    else:
        try:
            await context.bot.forward_message(
                chat_id=TARGET_CHANNEL_USERNAME,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )
            logging.info("✅ پیام تکی فوروارد شد.")
        except Exception as e:
            logging.error(f"❌ خطا در فوروارد پیام تکی: {e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, forward_handler))

# اجرای تسک پس‌زمینه بعد از شروع برنامه
async def post_init(application):
    application.create_task(check_and_send_media_group(application))

app.post_init = post_init

print("🤖 ربات فعال شد و در حال شنود پیام‌ها...")

app.run_polling()
