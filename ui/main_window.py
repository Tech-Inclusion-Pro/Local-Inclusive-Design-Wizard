"""Main application window."""

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QCursor, QFont, QFontDatabase, QPainter, QScreen, QShortcut, QKeySequence,
)

from config.settings import APP_SETTINGS
from core.database import DatabaseManager
from core.auth import AuthManager
from core.ai_manager import AIManager
from core.conversation import ConversationManager

from .styles import MAIN_STYLESHEET, get_main_stylesheet
from .login import LoginWidget
from .dashboard import DashboardWidget
from .chat import ChatWidget
from .settings import SettingsDialog
from .accessibility_manager import AccessibilityManager


class CursorTrailOverlay(QWidget):
    """Transparent overlay that paints fading cursor images at recent positions."""

    TRAIL_LENGTH = 8       # number of ghost copies to keep
    UPDATE_MS = 20         # timer interval (~50 fps)
    MIN_DISTANCE_SQ = 36   # 6 px² – skip if cursor barely moved

    def __init__(self, cursor_pixmap, hot_x, hot_y, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._pixmap = cursor_pixmap
        self._hot_x = hot_x
        self._hot_y = hot_y
        self._points = []          # recent cursor positions (widget coords)
        self._last_global = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()
        self._timer.start(self.UPDATE_MS)

    def stop(self):
        self._timer.stop()
        self._points.clear()
        self.hide()

    # -- internals --

    def _tick(self):
        gpos = QCursor.pos()
        if self._last_global is not None:
            dx = gpos.x() - self._last_global.x()
            dy = gpos.y() - self._last_global.y()
            if dx * dx + dy * dy < self.MIN_DISTANCE_SQ:
                return
        self._last_global = gpos
        self._points.append(self.mapFromGlobal(gpos))
        if len(self._points) > self.TRAIL_LENGTH:
            self._points.pop(0)
        self.update()

    def paintEvent(self, event):
        if len(self._points) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # Draw every point except the last (the current cursor position)
        n = len(self._points) - 1
        for i in range(n):
            frac = (i + 1) / (n + 1)
            painter.setOpacity(frac * 0.35)
            scale = 0.4 + frac * 0.6
            w = int(self._pixmap.width() * scale)
            h = int(self._pixmap.height() * scale)
            x = self._points[i].x() - int(self._hot_x * scale)
            y = self._points[i].y() - int(self._hot_y * scale)
            painter.drawPixmap(x, y, w, h, self._pixmap)
        painter.end()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)
        self.ai = AIManager()
        self.conversation = ConversationManager(self.db)

        # Create accessibility manager singleton
        self.a11y_manager = AccessibilityManager.create(self)
        self.a11y_manager.settings_changed.connect(self._refresh_all_styles)
        self._cursor_override_active = False
        self._cursor_trail = None

        self.setup_window()
        self.setup_ui()
        self.apply_accessibility()
        self._setup_a11y_shortcut()

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

    def _setup_a11y_shortcut(self):
        """Set up keyboard shortcut for accessibility settings."""
        # Keyboard shortcut Ctrl+Shift+A opens settings
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        shortcut.activated.connect(self.open_settings)

    def _refresh_all_styles(self):
        """Re-apply stylesheets after accessibility preferences change."""
        new_stylesheet = self.a11y_manager.generate_main_stylesheet()
        self.setStyleSheet(new_stylesheet)

        # Apply custom cursor via QCursor (CSS cursor URLs don't work in Qt)
        self._apply_custom_cursor()

        # Notify page widgets to refresh their inline styles
        self.login_page.refresh_styles()
        self.dashboard_page.refresh_styles()
        self.chat_page.refresh_styles()

        # Persist settings if a user is logged in (skip during live preview)
        if not self.a11y_manager.preview_mode:
            self._persist_a11y_settings()

    def _apply_custom_cursor(self):
        """Apply the custom cursor from the accessibility manager.

        Uses QWidget.setCursor() on the main window for persistence, plus
        QApplication.setOverrideCursor() for global coverage (dialogs, menus).
        The override is re-applied after modal dialogs close to survive Qt's
        internal cursor-stack cleanup.

        When the "pointer_trail" cursor is active, a CursorTrailOverlay is
        created on top of the main window to draw fading ghost copies.
        """
        # Clear any active global override first to avoid stacking
        if self._cursor_override_active:
            QApplication.restoreOverrideCursor()
            self._cursor_override_active = False

        cursor = self.a11y_manager.get_cursor()
        if cursor is None:
            self.unsetCursor()
        else:
            # Persistent per-widget cursor (survives dialog open/close)
            self.setCursor(cursor)
            # Global override so dialogs / popups also show the cursor
            QApplication.setOverrideCursor(cursor)
            self._cursor_override_active = True

        # Manage the trail overlay
        needs_trail = (self.a11y_manager.custom_cursor == "pointer_trail"
                       and cursor is not None)
        if needs_trail:
            if self._cursor_trail is None:
                hot = cursor.hotSpot()
                self._cursor_trail = CursorTrailOverlay(
                    cursor.pixmap(), hot.x(), hot.y(), self)
            self._cursor_trail.start()
        else:
            if self._cursor_trail is not None:
                self._cursor_trail.stop()
                self._cursor_trail.deleteLater()
                self._cursor_trail = None

    def _persist_a11y_settings(self):
        """Save accessibility settings to user profile if logged in."""
        user = self.auth.get_current_user()
        if user:
            self.auth.update_user_settings({
                "accessibility": self.a11y_manager.to_dict()
            })

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
        # Load saved accessibility preferences
        user = self.auth.get_current_user()
        if user:
            a11y_prefs = user.settings.get("accessibility", {})
            if a11y_prefs:
                self.a11y_manager.load_from_dict(a11y_prefs)

        self.show_dashboard()

    def show_dashboard(self):
        """Show the dashboard page."""
        self.dashboard_page.refresh()
        self.stack.setCurrentWidget(self.dashboard_page)
        # Focus management: set focus on the primary action
        QTimer.singleShot(100, self._focus_dashboard)

    def _focus_dashboard(self):
        """Set focus to the main action button on the dashboard."""
        # Find the "Start New Consultation" button
        from PyQt6.QtWidgets import QPushButton
        for btn in self.dashboard_page.findChildren(QPushButton):
            if "New Consultation" in (btn.text() or ""):
                btn.setFocus()
                return

    def open_session(self, session_id: int):
        """Open an existing session."""
        self.chat_page.load_session(session_id)
        self.stack.setCurrentWidget(self.chat_page)
        # Focus the message input
        QTimer.singleShot(100, lambda: self.chat_page.message_input.setFocus())

    def create_session(self, title: str, template_type: str):
        """Create and open a new session (saved to database)."""
        user = self.auth.get_current_user()
        if not user:
            return

        session = self.conversation.start_new_session(user.id, title, template_type)
        self.chat_page.load_session(session.id)
        self.stack.setCurrentWidget(self.chat_page)
        QTimer.singleShot(100, lambda: self.chat_page.message_input.setFocus())

    def on_session_saved(self):
        """Handle when a temporary session is saved."""
        # Refresh dashboard to show the new session
        self.dashboard_page.refresh()

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.ai, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
        # Re-apply cursor after modal dialog closes — Qt's dialog teardown
        # pops the override cursor stack, so we need to re-establish it.
        self._apply_custom_cursor()

    def on_settings_changed(self):
        """Handle settings changes — persist accessibility after save."""
        self._persist_a11y_settings()

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
            # Reset accessibility to defaults
            self.a11y_manager.load_from_dict({})
            self.stack.setCurrentWidget(self.login_page)
            # Focus email input on login page
            QTimer.singleShot(100, lambda: self.login_page.login_email.setFocus())

    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        if self._cursor_trail is not None and self._cursor_trail.isVisible():
            self._cursor_trail.setGeometry(self.rect())
            self._cursor_trail.raise_()

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
        if self._cursor_trail is not None:
            self._cursor_trail.stop()
        # Clean up cursor override to restore system default on exit
        if self._cursor_override_active:
            QApplication.restoreOverrideCursor()
            self._cursor_override_active = False
        event.accept()
