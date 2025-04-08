"""
WhatsApp Business API Integration Module

This module handles all communications with the WhatsApp Business API,
including sending messages, handling errors, and managing rate limits.
"""

import time
import requests
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin
import logging
from config import (
    WHATSAPP_API_URL,
    AUTH_TOKEN,
    PHONE_NUMBER_ID,
    MAX_RETRIES,
    RETRY_DELAY,
    RATE_LIMIT
)
from logger import setup_logger

# Initialize logger
logger = setup_logger()

class WhatsAppAPI:
    def __init__(self):
        """Initialize WhatsApp API client with configuration settings."""
        self.base_url = WHATSAPP_API_URL
        self.auth_token = AUTH_TOKEN
        self.phone_number_id = PHONE_NUMBER_ID
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.message_count = 0
        self.last_reset_time = time.time()

    def _check_rate_limit(self) -> bool:
        """
        Check if current message rate is within limits.
        
        Returns:
            bool: True if within rate limit, False otherwise
        """
        current_time = time.time()
        if current_time - self.last_reset_time >= 60:
            self.message_count = 0
            self.last_reset_time = current_time
        
        if self.message_count >= RATE_LIMIT:
            logger.warning("Rate limit reached. Waiting before sending more messages.")
            return False
        return True

    def _wait_for_rate_limit(self):
        """Wait until rate limit reset."""
        while not self._check_rate_limit():
            time.sleep(1)

    def send_message(
        self,
        phone_number: str,
        message: str,
        image_url: Optional[str] = None,
        retry_count: int = 0
    ) -> Dict:
        """
        Send a message to a specific phone number via WhatsApp Business API.
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message content
            image_url (str, optional): URL of image to send
            retry_count (int): Current retry attempt number
            
        Returns:
            dict: API response
        """
        self._wait_for_rate_limit()

        try:
            endpoint = f"{self.base_url}/{self.phone_number_id}/messages"
            
            # Prepare message payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }

            # If image URL is provided, modify payload to include image
            if image_url:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_number,
                    "type": "image",
                    "image": {"url": image_url}
                }

            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                self.message_count += 1
                logger.info(f"Message sent successfully to {phone_number}")
                return response.json()
            
            error_msg = f"Failed to send message to {phone_number}. Status: {response.status_code}"
            if retry_count < MAX_RETRIES:
                logger.warning(f"{error_msg} Retrying...")
                time.sleep(RETRY_DELAY)
                return self.send_message(phone_number, message, image_url, retry_count + 1)
            
            logger.error(f"{error_msg} Max retries reached.")
            return {"error": error_msg, "status_code": response.status_code}

        except requests.RequestException as e:
            error_msg = f"Network error while sending message to {phone_number}: {str(e)}"
            if retry_count < MAX_RETRIES:
                logger.warning(f"{error_msg} Retrying...")
                time.sleep(RETRY_DELAY)
                return self.send_message(phone_number, message, image_url, retry_count + 1)
            
            logger.error(f"{error_msg} Max retries reached.")
            return {"error": error_msg}

    def send_bulk_messages(
        self,
        contacts: List[Dict],
        message_template: str,
        image_url: Optional[str] = None,
        callback=None
    ) -> Dict:
        """
        Send customized messages to multiple contacts.
        
        Args:
            contacts (List[Dict]): List of contact dictionaries with details
            message_template (str): Message template with placeholders
            image_url (str, optional): URL of image to send
            callback (callable, optional): Callback function for progress updates
            
        Returns:
            dict: Summary of sending operation
        """
        results = {
            "total": len(contacts),
            "successful": 0,
            "failed": 0,
            "failures": []
        }

        for index, contact in enumerate(contacts):
            try:
                # Customize message for this contact
                custom_message = message_template.format(**contact)
                
                # Send message
                response = self.send_message(
                    phone_number=contact['phone_number'],
                    message=custom_message,
                    image_url=image_url
                )

                # Update results
                if "error" not in response:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append({
                        "contact": contact,
                        "error": response["error"]
                    })

                # Progress callback
                if callback:
                    progress = (index + 1) / len(contacts) * 100
                    callback(progress, results)

            except Exception as e:
                logger.error(f"Error processing contact {contact}: {str(e)}")
                results["failed"] += 1
                results["failures"].append({
                    "contact": contact,
                    "error": str(e)
                })

        logger.info(f"Bulk message sending completed. "
                   f"Success: {results['successful']}, "
                   f"Failed: {results['failed']}")
        return results

    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any spaces or special characters
        cleaned_number = ''.join(filter(str.isdigit, phone_number))
        
        # Basic validation (can be enhanced based on specific requirements)
        if len(cleaned_number) < 10 or len(cleaned_number) > 15:
            return False
        return True

    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to WhatsApp API requirements.
        
        Args:
            phone_number (str): Phone number to format
            
        Returns:
            str: Formatted phone number
        """
        # Remove any non-digit characters
        cleaned_number = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure number starts with country code
        if not cleaned_number.startswith('+'):
            cleaned_number = '+' + cleaned_number
            
        return cleaned_number