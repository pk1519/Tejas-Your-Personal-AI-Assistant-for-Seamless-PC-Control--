# config_template.py - Configuration template for AI Dashboard
"""
Configuration template for AI Dashboard
Copy this file to config.py and fill in your actual credentials

IMPORTANT: Never commit config.py with real credentials to git!
"""

# Google OAuth Configuration
# Get these from Google Cloud Console: https://console.cloud.google.com/
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET_HERE"

# MongoDB Configuration  
MONGODB_URI = "mongodb://localhost:27017/"  # Local MongoDB
# For MongoDB Atlas (cloud), use format like:
# MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/"

DATABASE_NAME = "ai_dashboard"
COLLECTION_NAME = "users"

# Application Settings
DEBUG_MODE = True
VOICE_RECOGNITION_TIMEOUT = 5  # seconds
REDIRECT_URI = "http://localhost:8080/callback"

# OAuth Scopes
OAUTH_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

"""
SETUP INSTRUCTIONS:
1. Copy this file to config.py
2. Go to https://console.cloud.google.com/
3. Create a new project or select existing one
4. Enable Google+ API and Google OAuth2 API
5. Create OAuth 2.0 credentials
6. Add http://localhost:8080/callback to authorized redirect URIs
7. Copy your Client ID and Client Secret to the variables above
8. Set up MongoDB (local or Atlas)
9. Never commit config.py to git!
"""
