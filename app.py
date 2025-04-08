"""
Main Application Entry Point

This module serves as the entry point for the WhatsApp Business API Bulk Messaging application.
It initializes the logging system and launches the GUI.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui import MainWindow
from logger import setup_logger
import logging

def initialize_app():
    """Initialize the application environment."""
    # Set up logging
    logger = setup_logger()
    logger.info("Application starting...")

    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    return logger

def main():
    """Main application entry point."""
    # Initialize application
    logger = initialize_app()

    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for a modern look
        
        # Set application-wide attributes
        app.setApplicationName("WhatsApp Bulk Messenger")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("GUI initialized successfully")
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()