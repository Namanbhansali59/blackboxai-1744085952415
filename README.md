# WhatsApp Bulk Messenger

A Python application that integrates with the WhatsApp Business API to send automated messages to multiple contacts. The application features a modern GUI built with PyQt5, allowing users to easily manage contacts, customize messages, and monitor sending progress.

## Features

- Modern, user-friendly GUI interface
- Bulk message sending with customization
- Image/pamphlet sharing capability
- Real-time progress monitoring
- Comprehensive error handling and logging
- Rate limiting compliance with WhatsApp Business API

## Prerequisites

- Python 3.7 or higher
- WhatsApp Business API credentials
- Active internet connection

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd whatsapp-bulk-messenger
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
   - Open `config.py`
   - Update `AUTH_TOKEN` with your WhatsApp Business API token
   - Update `PHONE_NUMBER_ID` with your WhatsApp Business phone number ID

## Usage

1. Start the application:
```bash
python app.py
```

2. Load contacts:
   - Click "Load Contacts" to import a CSV file
   - CSV should contain columns: name, phone_number, custom_field

3. Compose message:
   - Enter message template in the text area
   - Use placeholders like {name}, {phone_number} for customization

4. (Optional) Add image:
   - Click "Upload Image" to attach a pamphlet
   - Supported formats: JPG, JPEG, PNG
   - Maximum size: 5MB

5. Send messages:
   - Click "Send Messages" to start the bulk sending process
   - Monitor progress in real-time
   - View detailed logs in the activity log panel

## CSV Format

Example contacts.csv format:
```csv
name,phone_number,custom_field
John Doe,+1234567890,Premium
Jane Smith,+0987654321,Standard
```

## Error Handling

- The application includes comprehensive error handling
- Failed messages are automatically retried
- Detailed logs are maintained in `app.log`
- GUI displays real-time status updates

## Rate Limiting

The application respects WhatsApp Business API rate limits:
- Maximum 20 messages per minute by default
- Configurable in `config.py`
- Automatic queue management

## Troubleshooting

1. Check the activity log panel for error messages
2. Verify WhatsApp Business API credentials
3. Ensure proper CSV format
4. Check internet connectivity
5. Verify phone numbers are in correct format

## License

This project is licensed under the MIT License - see the LICENSE file for details.