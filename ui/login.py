"""Login and registration screen."""

import os
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QTabWidget, QCheckBox,
    QSizePolicy, QScrollArea, QDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from config.settings import COLORS
from core.auth import AuthManager

# Security question options
SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your elementary school?",
    "What is your favorite book?",
    "What was the make of your first car?",
    "What is your favorite movie?",
    "What street did you grow up on?"
]


def get_asset_path(filename: str) -> str:
    """Get the path to an asset file, works for both dev and bundled app."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'assets', filename)


class PasswordRecoveryDialog(QDialog):
    """Dialog for recovering password using security questions."""

    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth_manager
        self.email = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the recovery dialog UI."""
        self.setWindowTitle("Recover Password")
        self.setFixedSize(450, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_card']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Password Recovery")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Stacked sections
        self.email_section = QWidget()
        self.questions_section = QWidget()
        self.reset_section = QWidget()

        self._setup_email_section()
        self._setup_questions_section()
        self._setup_reset_section()

        layout.addWidget(self.email_section)
        layout.addWidget(self.questions_section)
        layout.addWidget(self.reset_section)

        self.questions_section.hide()
        self.reset_section.hide()

        layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {COLORS['tertiary']};
                color: white;
            }}
        """)
        layout.addWidget(cancel_btn)

    def _setup_email_section(self):
        """Set up the email entry section."""
        layout = QVBoxLayout(self.email_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        label = QLabel("Enter your email address:")
        label.setStyleSheet(f"color: {COLORS['text']}; font-size: 12pt;")
        layout.addWidget(label)

        self.recovery_email = QLineEdit()
        self.recovery_email.setPlaceholderText("your@email.com")
        self.recovery_email.setFixedHeight(44)
        self.recovery_email.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.recovery_email)

        self.email_error = QLabel("")
        self.email_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt;")
        self.email_error.hide()
        layout.addWidget(self.email_error)

        find_btn = QPushButton("Find Account")
        find_btn.clicked.connect(self._on_find_account)
        find_btn.setFixedHeight(40)
        find_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['tertiary']};
            }}
        """)
        layout.addWidget(find_btn)

    def _setup_questions_section(self):
        """Set up the security questions section."""
        layout = QVBoxLayout(self.questions_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.question1_label = QLabel("Question 1:")
        self.question1_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 11pt; font-weight: bold;")
        layout.addWidget(self.question1_label)

        self.answer1_input = QLineEdit()
        self.answer1_input.setPlaceholderText("Your answer (not case sensitive)")
        self.answer1_input.setFixedHeight(44)
        self.answer1_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.answer1_input)
        layout.addSpacing(8)

        self.question2_label = QLabel("Question 2:")
        self.question2_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 11pt; font-weight: bold;")
        layout.addWidget(self.question2_label)

        self.answer2_input = QLineEdit()
        self.answer2_input.setPlaceholderText("Your answer (not case sensitive)")
        self.answer2_input.setFixedHeight(44)
        self.answer2_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.answer2_input)

        self.questions_error = QLabel("")
        self.questions_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt;")
        self.questions_error.hide()
        layout.addWidget(self.questions_error)

        verify_btn = QPushButton("Verify Answers")
        verify_btn.clicked.connect(self._on_verify_answers)
        verify_btn.setFixedHeight(40)
        verify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['tertiary']};
            }}
        """)
        layout.addWidget(verify_btn)

    def _setup_reset_section(self):
        """Set up the password reset section."""
        layout = QVBoxLayout(self.reset_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        label = QLabel("Enter your new password:")
        label.setStyleSheet(f"color: {COLORS['text']}; font-size: 12pt;")
        layout.addWidget(label)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("New password (8+ characters)")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setFixedHeight(44)
        self.new_password.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm new password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setFixedHeight(44)
        self.confirm_password.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.confirm_password)

        self.reset_error = QLabel("")
        self.reset_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt;")
        self.reset_error.hide()
        layout.addWidget(self.reset_error)

        reset_btn = QPushButton("Reset Password")
        reset_btn.clicked.connect(self._on_reset_password)
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['tertiary']};
            }}
        """)
        layout.addWidget(reset_btn)

    def _on_find_account(self):
        """Handle finding account by email."""
        email = self.recovery_email.text().strip()
        if not email:
            self.email_error.setText("Please enter your email")
            self.email_error.show()
            return

        success, message, q1, q2 = self.auth.get_security_questions(email)
        if success:
            self.email = email
            self.question1_label.setText(f"Q1: {q1}")
            self.question2_label.setText(f"Q2: {q2}")
            self.email_section.hide()
            self.questions_section.show()
        else:
            self.email_error.setText(message)
            self.email_error.show()

    def _on_verify_answers(self):
        """Handle verifying security answers."""
        answer1 = self.answer1_input.text().strip()
        answer2 = self.answer2_input.text().strip()

        if not answer1 or not answer2:
            self.questions_error.setText("Please answer both questions")
            self.questions_error.show()
            return

        success, message = self.auth.verify_security_answers(self.email, answer1, answer2)
        if success:
            self.questions_section.hide()
            self.reset_section.show()
        else:
            self.questions_error.setText(message)
            self.questions_error.show()

    def _on_reset_password(self):
        """Handle password reset."""
        new_pass = self.new_password.text()
        confirm = self.confirm_password.text()

        if not new_pass or not confirm:
            self.reset_error.setText("Please fill in both fields")
            self.reset_error.show()
            return

        if new_pass != confirm:
            self.reset_error.setText("Passwords do not match")
            self.reset_error.show()
            return

        if len(new_pass) < 8:
            self.reset_error.setText("Password must be at least 8 characters")
            self.reset_error.show()
            return

        success, message = self.auth.reset_password(self.email, new_pass)
        if success:
            QMessageBox.information(self, "Success", "Your password has been reset. You can now log in.")
            self.accept()
        else:
            self.reset_error.setText(message)
            self.reset_error.show()


