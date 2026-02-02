import os

from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

DATA_DIR = "data"
TRACKS_DIR = os.path.join(DATA_DIR, "tracks")
MEDIA_DIR = os.path.join(DATA_DIR, "media")
GRAPHICS_DIR = os.path.join(DATA_DIR, "graphics")

for dir_path in [DATA_DIR, TRACKS_DIR, MEDIA_DIR, GRAPHICS_DIR]:
    os.makedirs(dir_path, exist_ok=True)
