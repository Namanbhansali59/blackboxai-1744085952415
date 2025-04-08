"""
WhatsApp Business API Configuration

This module contains configuration settings for the WhatsApp Business API integration.
To use this application:
1. Obtain your WhatsApp Business API credentials
2. Update the AUTH_TOKEN with your token
3. Update the PHONE_NUMBER_ID with your WhatsApp Business phone number ID
"""

# WhatsApp Business API Configuration
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"  # Base URL for WhatsApp Business API
AUTH_TOKEN = "YOUR_AUTH_TOKEN"  # Replace with your WhatsApp Business API token
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"  # Replace with your WhatsApp Business phone number ID

# Application Configuration
MAX_RETRIES = 3  # Maximum number of retry attempts for failed messages
RETRY_DELAY = 5  # Delay (in seconds) between retry attempts
RATE_LIMIT = 20  # Maximum messages per minute (adjust according to your WhatsApp Business API limits)

# Logging Configuration
LOG_FILE = "app.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# File Upload Configuration
ALLOWED_IMAGE_TYPES = [".jpg", ".jpeg", ".png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
CONTACTS_FILE_TYPE = ".csv"