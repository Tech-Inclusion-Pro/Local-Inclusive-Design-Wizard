"""Settings panel for AI configuration."""

import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QRadioButton, QButtonGroup,
    QMessageBox, QStackedWidget, QDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from config.settings import COLORS
from config.ai_providers import AI_PROVIDERS
from core.ai_manager import AIManager


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
        self.test_worker = None
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(550, 500)
        self.setup_ui()

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
        ai_section = QFrame()
        ai_section.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
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

        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Buttons (fixed at bottom)
        btn_container = QWidget()
        btn_container.setStyleSheet(f"background-color: {COLORS['dark_bg']};")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(24, 16, 24, 16)

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
        provider_label = QLabel("Provider")
        layout.addWidget(provider_label)
        layout.addSpacing(8)

        self.cloud_provider = QComboBox()
        self.cloud_provider.setAccessibleName("Select cloud AI provider")
        self.cloud_provider.setMinimumHeight(36)

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
        if self.ai.api_key:
            self.api_key_input.setText(self.ai.api_key)
        key_layout.addWidget(self.api_key_input)

        show_key_btn = QPushButton("Show")
        show_key_btn.setProperty("class", "text")
        show_key_btn.setMaximumWidth(80)
        show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        key_layout.addWidget(show_key_btn)

        layout.addLayout(key_layout)
        layout.addSpacing(20)

        # Model selection
        model_label = QLabel("Model")
        layout.addWidget(model_label)
        layout.addSpacing(8)

        self.cloud_model = QComboBox()
        self.cloud_model.setAccessibleName("Select AI model")
        self.cloud_model.setMinimumHeight(36)
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

    def save_settings(self):
        """Save settings and close."""
        self.apply_settings_to_manager()
        self.settings_changed.emit()
        self.accept()
