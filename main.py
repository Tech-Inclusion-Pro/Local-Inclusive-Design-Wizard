#!/usr/bin/env python3
"""
Inclusive Design Wizard
AI-powered accessibility consultation tool for educators.

This application guides educators through UDL and WCAG frameworks
to create inclusive learning experiences.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from config.settings import COLORS, APP_SETTINGS
from ui.main_window import MainWindow


def setup_palette(app: QApplication):
    """Set up the dark color palette."""
    palette = QPalette()

    # Base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["dark_bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["dark_input"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["primary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(COLORS["primary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["text"]))

    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(COLORS["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(COLORS["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(COLORS["text_muted"]))

    app.setPalette(palette)


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Set application info
    app.setApplicationName(APP_SETTINGS["app_name"])
    app.setApplicationVersion(APP_SETTINGS["version"])
    app.setOrganizationName("Inclusive Design")

    # Set up dark palette
    setup_palette(app)

    # Set default font
    font = app.font()
    font.setFamily("Arial")
    font.setPointSize(APP_SETTINGS["min_font_size"])
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
