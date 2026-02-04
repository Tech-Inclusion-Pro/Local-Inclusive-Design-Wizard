"""Global styles and stylesheets for the application."""

from config.settings import COLORS

# Main application stylesheet
MAIN_STYLESHEET = f"""
/* Global styles */
* {{
    font-family: Arial, sans-serif;
    font-size: 16px;
}}

QMainWindow, QDialog, QWidget {{
    background-color: {COLORS['dark_bg']};
    color: {COLORS['text']};
}}

/* Labels */
QLabel {{
    color: {COLORS['text']};
    font-size: 16px;
}}

QLabel[class="heading"] {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['text']};
}}

QLabel[class="subheading"] {{
    font-size: 18px;
    color: {COLORS['text_muted']};
}}

QLabel[class="muted"] {{
    color: {COLORS['text_muted']};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text']};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    min-height: 44px;
    min-width: 44px;
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

QPushButton:disabled {{
    background-color: {COLORS['dark_input']};
    color: {COLORS['text_muted']};
}}

QPushButton[class="secondary"] {{
    background-color: {COLORS['secondary']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['tertiary']};
}}

QPushButton[class="text"] {{
    background-color: transparent;
    color: {COLORS['primary']};
}}

QPushButton[class="text"]:hover {{
    background-color: rgba(162, 59, 132, 0.1);
}}

/* Input fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['dark_input']};
    color: {COLORS['text']};
    border: 2px solid {COLORS['dark_card']};
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
    min-height: 44px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QLineEdit:disabled {{
    background-color: {COLORS['dark_bg']};
    color: {COLORS['text_muted']};
}}

/* Combo boxes */
QComboBox {{
    background-color: {COLORS['dark_input']};
    color: {COLORS['text']};
    border: 2px solid {COLORS['dark_card']};
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
    min-height: 44px;
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 12px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
    width: 12px;
    height: 12px;
    background: {COLORS['text']};
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['dark_card']};
    color: {COLORS['text']};
    border: 2px solid {COLORS['primary']};
    selection-background-color: {COLORS['primary']};
}}

/* Scroll areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {COLORS['dark_bg']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['dark_input']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['dark_bg']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['dark_input']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['primary']};
}}

/* Cards */
QFrame[class="card"] {{
    background-color: {COLORS['dark_card']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame[class="card"]:hover {{
    background-color: {COLORS['dark_input']};
}}

/* Progress bar */
QProgressBar {{
    background-color: {COLORS['dark_input']};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {COLORS['text']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 8px;
}}

/* Tabs */
QTabWidget::pane {{
    border: none;
    background-color: {COLORS['dark_card']};
    border-radius: 8px;
}}

QTabBar::tab {{
    background-color: {COLORS['dark_bg']};
    color: {COLORS['text_muted']};
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 16px;
    min-height: 44px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['dark_card']};
    color: {COLORS['text']};
}}

QTabBar::tab:hover {{
    color: {COLORS['primary']};
}}

/* Check boxes */
QCheckBox {{
    color: {COLORS['text']};
    font-size: 16px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 24px;
    height: 24px;
    border-radius: 4px;
    border: 2px solid {COLORS['dark_input']};
    background-color: {COLORS['dark_bg']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:focus {{
    outline: 3px solid {COLORS['primary']};
    outline-offset: 2px;
}}

/* Radio buttons */
QRadioButton {{
    color: {COLORS['text']};
    font-size: 16px;
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 24px;
    height: 24px;
    border-radius: 12px;
    border: 2px solid {COLORS['dark_input']};
    background-color: {COLORS['dark_bg']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

/* Message boxes */
QMessageBox {{
    background-color: {COLORS['dark_card']};
}}

QMessageBox QLabel {{
    color: {COLORS['text']};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS['dark_card']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['primary']};
    padding: 8px;
    border-radius: 4px;
    font-size: 14px;
}}

/* Menu */
QMenu {{
    background-color: {COLORS['dark_card']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['dark_input']};
    padding: 8px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary']};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['dark_input']};
}}

QSplitter::handle:hover {{
    background-color: {COLORS['primary']};
}}
"""

# Card styles for dashboard
CARD_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_card']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame:hover {{
    background-color: {COLORS['dark_input']};
    border: 2px solid {COLORS['primary']};
}}
"""

# Chat message styles
USER_MESSAGE_STYLE = f"""
QFrame {{
    background-color: {COLORS['primary']};
    border-radius: 12px;
    padding: 12px;
    margin: 4px;
}}
"""

ASSISTANT_MESSAGE_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_card']};
    border-radius: 12px;
    padding: 12px;
    margin: 4px;
}}
"""

# Phase indicator styles
PHASE_COMPLETED_STYLE = f"""
QFrame {{
    background-color: {COLORS['success']};
    border-radius: 8px;
    padding: 8px;
}}
"""

PHASE_CURRENT_STYLE = f"""
QFrame {{
    background-color: {COLORS['primary']};
    border-radius: 8px;
    padding: 8px;
    border: 2px solid {COLORS['text']};
}}
"""

PHASE_PENDING_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_input']};
    border-radius: 8px;
    padding: 8px;
}}
"""


def get_focus_style() -> str:
    """Get focus indicator style."""
    return f"outline: 3px solid {COLORS['primary']}; outline-offset: 2px;"
