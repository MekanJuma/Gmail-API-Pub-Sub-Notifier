import os

class Config:
    DEBUG = False
    PORT = os.environ.get("PORT", "5000")
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/....'
    FIREBASE_EMAIL = 'firebase user email'
    FIREBASE_PASSWORD = 'firebase user password'
