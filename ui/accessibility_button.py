"""Floating accessibility options button."""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QEvent


class AccessibilityFloatingButton(QPushButton):
    """Fixed 56x56 circular button positioned bottom-right of parent."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("\u267F")  # Wheelchair symbol
        self.setFixedSize(56, 56)
        self.setAccessibleName("Accessibility options (Ctrl+Shift+A)")
        self.setToolTip("Accessibility options (Ctrl+Shift+A)")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

        if parent:
            parent.installEventFilter(self)
            self._reposition()

    def _apply_style(self):
        from config.settings import get_colors
        c = get_colors()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: {c['text']};
                border: 2px solid {c.get('primary_text', c['primary'])};
                border-radius: 28px;
                font-size: 24px;
                font-weight: bold;
                min-height: 56px;
                max-height: 56px;
                min-width: 56px;
                max-width: 56px;
            }}
            QPushButton:hover {{
                background-color: {c['tertiary']};
                border-color: {c['text']};
            }}
            QPushButton:focus {{
                outline: 3px solid {c.get('primary_text', c['primary'])};
                outline-offset: 2px;
            }}
        """)

    def refresh_style(self):
        """Re-apply style after theme change."""
        self._apply_style()

    def _reposition(self):
        """Position at bottom-right of parent with margin."""
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - 24
            y = parent_rect.height() - self.height() - 24
            self.move(x, y)
            self.raise_()

    def eventFilter(self, obj, event):
        """Reposition on parent resize."""
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            self._reposition()
        return super().eventFilter(obj, event)
