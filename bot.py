import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import yt_dlp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token (set in .env file)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Function to download media from a tweet
def download_tweet_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'media.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info.get("entries"):
            # Handle playlists (e.g., tweets with multiple images/videos)
            media_files = []
            for entry in info["entries"]:
                ydl.download([entry["url"]])
                media_files.extend([f for f in os.listdir() if f.startswith("media.")])
            return media_files
        else:
            # Handle single media (image or video)
            ydl.download([url])
            return [f for f in os.listdir() if f.startswith("media.")]

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text("Hi! Send me a Twitter link, and I'll download the media for you.")

# Message handler for Twitter links
async def handle_message(update: Update, context):
    url = update.message.text
    if "twitter.com" in url or "x.com" in url:
        await update.message.reply_text("Processing... Please wait.")
        try:
            media_files = download_tweet_media(url)
            if media_files:
                for media_file in media_files:
                    if media_file.endswith((".jpg", ".png", ".jpeg")):
                        # Send images as photos
                        with open(media_file, 'rb') as file:
                            await update.message.reply_photo(file)
                    elif media_file.endswith((".mp4", ".mkv", ".webm")):
                        # Send videos as videos
                        with open(media_file, 'rb') as file:
                            await update.message.reply_video(file)
                    os.remove(media_file)  # Clean up the downloaded file
            else:
                await update.message.reply_text("No media found in this tweet.")
        except Exception as e:
            logger.error(f"Error processing tweet: {e}")
            await update.message.reply_text("Sorry, I couldn't process the tweet. Please check the link and try again.")
    else:
        await update.message.reply_text("Please send a valid Twitter link.")

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