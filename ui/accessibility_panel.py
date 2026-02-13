"""Accessibility options dialog panel."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QCheckBox, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.accessibility_manager import AccessibilityManager


class AccessibilityPanel(QDialog):
    """Dialog with accessibility preference controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = AccessibilityManager.instance()
        self.setWindowTitle("Accessibility Options")
        self.setMinimumSize(420, 500)
        self.setModal(True)
        self._setup_ui()
        self._sync_from_manager()

    def _setup_ui(self):
        c = self.manager.get_effective_colors()

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['dark_card']};
            }}
            QLabel {{
                color: {c['text']};
            }}
            QRadioButton, QCheckBox {{
                color: {c['text']};
                font-size: 15px;
                spacing: 10px;
            }}
            QRadioButton::indicator, QCheckBox::indicator {{
                width: 22px;
                height: 22px;
            }}
            QRadioButton::indicator {{
                border-radius: 11px;
                border: 2px solid {c['dark_input']};
                background-color: {c['dark_bg']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
            }}
            QCheckBox::indicator {{
                border-radius: 4px;
                border: 2px solid {c['dark_input']};
                background-color: {c['dark_bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Accessibility Options")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAccessibleName("Accessibility Options dialog")
        layout.addWidget(title)

        subtitle = QLabel("Adjust display and interaction settings")
        subtitle.setStyleSheet(f"color: {c['text_muted']}; font-size: 14px;")
        layout.addWidget(subtitle)

        # --- Font Size ---
        font_section = QLabel("Font Size")
        font_section.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(font_section)

        self.font_group = QButtonGroup(self)
        font_options = [
            ("small", "Small"),
            ("medium", "Medium (Default)"),
            ("large", "Large"),
            ("extra_large", "Extra Large"),
        ]
        for key, label_text in font_options:
            rb = QRadioButton(label_text)
            rb.setAccessibleName(f"Font size: {label_text}")
            rb.setProperty("scale_key", key)
            self.font_group.addButton(rb)
            layout.addWidget(rb)

        self.font_group.buttonClicked.connect(self._on_font_changed)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet(f"color: {c['dark_input']};")
        layout.addWidget(sep1)

        # --- High Contrast ---
        self.high_contrast_cb = QCheckBox("Enable high contrast mode")
        self.high_contrast_cb.setAccessibleName("Toggle high contrast mode")
        self.high_contrast_cb.toggled.connect(self._on_high_contrast_changed)
        layout.addWidget(self.high_contrast_cb)

        # --- Reduced Motion ---
        self.reduced_motion_cb = QCheckBox("Reduce motion and animations")
        self.reduced_motion_cb.setAccessibleName("Toggle reduced motion")
        self.reduced_motion_cb.toggled.connect(self._on_reduced_motion_changed)
        layout.addWidget(self.reduced_motion_cb)

        # --- Enhanced Focus ---
        self.enhanced_focus_cb = QCheckBox("Show enhanced focus indicators")
        self.enhanced_focus_cb.setAccessibleName("Toggle enhanced focus indicators")
        self.enhanced_focus_cb.toggled.connect(self._on_enhanced_focus_changed)
        layout.addWidget(self.enhanced_focus_cb)

        layout.addStretch()

        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setProperty("class", "secondary")
        reset_btn.setAccessibleName("Reset accessibility settings to defaults")
        reset_btn.clicked.connect(self._on_reset)
        reset_btn.setMinimumHeight(44)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setAccessibleName("Close accessibility options")
        close_btn.setMinimumHeight(44)
        close_btn.setMinimumWidth(100)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _sync_from_manager(self):
        """Set control states from current manager values."""
        # Font scale
        current_scale = self.manager.font_scale
        for btn in self.font_group.buttons():
            if btn.property("scale_key") == current_scale:
                btn.setChecked(True)
                break

        self.high_contrast_cb.setChecked(self.manager.high_contrast)
        self.reduced_motion_cb.setChecked(self.manager.reduced_motion)
        self.enhanced_focus_cb.setChecked(self.manager.enhanced_focus)

    def _on_font_changed(self, button):
        key = button.property("scale_key")
        if key:
            self.manager.set_font_scale(key)

    def _on_high_contrast_changed(self, checked):
        self.manager.set_high_contrast(checked)

    def _on_reduced_motion_changed(self, checked):
        self.manager.set_reduced_motion(checked)

    def _on_enhanced_focus_changed(self, checked):
        self.manager.set_enhanced_focus(checked)

    def _on_reset(self):
        self.manager.load_from_dict({})
        self._sync_from_manager()
