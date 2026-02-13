"""Global styles and stylesheets for the application."""

from config.settings import COLORS


def get_main_stylesheet(colors=None, fonts=None, enhanced_focus=False,
                        dyslexia_font=False, custom_cursor="default") -> str:
    """Generate the main application stylesheet dynamically.

    Args:
        colors: Color dict (defaults to COLORS).
        fonts: Font size dict with keys base, heading, subheading (defaults to medium).
        enhanced_focus: Whether to append enhanced focus indicator rules.
        dyslexia_font: Whether to use OpenDyslexic font family.
        custom_cursor: Unused (kept for API compatibility). Cursor is now
            applied programmatically via QCursor in MainWindow.
    """
    c = colors or COLORS
    f = fonts or {"base": 16, "heading": 24, "subheading": 18}

    if dyslexia_font:
        font_family = "'OpenDyslexic', 'Comic Sans MS', Arial, sans-serif"
    else:
        font_family = "Arial, sans-serif"

    stylesheet = f"""
/* Global styles */
* {{
    font-family: {font_family};
    font-size: {f['base']}px;
    letter-spacing: 0.2px;
}}

QMainWindow, QDialog, QWidget {{
    background-color: {c['dark_bg']};
    color: {c['text']};
}}

/* Labels */
QLabel {{
    color: {c['text']};
    font-size: {f['base']}px;
}}

QLabel[class="heading"] {{
    font-size: {f['heading']}px;
    font-weight: bold;
    color: {c['text']};
}}

QLabel[class="subheading"] {{
    font-size: {f['subheading']}px;
    color: {c['text_muted']};
}}

QLabel[class="muted"] {{
    color: {c['text_muted']};
}}

/* Buttons */
QPushButton {{
    background-color: {c['primary']};
    color: {c['text']};
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: {f['base']}px;
    font-weight: bold;
    letter-spacing: 0.3px;
    min-height: 44px;
    min-width: 44px;
}}

QPushButton:hover {{
    background-color: {c['tertiary']};
}}

QPushButton:pressed {{
    background-color: {c['secondary']};
}}

QPushButton:focus {{
    outline: 3px solid {c['primary']};
    outline-offset: 2px;
}}

QPushButton:disabled {{
    background-color: {c['dark_input']};
    color: {c['text_muted']};
}}

QPushButton[class="secondary"] {{
    background-color: {c['secondary']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {c['tertiary']};
}}

QPushButton[class="text"] {{
    background-color: transparent;
    color: {c.get('primary_text', c['primary'])};
}}

QPushButton[class="text"]:hover {{
    background-color: rgba(162, 59, 132, 0.1);
}}

/* Input fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c['dark_input']};
    color: {c['text']};
    border: 2px solid {c['dark_card']};
    border-radius: 10px;
    padding: 14px;
    font-size: {f['base']}px;
    min-height: 44px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {c['primary']};
    outline: none;
}}

QLineEdit:disabled {{
    background-color: {c['dark_bg']};
    color: {c['text_muted']};
}}

/* Combo boxes */
QComboBox {{
    background-color: {c['dark_input']};
    color: {c['text']};
    border: 2px solid {c['dark_card']};
    border-radius: 10px;
    padding: 14px;
    font-size: {f['base']}px;
    min-height: 44px;
}}

QComboBox:focus {{
    border-color: {c['primary']};
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
    background: {c['text']};
}}

QComboBox QAbstractItemView {{
    background-color: {c['dark_card']};
    color: {c['text']};
    border: 2px solid {c['primary']};
    selection-background-color: {c['primary']};
}}

/* Scroll areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {c['dark_bg']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {c['dark_input']};
    border-radius: 8px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c['primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {c['dark_bg']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c['dark_input']};
    border-radius: 8px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c['primary']};
}}

/* Cards */
QFrame[class="card"] {{
    background-color: {c['dark_card']};
    border: 1px solid {c.get('dark_border', '#1c2a4a')};
    border-radius: 12px;
    padding: 16px;
}}

QFrame[class="card"]:hover {{
    background-color: {c.get('dark_hover', '#1a2d50')};
}}

/* Progress bar */
QProgressBar {{
    background-color: {c['dark_input']};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {c['text']};
}}

QProgressBar::chunk {{
    background-color: {c['primary']};
    border-radius: 8px;
}}

/* Tabs */
QTabWidget::pane {{
    border: none;
    background-color: {c['dark_card']};
    border-radius: 10px;
}}

QTabBar::tab {{
    background-color: {c['dark_bg']};
    color: {c['text_muted']};
    padding: 14px 28px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-size: {f['base']}px;
    min-height: 44px;
}}

QTabBar::tab:selected {{
    background-color: {c['dark_card']};
    color: {c['text']};
}}

QTabBar::tab:hover {{
    color: {c.get('primary_text', c['primary'])};
}}

/* Check boxes */
QCheckBox {{
    color: {c['text']};
    font-size: {f['base']}px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 24px;
    height: 24px;
    border-radius: 4px;
    border: 2px solid {c['dark_input']};
    background-color: {c['dark_bg']};
}}

QCheckBox::indicator:checked {{
    background-color: {c['primary']};
    border-color: {c['primary']};
}}

QCheckBox::indicator:focus {{
    outline: 3px solid {c['primary']};
    outline-offset: 2px;
}}

/* Radio buttons */
QRadioButton {{
    color: {c['text']};
    font-size: {f['base']}px;
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 24px;
    height: 24px;
    border-radius: 12px;
    border: 2px solid {c['dark_input']};
    background-color: {c['dark_bg']};
}}

QRadioButton::indicator:checked {{
    background-color: {c['primary']};
    border-color: {c['primary']};
}}

/* Message boxes */
QMessageBox {{
    background-color: {c['dark_card']};
}}

QMessageBox QLabel {{
    color: {c['text']};
}}

/* Tooltips */
QToolTip {{
    background-color: {c['dark_card']};
    color: {c['text']};
    border: 1px solid {c['primary']};
    padding: 8px;
    border-radius: 4px;
    font-size: {max(f['base'] - 2, 12)}px;
}}

/* Menu */
QMenu {{
    background-color: {c['dark_card']};
    color: {c['text']};
    border: 1px solid {c['dark_input']};
    padding: 8px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {c['primary']};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {c['dark_input']};
}}

QSplitter::handle:hover {{
    background-color: {c['primary']};
}}
"""
    if enhanced_focus:
        stylesheet += f"""
/* Enhanced focus indicators */
*:focus {{
    outline: 4px solid {c.get('primary_text', c['primary'])} !important;
    outline-offset: 4px !important;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 3px solid {c.get('primary_text', c['primary'])} !important;
}}
"""

    if dyslexia_font:
        stylesheet += f"""
/* Dyslexia-friendly font adjustments */
* {{
    font-family: {font_family};
    letter-spacing: 0.5px;
    word-spacing: 2px;
}}
QLabel, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox,
QCheckBox, QRadioButton, QMenu, QToolTip {{
    line-height: 160%;
}}
"""

    return stylesheet


