import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'wo-and-man-luxury-secret-key-2026-prod-grade')
    
    # Database: SQLite with WAL mode by default, or Postgres if DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{BASE_DIR / 'instance' / 'wo_and_man.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 30, "check_same_thread": False} if "sqlite" in os.getenv('DATABASE_URL', 'sqlite') else {}
    }
    
    # Business timezone
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tashkent')
    
    # Studio Brand & Defaults
    STUDIO_NAME = "WO&MAN"
    STUDIO_TAGLINE = "Grooming & Beauty Studio"
    STUDIO_PHONE = "+998 71 200 00 20"
    STUDIO_ADDRESS = "Toshkent shahri, Amir Temur shox ko'chasi, 45-uy"
    STUDIO_MAP_QUERY = "Amir Temur shox ko'chasi 45, Toshkent"
    STUDIO_WORKING_HOURS = "09:00 - 21:00 (Har kuni / Без выходных)"
    
    # Booking Rules
    MIN_BOOKING_NOTICE_HOURS = int(os.getenv('MIN_BOOKING_NOTICE_HOURS', 2))
    MAX_BOOKING_ADVANCE_DAYS = int(os.getenv('MAX_BOOKING_ADVANCE_DAYS', 30))
    APPOINTMENT_BUFFER_MINUTES = int(os.getenv('APPOINTMENT_BUFFER_MINUTES', 10))
    MANUAL_APPROVAL_REQUIRED = os.getenv('MANUAL_APPROVAL_REQUIRED', 'false').lower() == 'true'
    
    # Telegram Bot Configuration
    # Single official bot, separate Chat IDs for the five professionals and studio admin
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID_ADMIN = os.getenv('TELEGRAM_CHAT_ID_ADMIN', '')
    TELEGRAM_CHAT_ID_AZIZ = os.getenv('TELEGRAM_CHAT_ID_AZIZ', '')
    TELEGRAM_CHAT_ID_KAMILA = os.getenv('TELEGRAM_CHAT_ID_KAMILA', '')
    TELEGRAM_CHAT_ID_JAMSHID = os.getenv('TELEGRAM_CHAT_ID_JAMSHID', '')
    TELEGRAM_CHAT_ID_MADINA = os.getenv('TELEGRAM_CHAT_ID_MADINA', '')
    TELEGRAM_CHAT_ID_SHAVKAT = os.getenv('TELEGRAM_CHAT_ID_SHAVKAT', '')
    
    # SMS Configuration
    SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'mock') # mock, eskiz, playmobile, twilio
    SMS_API_KEY = os.getenv('SMS_API_KEY', '')
    SMS_API_SECRET = os.getenv('SMS_API_SECRET', '')
    SMS_SENDER_NAME = os.getenv('SMS_SENDER_NAME', 'WO&MAN')
    
    # Media & Uploads
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
