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


def setup_palette(app: QApplication):
    """Set up the dark color palette."""
    from config.settings import get_colors
    colors = get_colors()

    palette = QPalette()

    # Base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["dark_bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["dark_input"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["dark_card"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["text"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["text"]))

    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(colors["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(colors["text_muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(colors["text_muted"]))

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
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
