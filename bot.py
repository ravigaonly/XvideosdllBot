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
        'format': 'best',  # Prioritize highest quality
        'outtmpl': 'media.%(ext)s',
        'quiet': True,
        'force_generic_extractor': True,  # Handle Twitter/X media better
        'extract_flat': False,  # Ensure all media is extracted
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Log extracted info for debugging
        logger.info(f"Extracted info: {info}")
        
        # Download media
        ydl.download([url])
        
        # Collect downloaded files
        media_files = [f for f in os.listdir() if f.startswith("media.")]
        logger.info(f"Downloaded files: {media_files}")
        return media_files

# Message handler for Twitter links
async def handle_message(update: Update, context):
    url = update.message.text
    if "twitter.com" in url or "x.com" in url:
        await update.message.reply_text("Processing... Please wait.")
        try:
            media_files = download_tweet_media(url)
            if media_files:
                for media_file in media_files:
                    # Check file type and send accordingly
                    if media_file.endswith((".jpg", ".jpeg", ".png")):
                        with open(media_file, 'rb') as file:
                            await update.message.reply_photo(file)
                    elif media_file.endswith((".mp4", ".gif", ".mkv")):
                        with open(media_file, 'rb') as file:
                            await update.message.reply_video(file)
                    else:
                        logger.warning(f"Unsupported file type: {media_file}")
                    os.remove(media_file)  # Clean up
            else:
                await update.message.reply_text("No media found in this tweet.")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            await update.message.reply_text("Failed to process the tweet. Please try again.")
    else:
        await update.message.reply_text("Please send a valid Twitter link.")

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text("Hi! Send me a Twitter link, and I'll download the media for you.")

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