class LoginWidget(QWidget):
    """Login/Register screen widget."""

    login_successful = pyqtSignal()

    def __init__(self, auth_manager: AuthManager):
        super().__init__()
        self.auth = auth_manager
        self.setup_ui()

    def setup_ui(self):
        """Set up the login UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for the entire login page
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['dark_bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['dark_input']};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['primary']};
            }}
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)

        # Center everything
        scroll_layout.addStretch()

        center_layout = QHBoxLayout()
        center_layout.addStretch()

        # Main container
        container = QFrame()
        container.setMaximumSize(520, 880)
        container.setMinimumSize(400, 600)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
                border-radius: 16px;
            }}
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 32, 32, 32)
        container_layout.setSpacing(16)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path('icon.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setMinimumHeight(150)
        logo_label.setAccessibleName("Inclusive Design Wizard logo")
        container_layout.addWidget(logo_label)

        # App Title
        title = QLabel("Inclusive Design Wizard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['primary']};
            margin-bottom: 4px;
        """)
        container_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("AI-Powered Accessibility Consultation")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12pt;")
        container_layout.addWidget(subtitle)

        container_layout.addSpacing(8)

        # Tab widget for Login/Register
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['dark_input']};
                border-radius: 8px;
                background-color: {COLORS['dark_bg']};
                padding: 24px;
                min-height: 350px;
            }}
            QTabBar::tab {{
                padding: 4px 50px;
                margin-right: 4px;
                background-color: {COLORS['dark_input']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['dark_input']};
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-size: 14pt;
                font-weight: bold;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['tertiary']};
                color: white;
            }}
        """)

        # Login tab
        login_tab = self.create_login_tab()
        self.tabs.addTab(login_tab, "Login")

        # Register tab
        register_tab = self.create_register_tab()
        self.tabs.addTab(register_tab, "Register")

        container_layout.addWidget(self.tabs)

        # Continue without login button
        skip_btn = QPushButton("Continue in Local Mode")
        skip_btn.clicked.connect(self.on_local_mode)
        skip_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: none;
                color: {COLORS['text_muted']};
                text-decoration: underline;
                font-size: 11pt;
                padding: 8px;
            }}
            QPushButton:hover {{
                color: {COLORS['primary']};
            }}
        """)
        skip_btn.setAccessibleName("Continue without creating an account")
        container_layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Privacy note
        privacy_note = QLabel("Local mode keeps all data on your device")
        privacy_note.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10pt;")
        privacy_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(privacy_note)

        center_layout.addWidget(container)
        center_layout.addStretch()

        scroll_layout.addLayout(center_layout)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def create_login_tab(self) -> QWidget:
        """Create the login tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(0)
        layout.setContentsMargins(9, 17, 9, 9)

        # Email label
        layout.addWidget(self._create_field_label("Email"))
        layout.addSpacing(5)

        # Email input field
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email")
        self.login_email.setAccessibleName("Login email")
        self._apply_input_style(self.login_email)
        layout.addWidget(self.login_email)
        layout.addSpacing(50)

        # Password label
        layout.addWidget(self._create_field_label("Password"))
        layout.addSpacing(5)

        # Password input field
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setAccessibleName("Login password")
        self.login_password.returnPressed.connect(self.on_login)
        self._apply_input_style(self.login_password)
        layout.addWidget(self.login_password)
        layout.addSpacing(140)

        # Remember login checkbox
        self.remember_login_cb = QCheckBox("Remember login info")
        self.remember_login_cb.setAccessibleName("Remember login credentials")
        self.remember_login_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_muted']};
                font-size: 11pt;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS['dark_input']};
                border: 2px solid {COLORS['dark_input']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.remember_login_cb)
        layout.addSpacing(140)

        # Error label
        self.login_error = QLabel("")
        self.login_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt;")
        self.login_error.setWordWrap(True)
        self.login_error.hide()
        layout.addWidget(self.login_error)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.on_login)
        login_btn.setStyleSheet(self._get_button_style(primary=True))
        login_btn.setFixedHeight(21)
        login_btn.setMinimumWidth(200)
        login_btn.setAccessibleName("Login to your account")
        layout.addWidget(login_btn)

        layout.addSpacing(16)

        # Forgot password link
        forgot_btn = QPushButton("Forgot your password?")
        forgot_btn.clicked.connect(self.on_forgot_password)
        forgot_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: none;
                color: {COLORS['primary']};
                text-decoration: underline;
                font-size: 11pt;
                padding: 4px;
            }}
            QPushButton:hover {{
                color: {COLORS['tertiary']};
            }}
        """)
        forgot_btn.setAccessibleName("Recover your password")
        layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Load saved credentials if available
        self._load_saved_credentials()

        layout.addStretch()

        return tab

    def create_register_tab(self) -> QWidget:
        """Create the register tab with scroll area."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['dark_bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['dark_input']};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['primary']};
            }}
        """)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 20, 8, 8)

        # Email field
        layout.addWidget(self._create_field_label("Email"))
        layout.addSpacing(8)
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Enter your email")
        self.register_email.setAccessibleName("Registration email")
        self._apply_input_style(self.register_email)
        layout.addWidget(self.register_email)
        layout.addSpacing(20)

        # Password field
        layout.addWidget(self._create_field_label("Password"))
        layout.addSpacing(8)
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Create a password (8+ characters)")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password.setAccessibleName("Create password")
        self._apply_input_style(self.register_password)
        layout.addWidget(self.register_password)
        layout.addSpacing(20)

        # Confirm password field
        layout.addWidget(self._create_field_label("Confirm Password"))
        layout.addSpacing(8)
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm your password")
        self.register_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm.setAccessibleName("Confirm password")
        self.register_confirm.returnPressed.connect(self.on_register)
        self._apply_input_style(self.register_confirm)
        layout.addWidget(self.register_confirm)
        layout.addSpacing(20)

        # Show password checkbox
        self.show_reg_password_cb = QCheckBox("Show passwords")
        self.show_reg_password_cb.setAccessibleName("Toggle password visibility")
        self.show_reg_password_cb.toggled.connect(self._toggle_register_password)
        self.show_reg_password_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_muted']};
                font-size: 11pt;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS['dark_input']};
                border: 2px solid {COLORS['dark_input']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.show_reg_password_cb)
        layout.addSpacing(20)

        # Security Questions section
        security_label = QLabel("Security Questions (for password recovery)")
        security_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 12pt;
            color: {COLORS['primary']};
        """)
        layout.addWidget(security_label)
        layout.addSpacing(12)

        # Security Question 1
        layout.addWidget(self._create_field_label("Security Question 1"))
        layout.addSpacing(4)
        self.security_q1 = QComboBox()
        self.security_q1.addItems(SECURITY_QUESTIONS)
        self.security_q1.setFixedHeight(44)
        self.security_q1.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.security_q1)
        layout.addSpacing(8)

        self.security_a1 = QLineEdit()
        self.security_a1.setPlaceholderText("Your answer (not case sensitive)")
        self._apply_input_style(self.security_a1)
        layout.addWidget(self.security_a1)
        layout.addSpacing(16)

        # Security Question 2
        layout.addWidget(self._create_field_label("Security Question 2"))
        layout.addSpacing(4)
        self.security_q2 = QComboBox()
        self.security_q2.addItems(SECURITY_QUESTIONS)
        self.security_q2.setCurrentIndex(1)  # Default to different question
        self.security_q2.setFixedHeight(44)
        self.security_q2.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.security_q2)
        layout.addSpacing(8)

        self.security_a2 = QLineEdit()
        self.security_a2.setPlaceholderText("Your answer (not case sensitive)")
        self.security_a2.returnPressed.connect(self.on_register)
        self._apply_input_style(self.security_a2)
        layout.addWidget(self.security_a2)
        layout.addSpacing(20)

        # Error label
        self.register_error = QLabel("")
        self.register_error.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt;")
        self.register_error.setWordWrap(True)
        self.register_error.hide()
        layout.addWidget(self.register_error)

        # Register button
        register_btn = QPushButton("Create Account")
        register_btn.clicked.connect(self.on_register)
        register_btn.setStyleSheet(self._get_button_style(primary=True))
        register_btn.setFixedHeight(42)
        register_btn.setMinimumWidth(200)
        register_btn.setAccessibleName("Create a new account")
        layout.addWidget(register_btn)

        layout.addStretch()

        scroll.setWidget(scroll_content)
        tab_layout.addWidget(scroll)

        return tab

    def _create_field_label(self, text: str) -> QLabel:
        """Create a styled field label."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 13pt;
            color: {COLORS['text']};
        """)
        label.setFixedHeight(28)
        return label

    def _apply_input_style(self, widget: QLineEdit):
        """Apply consistent input field styling."""
        widget.setFixedHeight(32)
        widget.setFont(QFont("Arial", 12))
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['dark_input']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_muted']};
            }}
        """)

    def _get_button_style(self, primary: bool = False) -> str:
        """Get button stylesheet."""
        if primary:
            return f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 26pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['tertiary']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['secondary']};
                }}
                QPushButton:focus {{
                    outline: 3px solid {COLORS['primary']};
                    outline-offset: 2px;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['dark_input']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13pt;
            }}
            QPushButton:hover {{
                background-color: {COLORS['tertiary']};
                color: white;
            }}
        """

    def _get_credentials_path(self) -> Path:
        """Get path to saved credentials file."""
        if sys.platform == "darwin":
            creds_dir = Path.home() / "Library" / "Application Support" / "Inclusive Design Wizard"
        else:
            creds_dir = Path.home() / ".inclusive-design-wizard"
        creds_dir.mkdir(parents=True, exist_ok=True)
        return creds_dir / ".saved_login"

    def _save_credentials(self, email: str, password: str):
        """Save login credentials to file."""
        try:
            creds_path = self._get_credentials_path()
            # Simple encoding (not secure, but functional for remember me)
            import base64
            encoded = base64.b64encode(json.dumps({
                "email": email,
                "password": password
            }).encode()).decode()
            creds_path.write_text(encoded)
        except Exception as e:
            print(f"Failed to save credentials: {e}")

    def _load_saved_credentials(self):
        """Load saved credentials if available."""
        try:
            creds_path = self._get_credentials_path()
            if creds_path.exists():
                import base64
                encoded = creds_path.read_text()
                data = json.loads(base64.b64decode(encoded).decode())
                self.login_email.setText(data.get("email", ""))
                self.login_password.setText(data.get("password", ""))
                self.remember_login_cb.setChecked(True)
        except Exception as e:
            print(f"Failed to load credentials: {e}")

    def _clear_saved_credentials(self):
        """Clear saved credentials."""
        try:
            creds_path = self._get_credentials_path()
            if creds_path.exists():
                creds_path.unlink()
        except Exception:
            pass

    def _toggle_register_password(self, checked: bool):
        """Toggle register password visibility."""
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.register_password.setEchoMode(mode)
        self.register_confirm.setEchoMode(mode)

    def on_login(self):
        """Handle login button click."""
        email = self.login_email.text().strip()
        password = self.login_password.text()

        if not email or not password:
            self.show_login_error("Please enter both email and password")
            return

        success, message = self.auth.login(email, password)
        if success:
            # Save or clear credentials based on checkbox
            if self.remember_login_cb.isChecked():
                self._save_credentials(email, password)
            else:
                self._clear_saved_credentials()
            self.login_successful.emit()
        else:
            self.show_login_error(message)

    def on_register(self):
        """Handle register button click."""
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        security_q1 = self.security_q1.currentText()
        security_a1 = self.security_a1.text().strip()
        security_q2 = self.security_q2.currentText()
        security_a2 = self.security_a2.text().strip()

        if not email or not password:
            self.show_register_error("Please fill in all fields")
            return

        if password != confirm:
            self.show_register_error("Passwords do not match")
            return

        if not security_a1 or not security_a2:
            self.show_register_error("Please answer both security questions")
            return

        if security_q1 == security_q2:
            self.show_register_error("Please select two different security questions")
            return

        success, message = self.auth.register(
            email, password,
            security_question_1=security_q1,
            security_answer_1=security_a1,
            security_question_2=security_q2,
            security_answer_2=security_a2
        )
        if success:
            self.login_successful.emit()
        else:
            self.show_register_error(message)

    def on_forgot_password(self):
        """Handle forgot password link click."""
        dialog = PasswordRecoveryDialog(self.auth, self)
        dialog.exec()

    def on_local_mode(self):
        """Handle local mode button click."""
        success, message = self.auth.login_local_mode()
        if success:
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Error", message)

    def show_login_error(self, message: str):
        """Show error in login form."""
        self.login_error.setText(message)
        self.login_error.show()
        self.login_error.setAccessibleDescription(f"Error: {message}")

    def show_register_error(self, message: str):
        """Show error in register form."""
        self.register_error.setText(message)
        self.register_error.show()
        self.register_error.setAccessibleDescription(f"Error: {message}")