# Backward-compatible module-level constant (initial value with defaults)
MAIN_STYLESHEET = get_main_stylesheet()

# Card styles for dashboard
CARD_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_card']};
    border: 1px solid {COLORS['dark_border']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame:hover {{
    background-color: {COLORS['dark_hover']};
    border: 2px solid {COLORS['primary']};
}}
"""

# Chat message styles
USER_MESSAGE_STYLE = f"""
QFrame {{
    background-color: {COLORS['primary']};
    border: 1px solid {COLORS['tertiary']};
    border-radius: 16px;
    padding: 16px 20px;
    margin: 8px;
}}
"""

ASSISTANT_MESSAGE_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_card']};
    border: 1px solid {COLORS['dark_border']};
    border-radius: 16px;
    padding: 16px 20px;
    margin: 8px;
}}
"""

# Phase indicator styles
PHASE_COMPLETED_STYLE = f"""
QFrame {{
    background-color: {COLORS['success']};
    border-radius: 10px;
    padding: 10px;
}}
"""

PHASE_CURRENT_STYLE = f"""
QFrame {{
    background-color: {COLORS['primary']};
    border-radius: 10px;
    padding: 10px;
    border: 2px solid {COLORS['text']};
}}
"""

PHASE_PENDING_STYLE = f"""
QFrame {{
    background-color: {COLORS['dark_input']};
    border-radius: 10px;
    padding: 10px;
}}
"""


def get_focus_style() -> str:
    """Get focus indicator style."""
    return f"outline: 3px solid {COLORS['primary']}; outline-offset: 2px;"
