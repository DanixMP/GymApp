import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, 
                            QDialog, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

from .database import db

class LoginWidget(QDialog):
    login_successful = pyqtSignal(dict)  
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Gym Management System - Login')
        self.setFixedSize(500, 700)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(200, 182, 255))
        self.setPalette(palette)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        logo_label = QLabel()
        import os
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"Failed to load logo from: {logo_path}")
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel('نرم افزار مدیریت باشگاه')
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("_MRT_Khodkar")
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Subtitle
        subtitle = QLabel('ورود اطلاعات کاربری')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("_MRT_Khodkar")
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet('color: #666;')
        
        # Form container
        form_container = QFrame()
        form_container.setStyleSheet('''
            QFrame {
                background: #E4DBFF;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #ddd;
            }
        ''')
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # # Username
        # username_label = QLabel('نام کاربری')
        # username_label.setStyleSheet('''
        #     QLabel {
        #         border: none;
        #     }
        # ''')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('نام کاربری خود را وارد کنید')
        self.username_input.setAlignment(Qt.AlignCenter)
        self.username_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                min-height: 36px;
                font-size: 15px;
                background: #fafbfc;
                text-align: center;
            }
            QLineEdit:focus {
                border: 1.5px solid #3498db;
                background: #f0f8ff;
            }
        ''')
        
        # Password
        # password_label = QLabel('رمز عبور')
        # password_label.setStyleSheet('''
        #     QLabel {
        #         border: none;
        #     }
        # ''')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('رمز عبور خود را وارد کنید')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                min-height: 36px;
                font-size: 15px;
                background: #fafbfc;
                text-align: center;
            }
            QLineEdit:focus {
                border: 1.5px solid #3498db;
                background: #f0f8ff;
            }
        ''')
        
        # Login button
        login_btn = QPushButton('ورود')
        login_btn.clicked.connect(self.authenticate)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setMinimumHeight(44)
        login_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #6dd5fa);
                color: white;
                border: none;
                padding: 12px 0;
                border-radius: 7px;
                font-weight: bold;
                font-size: 16px;
                letter-spacing: 1px;
                font-family:"Dubai Medium"
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #57c1eb);
            }
            QPushButton:pressed {
                background: #2472a4;
            }
        ''')
        
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_btn)
        
        main_layout.addWidget(logo_label)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(20)
        main_layout.addWidget(form_container)
        
        version_label = QLabel('v3.0.31')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #999; font-size: 10px;')
        auth_label = QLabel('Mahdi Pourghaffar')
        auth_label.setAlignment(Qt.AlignCenter)
        auth_label.setStyleSheet('color: #999; font-size: 14px;')
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(version_label)
        main_layout.addWidget(auth_label)
        
        self.setLayout(main_layout)
        
    def authenticate(self):
        """Authenticate the user."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.show_error('لطفا نام کاربری و رمز عبور را وارد کنید')
            return
        user = db.verify_user(username, password)
        if user:
            if user.get('role') == 'admin':
                self.user = user  # Store user info for later use
                self.login_successful.emit(user)
                self.accept()
            else:
                self.show_error('دسترسی فقط برای مدیران مجاز است.')
        else:
            self.show_error('رمز عبور یا نام کاربری را درست وارد کنید')
    
    def show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, 'Login Failed', message)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.authenticate()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)