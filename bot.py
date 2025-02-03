import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token (set as environment variable)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Function to download Twitter video
def download_twitter_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text("Hi! Send me a Twitter video link, and I'll download it for you.")

# Message handler for Twitter links
async def handle_message(update: Update, context):
    url = update.message.text
    if "twitter.com" in url or "x.com" in url:
        await update.message.reply_text("Downloading video... Please wait.")
        try:
            video_path = download_twitter_video(url)
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video_file)
            os.remove(video_path)  # Clean up the downloaded file
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            await update.message.reply_text("Sorry, I couldn't download the video. Please check the link and try again.")
    else:
        await update.message.reply_text("Please send a valid Twitter video link.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()