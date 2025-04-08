"""
Graphical User Interface Module

This module implements a modern GUI using PyQt5 for the WhatsApp Business API integration.
It provides an interface for uploading contacts, customizing messages, and monitoring sending progress.
"""

import sys
import csv
import os
from typing import List, Dict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QProgressBar, QMessageBox, QScrollArea,
    QPlainTextEdit, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from whatsapp_api import WhatsAppAPI
from logger import setup_logger, get_qt_handler
from config import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE

# Initialize logger
logger = setup_logger()

class SendMessagesWorker(QThread):
    """Worker thread for sending bulk messages."""
    progress = pyqtSignal(float, dict)
    finished = pyqtSignal(dict)

    def __init__(self, api: WhatsAppAPI, contacts: List[Dict], 
                 message_template: str, image_url: str = None):
        super().__init__()
        self.api = api
        self.contacts = contacts
        self.message_template = message_template
        self.image_url = image_url

    def run(self):
        """Execute the bulk message sending operation."""
        results = self.api.send_bulk_messages(
            self.contacts,
            self.message_template,
            self.image_url,
            self.progress.emit
        )
        self.finished.emit(results)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.api = WhatsAppAPI()
        self.contacts = []
        self.image_path = None
        self.setup_ui()
        
        # Connect logger to GUI
        qt_handler = get_qt_handler()
        if qt_handler:
            qt_handler.new_log.connect(self.append_log)

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("WhatsApp Bulk Messenger")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel (Contacts)
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel, 1)
        
        # Right panel (Message & Image)
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel, 1)
        
        # Apply modern styling
        self.apply_styles()

    def create_left_panel(self) -> QWidget:
        """Create the left panel containing contacts table and controls."""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Contacts")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        # Contacts table
        self.contacts_table = QTableWidget(0, 3)
        self.contacts_table.setHorizontalHeaderLabels(["Name", "Phone Number", "Custom Field"])
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.contacts_table)
        
        # Controls
        controls = QHBoxLayout()
        load_btn = QPushButton("Load Contacts (CSV)")
        load_btn.clicked.connect(self.load_contacts)
        controls.addWidget(load_btn)
        
        clear_btn = QPushButton("Clear Contacts")
        clear_btn.clicked.connect(self.clear_contacts)
        controls.addWidget(clear_btn)
        
        layout.addLayout(controls)
        
        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right panel containing message customization and sending controls."""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Message section
        msg_header = QLabel("Message Template")
        msg_header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(msg_header)
        
        msg_help = QLabel("Use {name}, {phone_number}, etc. as placeholders")
        msg_help.setStyleSheet("color: gray;")
        layout.addWidget(msg_help)
        
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Enter your message template here...")
        layout.addWidget(self.message_edit)
        
        # Image section
        img_header = QLabel("Pamphlet Image")
        img_header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(img_header)
        
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(300, 200)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        self.image_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_preview)
        
        img_btn = QPushButton("Upload Image")
        img_btn.clicked.connect(self.upload_image)
        layout.addWidget(img_btn)
        
        # Send button and progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        send_btn = QPushButton("Send Messages")
        send_btn.clicked.connect(self.send_messages)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(send_btn)
        
        # Log viewer
        log_header = QLabel("Activity Log")
        log_header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(log_header)
        
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        layout.addWidget(self.log_viewer)
        
        return panel

    def apply_styles(self):
        """Apply modern styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                background-color: #007bff;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTextEdit, QPlainTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007bff;
            }
        """)

    def load_contacts(self):
        """Load contacts from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Contacts",
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                self.contacts = list(reader)
                
            self.update_contacts_table()
            logger.info(f"Loaded {len(self.contacts)} contacts from {file_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load contacts: {str(e)}"
            )
            logger.error(f"Error loading contacts: {str(e)}")

    def update_contacts_table(self):
        """Update the contacts table with loaded data."""
        self.contacts_table.setRowCount(len(self.contacts))
        for i, contact in enumerate(self.contacts):
            self.contacts_table.setItem(i, 0, QTableWidgetItem(contact.get('name', '')))
            self.contacts_table.setItem(i, 1, QTableWidgetItem(contact.get('phone_number', '')))
            self.contacts_table.setItem(i, 2, QTableWidgetItem(contact.get('custom_field', '')))

    def clear_contacts(self):
        """Clear all loaded contacts."""
        self.contacts = []
        self.contacts_table.setRowCount(0)
        logger.info("Contacts cleared")

    def upload_image(self):
        """Upload and preview an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Image",
            "",
            f"Images ({' '.join(['*' + ext for ext in ALLOWED_IMAGE_TYPES])})"
        )
        
        if not file_path:
            return
            
        # Validate file size
        if os.path.getsize(file_path) > MAX_IMAGE_SIZE:
            QMessageBox.warning(
                self,
                "Warning",
                "Selected image exceeds maximum size limit"
            )
            return
            
        # Update preview
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            self.image_preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(scaled_pixmap)
        self.image_path = file_path
        logger.info(f"Image uploaded: {file_path}")

    def send_messages(self):
        """Initiate the bulk message sending operation."""
        if not self.contacts:
            QMessageBox.warning(
                self,
                "Warning",
                "Please load contacts first"
            )
            return
            
        if not self.message_edit.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Warning",
                "Please enter a message template"
            )
            return
            
        # Create and start worker thread
        self.worker = SendMessagesWorker(
            self.api,
            self.contacts,
            self.message_edit.toPlainText(),
            self.image_path
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.sending_finished)
        
        self.progress_bar.setVisible(True)
        self.worker.start()
        logger.info("Started sending messages")

    def update_progress(self, progress: float, results: dict):
        """Update progress bar and log during message sending."""
        self.progress_bar.setValue(int(progress))

    def sending_finished(self, results: dict):
        """Handle completion of message sending operation."""
        self.progress_bar.setVisible(False)
        
        message = (
            f"Message sending completed:\n"
            f"Successful: {results['successful']}\n"
            f"Failed: {results['failed']}"
        )
        
        QMessageBox.information(
            self,
            "Complete",
            message
        )
        logger.info(message)

    def append_log(self, message: str):
        """Append a message to the log viewer."""
        self.log_viewer.appendPlainText(message)
        
    def closeEvent(self, event):
        """Handle application closure."""
        if hasattr(self, 'worker') and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Messages are still being sent. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()