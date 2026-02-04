"""Main application window."""

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QScreen

from config.settings import APP_SETTINGS
from core.database import DatabaseManager
from core.auth import AuthManager
from core.ai_manager import AIManager
from core.conversation import ConversationManager

from .styles import MAIN_STYLESHEET
from .login import LoginWidget
from .dashboard import DashboardWidget
from .chat import ChatWidget
from .settings import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)
        self.ai = AIManager()
        self.conversation = ConversationManager(self.db)

        self.setup_window()
        self.setup_ui()
        self.apply_accessibility()

    def setup_window(self):
        """Configure the main window."""
        self.setWindowTitle(APP_SETTINGS["app_name"])
        self.setMinimumSize(1024, 768)

        # Set initial size to 1200x800 or screen size if smaller
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            width = min(1200, screen_geometry.width() - 100)
            height = min(850, screen_geometry.height() - 100)
            self.resize(width, height)

            # Center on screen
            x = (screen_geometry.width() - width) // 2 + screen_geometry.x()
            y = (screen_geometry.height() - height) // 2 + screen_geometry.y()
            self.move(x, y)
        else:
            self.resize(1200, 850)

        # Set stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)

        # Enable high DPI scaling
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)

    def setup_ui(self):
        """Set up the main UI with stacked pages."""
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Login page
        self.login_page = LoginWidget(self.auth)
        self.login_page.login_successful.connect(self.on_login_success)
        self.stack.addWidget(self.login_page)

        # Dashboard page
        self.dashboard_page = DashboardWidget(self.db, self.auth, self.ai)
        self.dashboard_page.open_session.connect(self.open_session)
        self.dashboard_page.new_session.connect(self.create_session)
        self.dashboard_page.open_settings.connect(self.open_settings)
        self.dashboard_page.logout.connect(self.logout)
        self.stack.addWidget(self.dashboard_page)

        # Chat page
        self.chat_page = ChatWidget(self.ai, self.conversation)
        self.chat_page.back_to_dashboard.connect(self.show_dashboard)
        self.chat_page.session_saved.connect(self.on_session_saved)
        self.stack.addWidget(self.chat_page)

        # Start on login page
        self.stack.setCurrentWidget(self.login_page)

    def apply_accessibility(self):
        """Apply accessibility enhancements."""
        # Set minimum font size
        font = QFont("Arial", APP_SETTINGS["min_font_size"])
        self.setFont(font)

        # Set accessible name for main window
        self.setAccessibleName(APP_SETTINGS["app_name"])
        self.setAccessibleDescription("AI-powered accessibility consultation tool for educators")

    def on_login_success(self):
        """Handle successful login."""
        self.show_dashboard()

    def show_dashboard(self):
        """Show the dashboard page."""
        self.dashboard_page.refresh()
        self.stack.setCurrentWidget(self.dashboard_page)

    def open_session(self, session_id: int):
        """Open an existing session."""
        self.chat_page.load_session(session_id)
        self.stack.setCurrentWidget(self.chat_page)

    def create_session(self, title: str, template_type: str):
        """Create and open a new session (saved to database)."""
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.conversation.start_new_session(user.id, title, template_type)
        self.chat_page.load_session(session.id)
        self.stack.setCurrentWidget(self.chat_page)

    def on_session_saved(self):
        """Handle when a temporary session is saved."""
        # Refresh dashboard to show the new session
        self.dashboard_page.refresh()

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.ai, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self):
        """Handle settings changes."""
        # Could save to user settings here
        pass

    def logout(self):
        """Log out the current user."""
        reply = QMessageBox.question(
            self,
            "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.auth.logout()
            self.stack.setCurrentWidget(self.login_page)

    def keyPressEvent(self, event):
        """Handle global keyboard shortcuts."""
        # Escape to go back
        if event.key() == Qt.Key.Key_Escape:
            if self.stack.currentWidget() == self.chat_page:
                self.show_dashboard()
                return

        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close."""
        # Could add confirmation for unsaved sessions
        event.accept()
