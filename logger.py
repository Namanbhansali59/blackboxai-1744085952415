"""
Logging Configuration Module

This module sets up a centralized logging system for the WhatsApp Business API integration.
It provides both file and console logging, with the ability to stream logs to the GUI.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from PyQt5.QtCore import QObject, pyqtSignal
from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

class QtHandler(QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for GUI integration."""
    new_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter(LOG_FORMAT))

    def emit(self, record):
        """Emit a log message as a Qt signal."""
        msg = self.format(record)
        self.new_log.emit(msg)

def setup_logger(name="whatsapp_messenger"):
    """
    Set up and configure the logger with console, file, and Qt handlers.
    
    Args:
        name (str): The name of the logger instance
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # File Handler (with rotation)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    # Qt Handler for GUI integration
    qt_handler = QtHandler()
    logger.addHandler(qt_handler)

    return logger

def get_qt_handler():
    """
    Get the Qt handler instance from the logger.
    
    Returns:
        QtHandler: The Qt handler instance for GUI integration
    """
    logger = logging.getLogger("whatsapp_messenger")
    for handler in logger.handlers:
        if isinstance(handler, QtHandler):
            return handler
    return None

# Example usage of different log levels
def log_debug(message):
    """Log a debug message."""
    logging.getLogger("whatsapp_messenger").debug(message)

def log_info(message):
    """Log an info message."""
    logging.getLogger("whatsapp_messenger").info(message)

def log_warning(message):
    """Log a warning message."""
    logging.getLogger("whatsapp_messenger").warning(message)

def log_error(message):
    """Log an error message."""
    logging.getLogger("whatsapp_messenger").error(message)

def log_critical(message):
    """Log a critical message."""
    logging.getLogger("whatsapp_messenger").critical(message)