"""Settings panel for AI configuration."""

import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QRadioButton, QButtonGroup,
    QCheckBox, QMessageBox, QStackedWidget, QDialog, QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from config.settings import COLORS
from config.ai_providers import AI_PROVIDERS
from core.ai_manager import AIManager
from ui.accessibility_manager import AccessibilityManager


class ConnectionTestWorker(QThread):
    """Worker thread for testing AI connection."""

    finished = pyqtSignal(bool, str)

    def __init__(self, ai_manager: AIManager):
        super().__init__()
        self.ai_manager = ai_manager

    def run(self):
        """Run the connection test."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(self.ai_manager.test_connection())
        self.finished.emit(success, message)


class SettingsDialog(QDialog):
    """Settings dialog for AI configuration."""

    settings_changed = pyqtSignal()

    def __init__(self, ai_manager: AIManager, parent=None):
        super().__init__(parent)
        self.ai = ai_manager
        self.a11y_manager = AccessibilityManager.instance()
        self.test_worker = None
        self._a11y_snapshot = None
        self._reverted = False
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(550, 600)
        self.setup_ui()

        # Snapshot current state and enable live preview
        self._a11y_snapshot = self.a11y_manager.to_dict()
        self.a11y_manager.preview_mode = True

        # Connect live preview signals AFTER syncing controls
        self._connect_live_preview()

        # Update dialog itself when settings change
        self.a11y_manager.settings_changed.connect(self._refresh_dialog_styles)

    def setup_ui(self):
        """Set up the settings UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_bg']};
            }}
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

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll content widget
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # AI Provider Section
        self.ai_section = QFrame()
        ai_section = self.ai_section
        ai_section.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
                border: 1px solid {COLORS.get('dark_border', '#1c2a4a')};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        ai_layout = QVBoxLayout(ai_section)
        ai_layout.setSpacing(16)

        ai_title = QLabel("AI Provider")
        ai_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        ai_layout.addWidget(ai_title)

        # Provider type selection
        type_layout = QHBoxLayout()

        self.local_radio = QRadioButton("Local AI (Recommended)")
        self.local_radio.setAccessibleName("Use local AI provider")
        self.local_radio.setChecked(self.ai.provider_type == "local")
        type_layout.addWidget(self.local_radio)

        self.cloud_radio = QRadioButton("Cloud AI")
        self.cloud_radio.setAccessibleName("Use cloud AI provider")
        self.cloud_radio.setChecked(self.ai.provider_type == "cloud")
        type_layout.addWidget(self.cloud_radio)

        type_layout.addStretch()

        self.type_group = QButtonGroup()
        self.type_group.addButton(self.local_radio, 0)
        self.type_group.addButton(self.cloud_radio, 1)
        self.type_group.idToggled.connect(self.on_type_changed)

        ai_layout.addLayout(type_layout)

        # Privacy warning
        self.privacy_warning = QFrame()
        self.privacy_warning.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['warning']};
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel {{
                color: #000000;
            }}
        """)
        warning_layout = QVBoxLayout(self.privacy_warning)
        warning_label = QLabel("⚠️ Cloud AI sends your data to external servers. For maximum privacy, use local AI.")
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)
        self.privacy_warning.setVisible(self.ai.provider_type == "cloud")
        ai_layout.addWidget(self.privacy_warning)

        # Stacked widget for local/cloud options
        self.options_stack = QStackedWidget()

        # Local options
        local_options = self.create_local_options()
        self.options_stack.addWidget(local_options)

        # Cloud options
        cloud_options = self.create_cloud_options()
        self.options_stack.addWidget(cloud_options)

        self.options_stack.setCurrentIndex(0 if self.ai.provider_type == "local" else 1)
        ai_layout.addWidget(self.options_stack)

        # Test connection button
        test_layout = QHBoxLayout()

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setProperty("class", "secondary")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setMinimumHeight(44)
        test_layout.addWidget(self.test_btn)

        self.test_status = QLabel("")
        self.test_status.setStyleSheet(f"color: {COLORS['text_muted']};")
        test_layout.addWidget(self.test_status)

        test_layout.addStretch()
        ai_layout.addLayout(test_layout)

        layout.addWidget(ai_section)

        # Accessibility Section
        self.a11y_section = QFrame()
        a11y_section = self.a11y_section
        a11y_section.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
                border: 1px solid {COLORS.get('dark_border', '#1c2a4a')};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        a11y_layout = QVBoxLayout(a11y_section)
        a11y_layout.setSpacing(8)

        a11y_title = QLabel("Accessibility")
        a11y_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        a11y_layout.addWidget(a11y_title)

        a11y_subtitle = QLabel("Adjust display and interaction settings")
        a11y_subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        a11y_layout.addWidget(a11y_subtitle)
        a11y_layout.addSpacing(8)

        # --- Visual Settings subsection ---
        visual_label = QLabel("Visual Settings")
        visual_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        a11y_layout.addWidget(visual_label)

        # High Contrast toggle
        self.high_contrast_cb = self._create_toggle_row(
            a11y_layout, "High Contrast Mode",
            "Increase contrast for better visibility")

        # Large Text toggle (font scale: medium vs large)
        self.large_text_cb = self._create_toggle_row(
            a11y_layout, "Large Text Mode",
            "Increase font size by 25%")

        # Reduced Motion toggle
        self.reduced_motion_cb = self._create_toggle_row(
            a11y_layout, "Reduced Motion",
            "Disable animations")

        # Enhanced Focus toggle
        self.enhanced_focus_cb = self._create_toggle_row(
            a11y_layout, "Enhanced Focus Indicators",
            "Larger, more visible focus outlines")

        # Dyslexia Font toggle
        self.dyslexia_font_cb = self._create_toggle_row(
            a11y_layout, "Dyslexia-Friendly Font",
            "Use OpenDyslexic font style")

        a11y_layout.addSpacing(4)

        # --- Color Vision subsection ---
        cv_label = QLabel("Color Vision")
        cv_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        a11y_layout.addWidget(cv_label)

        # Color Blind Mode dropdown
        cb_row = QFrame()
        cb_row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_bg']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        cb_row_layout = QVBoxLayout(cb_row)
        cb_row_layout.setSpacing(4)
        cb_row_layout.setContentsMargins(12, 12, 12, 12)

        cb_title = QLabel("Color Blindness Mode")
        cb_title.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; background: transparent;")
        cb_row_layout.addWidget(cb_title)

        cb_desc = QLabel("Adjust colors for color vision deficiency")
        cb_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        cb_row_layout.addWidget(cb_desc)

        self.color_blind_combo = QComboBox()
        self.color_blind_combo.setAccessibleName("Color blindness mode")
        self.color_blind_combo.setMinimumHeight(36)
        for mode_key, mode_label in AccessibilityManager.COLOR_BLIND_LABELS.items():
            self.color_blind_combo.addItem(mode_label, mode_key)

        cb_row_layout.addWidget(self.color_blind_combo)

        # Color preview swatch
        self.color_preview = QFrame()
        self.color_preview.setMinimumHeight(28)
        self.color_preview.setStyleSheet(self._build_preview_style("none"))
        cb_row_layout.addWidget(self.color_preview)

        self.color_blind_combo.currentIndexChanged.connect(self._on_color_blind_preview)

        a11y_layout.addWidget(cb_row)

        a11y_layout.addSpacing(4)

        # --- Cursor subsection ---
        cursor_label = QLabel("Cursor")
        cursor_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        a11y_layout.addWidget(cursor_label)

        # Custom Cursor dropdown
        cur_row = QFrame()
        cur_row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_bg']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        cur_row_layout = QVBoxLayout(cur_row)
        cur_row_layout.setSpacing(4)
        cur_row_layout.setContentsMargins(12, 12, 12, 12)

        cur_title = QLabel("Custom Cursor")
        cur_title.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; background: transparent;")
        cur_row_layout.addWidget(cur_title)

        cur_desc = QLabel("Choose a cursor style for better visibility")
        cur_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        cur_row_layout.addWidget(cur_desc)

        self.cursor_combo = QComboBox()
        self.cursor_combo.setAccessibleName("Custom cursor style")
        self.cursor_combo.setMinimumHeight(36)
        for cur_key, cur_label in AccessibilityManager.CUSTOM_CURSORS.items():
            self.cursor_combo.addItem(cur_label, cur_key)

        cur_row_layout.addWidget(self.cursor_combo)
        a11y_layout.addWidget(cur_row)

        a11y_layout.addSpacing(8)

        # Reset defaults button
        reset_a11y_btn = QPushButton("Reset to Defaults")
        reset_a11y_btn.setProperty("class", "text")
        reset_a11y_btn.setAccessibleName("Reset accessibility settings to defaults")
        reset_a11y_btn.clicked.connect(self._reset_accessibility)
        reset_a11y_btn.setMinimumHeight(36)
        reset_a11y_btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        a11y_layout.addWidget(reset_a11y_btn)

        layout.addWidget(a11y_section)

        # Sync accessibility controls from current manager state
        self._sync_accessibility_from_manager()

        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Buttons (fixed at bottom)
        btn_container = QWidget()
        btn_container.setStyleSheet(f"background-color: {COLORS['dark_bg']};")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(24, 20, 24, 20)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(48)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setMinimumHeight(48)
        btn_layout.addWidget(save_btn)

        main_layout.addWidget(btn_container)

    def create_local_options(self) -> QWidget:
        """Create local AI options panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        # Provider selection
        provider_label = QLabel("Provider")
        layout.addWidget(provider_label)
        layout.addSpacing(8)

        self.local_provider = QComboBox()
        self.local_provider.setAccessibleName("Select local AI provider")
        self.local_provider.setMinimumHeight(36)
        provider_label.setBuddy(self.local_provider)

        for key, config in AI_PROVIDERS["local"].items():
            self.local_provider.addItem(config["name"], key)

        # Set current
        current_idx = self.local_provider.findData(self.ai.provider)
        if current_idx >= 0:
            self.local_provider.setCurrentIndex(current_idx)

        self.local_provider.currentIndexChanged.connect(self.on_local_provider_changed)
        layout.addWidget(self.local_provider)
        layout.addSpacing(20)

        # Model selection
        model_label = QLabel("Model")
        layout.addWidget(model_label)
        layout.addSpacing(8)

        self.local_model = QComboBox()
        self.local_model.setAccessibleName("Select AI model")
        self.local_model.setMinimumHeight(36)
        self.local_model.setEditable(True)
        model_label.setBuddy(self.local_model)
        self.update_local_models()
        layout.addWidget(self.local_model)
        layout.addSpacing(20)

        # Custom endpoint
        endpoint_label = QLabel("Endpoint (optional)")
        layout.addWidget(endpoint_label)
        layout.addSpacing(8)

        self.local_endpoint = QLineEdit()
        self.local_endpoint.setPlaceholderText("http://localhost:11434")
        self.local_endpoint.setText(self.ai.base_url)
        self.local_endpoint.setAccessibleName("Custom API endpoint")
        self.local_endpoint.setMinimumHeight(36)
        endpoint_label.setBuddy(self.local_endpoint)
        layout.addWidget(self.local_endpoint)
        layout.addSpacing(16)

        # Instructions
        instructions = QLabel(
            "For Ollama: Install from ollama.ai and run 'ollama pull llama3.2'\n"
            "For LM Studio: Download from lmstudio.ai and start the server"
        )
        instructions.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        return widget

    def create_cloud_options(self) -> QWidget:
        """Create cloud AI options panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        # Provider selection
        cloud_provider_label = QLabel("Provider")
        layout.addWidget(cloud_provider_label)
        layout.addSpacing(8)

        self.cloud_provider = QComboBox()
        self.cloud_provider.setAccessibleName("Select cloud AI provider")
        self.cloud_provider.setMinimumHeight(36)
        cloud_provider_label.setBuddy(self.cloud_provider)

        for key, config in AI_PROVIDERS["cloud"].items():
            self.cloud_provider.addItem(config["name"], key)

        self.cloud_provider.currentIndexChanged.connect(self.on_cloud_provider_changed)
        layout.addWidget(self.cloud_provider)
        layout.addSpacing(20)

        # API Key
        key_label = QLabel("API Key")
        layout.addWidget(key_label)
        layout.addSpacing(8)

        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setAccessibleName("API key input")
        self.api_key_input.setMinimumHeight(36)
        key_label.setBuddy(self.api_key_input)
        if self.ai.api_key:
            self.api_key_input.setText(self.ai.api_key)
        key_layout.addWidget(self.api_key_input)

        show_key_btn = QPushButton("Show")
        show_key_btn.setProperty("class", "text")
        show_key_btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        key_layout.addWidget(show_key_btn)

        layout.addLayout(key_layout)
        layout.addSpacing(20)

        # Model selection
        cloud_model_label = QLabel("Model")
        layout.addWidget(cloud_model_label)
        layout.addSpacing(8)

        self.cloud_model = QComboBox()
        self.cloud_model.setAccessibleName("Select AI model")
        self.cloud_model.setMinimumHeight(36)
        cloud_model_label.setBuddy(self.cloud_model)
        self.update_cloud_models()
        layout.addWidget(self.cloud_model)
        layout.addSpacing(16)

        return widget

    def on_type_changed(self, button_id: int, checked: bool):
        """Handle provider type change."""
        if checked:
            self.options_stack.setCurrentIndex(button_id)
            self.privacy_warning.setVisible(button_id == 1)

    def on_local_provider_changed(self, index: int):
        """Handle local provider change."""
        self.update_local_models()
        provider_key = self.local_provider.currentData()
        config = AI_PROVIDERS["local"].get(provider_key, {})
        self.local_endpoint.setPlaceholderText(config.get("base_url", ""))

    def on_cloud_provider_changed(self, index: int):
        """Handle cloud provider change."""
        self.update_cloud_models()

    def update_local_models(self):
        """Update local model dropdown."""
        self.local_model.clear()
        provider_key = self.local_provider.currentData()
        config = AI_PROVIDERS["local"].get(provider_key, {})

        for model in config.get("models", []):
            self.local_model.addItem(model)

        # Set current model
        idx = self.local_model.findText(self.ai.model)
        if idx >= 0:
            self.local_model.setCurrentIndex(idx)

    def update_cloud_models(self):
        """Update cloud model dropdown."""
        self.cloud_model.clear()
        provider_key = self.cloud_provider.currentData()
        config = AI_PROVIDERS["cloud"].get(provider_key, {})

        for model in config.get("models", []):
            self.cloud_model.addItem(model)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        sender = self.sender()
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            sender.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            sender.setText("Show")

    def test_connection(self):
        """Test the AI connection."""
        self.apply_settings_to_manager()

        self.test_btn.setEnabled(False)
        self.test_status.setText("Testing...")
        self.test_status.setStyleSheet(f"color: {COLORS['text_muted']};")

        self.test_worker = ConnectionTestWorker(self.ai)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.start()

    @pyqtSlot(bool, str)
    def on_test_finished(self, success: bool, message: str):
        """Handle test completion."""
        self.test_btn.setEnabled(True)

        if success:
            self.test_status.setText(f"✓ {message}")
            self.test_status.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.test_status.setText(f"✗ {message}")
            self.test_status.setStyleSheet(f"color: {COLORS['error']};")

    def apply_settings_to_manager(self):
        """Apply current UI settings to AI manager."""
        if self.local_radio.isChecked():
            self.ai.configure(
                provider_type="local",
                provider=self.local_provider.currentData(),
                model=self.local_model.currentText(),
                base_url=self.local_endpoint.text() or None
            )
        else:
            self.ai.configure(
                provider_type="cloud",
                provider=self.cloud_provider.currentData(),
                model=self.cloud_model.currentText(),
                api_key=self.api_key_input.text()
            )

    def _create_toggle_row(self, parent_layout, title: str, description: str) -> QCheckBox:
        """Create a toggle row with title, description, and checkbox (MycoFolio style)."""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_bg']};
                border-radius: 8px;
                padding: 8px;
                margin-bottom: 4px;
            }}
        """)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 10, 12, 10)
        row_layout.setSpacing(12)

        # Text area (title + description)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; background: transparent;")
        text_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)

        row_layout.addLayout(text_layout, 1)

        # Checkbox toggle
        cb = QCheckBox()
        cb.setAccessibleName(title)
        cb.setMinimumWidth(28)
        row_layout.addWidget(cb, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        parent_layout.addWidget(row)
        return cb

    def _sync_accessibility_from_manager(self):
        """Set accessibility control states from current manager values."""
        if not self.a11y_manager:
            return
        # Large text: "large" or "extra_large" = checked, otherwise unchecked
        self.large_text_cb.setChecked(
            self.a11y_manager.font_scale in ("large", "extra_large"))
        self.high_contrast_cb.setChecked(self.a11y_manager.high_contrast)
        self.reduced_motion_cb.setChecked(self.a11y_manager.reduced_motion)
        self.enhanced_focus_cb.setChecked(self.a11y_manager.enhanced_focus)
        self.dyslexia_font_cb.setChecked(self.a11y_manager.dyslexia_font)

        # Color blind combo
        cb_idx = self.color_blind_combo.findData(self.a11y_manager.color_blind_mode)
        if cb_idx >= 0:
            self.color_blind_combo.setCurrentIndex(cb_idx)
        self.color_preview.setStyleSheet(
            self._build_preview_style(self.a11y_manager.color_blind_mode))

        # Cursor combo
        cur_idx = self.cursor_combo.findData(self.a11y_manager.custom_cursor)
        if cur_idx >= 0:
            self.cursor_combo.setCurrentIndex(cur_idx)

    def _connect_live_preview(self):
        """Connect accessibility controls to push changes live to the manager."""
        self.high_contrast_cb.toggled.connect(self._push_a11y_to_manager)
        self.large_text_cb.toggled.connect(self._push_a11y_to_manager)
        self.reduced_motion_cb.toggled.connect(self._push_a11y_to_manager)
        self.enhanced_focus_cb.toggled.connect(self._push_a11y_to_manager)
        self.dyslexia_font_cb.toggled.connect(self._push_a11y_to_manager)
        self.color_blind_combo.currentIndexChanged.connect(self._push_a11y_to_manager)
        self.cursor_combo.currentIndexChanged.connect(self._push_a11y_to_manager)

    def _push_a11y_to_manager(self):
        """Push current UI control values to the accessibility manager for live preview."""
        if not self.a11y_manager:
            return
        self.a11y_manager.set_font_scale(
            "large" if self.large_text_cb.isChecked() else "medium")
        self.a11y_manager.set_high_contrast(self.high_contrast_cb.isChecked())
        self.a11y_manager.set_reduced_motion(self.reduced_motion_cb.isChecked())
        self.a11y_manager.set_enhanced_focus(self.enhanced_focus_cb.isChecked())
        self.a11y_manager.set_dyslexia_font(self.dyslexia_font_cb.isChecked())

        cb_key = self.color_blind_combo.currentData()
        if cb_key:
            self.a11y_manager.set_color_blind_mode(cb_key)

        cur_key = self.cursor_combo.currentData()
        if cur_key:
            self.a11y_manager.set_custom_cursor(cur_key)

    def _reset_accessibility(self):
        """Reset accessibility controls and push defaults to the manager."""
        # Block signals to avoid multiple intermediate pushes
        for widget in (self.high_contrast_cb, self.large_text_cb,
                       self.reduced_motion_cb, self.enhanced_focus_cb,
                       self.dyslexia_font_cb):
            widget.blockSignals(True)
        self.color_blind_combo.blockSignals(True)
        self.cursor_combo.blockSignals(True)

        self.high_contrast_cb.setChecked(False)
        self.large_text_cb.setChecked(False)
        self.reduced_motion_cb.setChecked(False)
        self.enhanced_focus_cb.setChecked(False)
        self.dyslexia_font_cb.setChecked(False)
        self.color_blind_combo.setCurrentIndex(0)
        self.cursor_combo.setCurrentIndex(0)
        self.color_preview.setStyleSheet(self._build_preview_style("none"))

        # Unblock signals
        for widget in (self.high_contrast_cb, self.large_text_cb,
                       self.reduced_motion_cb, self.enhanced_focus_cb,
                       self.dyslexia_font_cb):
            widget.blockSignals(False)
        self.color_blind_combo.blockSignals(False)
        self.cursor_combo.blockSignals(False)

        # Push defaults to the manager (triggers live refresh)
        self.a11y_manager.load_from_dict({})

    def _revert_if_needed(self):
        """Restore the accessibility snapshot unless already reverted."""
        if self._reverted:
            return
        self._reverted = True
        self.a11y_manager.preview_mode = False
        if self._a11y_snapshot is not None:
            self.a11y_manager.load_from_dict(self._a11y_snapshot)

    def _refresh_dialog_styles(self):
        """Re-apply inline styles within this dialog during live preview."""
        from config.settings import get_colors
        colors = get_colors()
        section_style = f"""
            QFrame {{
                background-color: {colors['dark_card']};
                border: 1px solid {colors.get('dark_border', '#1c2a4a')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        self.ai_section.setStyleSheet(section_style)
        self.a11y_section.setStyleSheet(section_style)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['dark_bg']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {colors['dark_bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['dark_input']};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['primary']};
            }}
        """)

        # Apply custom cursor to this dialog so preview is visible here too
        cursor = self.a11y_manager.get_cursor()
        if cursor is None:
            self.unsetCursor()
        else:
            self.setCursor(cursor)

    def _on_color_blind_preview(self, index):
        """Update the color preview swatch when a color blind mode is selected."""
        key = self.color_blind_combo.itemData(index)
        if key:
            self.color_preview.setStyleSheet(self._build_preview_style(key))

    @staticmethod
    def _build_preview_style(mode_key: str) -> str:
        """Build a CSS swatch showing the color palette for a given mode."""
        overrides = AccessibilityManager.COLOR_BLIND_MODES.get(mode_key, {})
        colors = dict(COLORS)
        if overrides:
            colors.update(overrides)
        return (
            f"background: qlineargradient("
            f"x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {colors['primary']}, "
            f"stop:0.2 {colors['secondary']}, "
            f"stop:0.4 {colors['tertiary']}, "
            f"stop:0.6 {colors['success']}, "
            f"stop:0.8 {colors['warning']}, "
            f"stop:1 {colors['error']});"
            f"border-radius: 6px; min-height: 32px;"
        )

    def save_settings(self):
        """Save settings and close — accessibility changes are already live."""
        self.apply_settings_to_manager()
        # End preview mode and persist
        self._reverted = True  # prevent revert on close
        self.a11y_manager.preview_mode = False
        self.settings_changed.emit()
        self.accept()

    def reject(self):
        """Cancel — revert accessibility changes to snapshot."""
        self._revert_if_needed()
        super().reject()

    def closeEvent(self, event):
        """Handle window close (X button) — revert if not saved."""
        self._revert_if_needed()
        super().closeEvent(event)
