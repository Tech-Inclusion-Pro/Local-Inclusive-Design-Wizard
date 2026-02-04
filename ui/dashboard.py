"""Dashboard screen with session management."""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QDialog, QLineEdit,
    QComboBox, QMessageBox, QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from config.settings import COLORS
from prompts.system_prompts import CONSULTATION_TYPES
from core.database import DatabaseManager, Session
from core.auth import AuthManager


class NotesDialog(QDialog):
    """Dialog for viewing and adding notes to a session."""

    note_added = pyqtSignal(int, str)  # session_id, note_content

    def __init__(self, session_id: int, session_title: str, notes: list, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.notes = notes
        self.setWindowTitle(f"Notes - {session_title}")
        self.setModal(True)
        self.setMinimumSize(500, 450)
        self.setup_ui()

    def setup_ui(self):
        """Set up the notes dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_card']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QTextEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['dark_input']};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Session Notes")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Existing notes section
        notes_label = QLabel("Previous Notes")
        notes_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(notes_label)

        # Notes scroll area
        notes_scroll = QScrollArea()
        notes_scroll.setWidgetResizable(True)
        notes_scroll.setMaximumHeight(200)
        notes_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {COLORS['dark_input']};
                border-radius: 8px;
                background-color: {COLORS['dark_bg']};
            }}
        """)

        notes_container = QWidget()
        notes_layout = QVBoxLayout(notes_container)
        notes_layout.setSpacing(8)
        notes_layout.setContentsMargins(8, 8, 8, 8)

        if self.notes:
            for note in reversed(self.notes):  # Show newest first
                note_frame = QFrame()
                note_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['dark_input']};
                        border-radius: 6px;
                        padding: 8px;
                    }}
                """)
                note_layout = QVBoxLayout(note_frame)
                note_layout.setSpacing(4)
                note_layout.setContentsMargins(8, 8, 8, 8)

                # Timestamp
                timestamp = datetime.fromisoformat(note['timestamp'])
                time_label = QLabel(timestamp.strftime("%b %d, %Y at %I:%M %p"))
                time_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
                note_layout.addWidget(time_label)

                # Content
                content_label = QLabel(note['content'])
                content_label.setWordWrap(True)
                content_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
                note_layout.addWidget(content_label)

                notes_layout.addWidget(note_frame)
        else:
            empty_label = QLabel("No notes yet. Add your first note below!")
            empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-style: italic;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            notes_layout.addWidget(empty_label)

        notes_layout.addStretch()
        notes_scroll.setWidget(notes_container)
        layout.addWidget(notes_scroll)

        # Add new note section
        new_note_label = QLabel("Add New Note")
        new_note_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(new_note_label)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Type your note here...")
        self.note_input.setAccessibleName("New note input")
        self.note_input.setMinimumHeight(80)
        self.note_input.setMaximumHeight(120)
        layout.addWidget(self.note_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.reject)
        close_btn.setMinimumHeight(44)
        btn_layout.addWidget(close_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("Save Note")
        save_btn.clicked.connect(self.save_note)
        save_btn.setMinimumHeight(44)
        save_btn.setMinimumWidth(120)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def save_note(self):
        """Save the new note."""
        content = self.note_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Empty Note", "Please enter some text for your note.")
            return

        self.note_added.emit(self.session_id, content)
        self.accept()


class TutorialDialog(QDialog):
    """Interactive tutorial dialog for the dashboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard Tutorial")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.current_step = 0
        self.steps = [
            {
                "title": "Welcome to Inclusive Design Wizard!",
                "content": (
                    "This tutorial will guide you through the main features of the dashboard.\n\n"
                    "The Inclusive Design Wizard helps educators create accessible learning "
                    "experiences using UDL (Universal Design for Learning) and WCAG "
                    "(Web Content Accessibility Guidelines) frameworks.\n\n"
                    "Click 'Next' to continue."
                )
            },
            {
                "title": "Starting a New Consultation",
                "content": (
                    "Click the 'Start New Consultation' button to begin a new accessibility review.\n\n"
                    "You'll be asked to:\n"
                    "  1. Give your consultation a name\n"
                    "  2. Select the type of consultation\n\n"
                    "The AI assistant will then guide you through a series of questions "
                    "to help identify accessibility improvements for your learning materials."
                )
            },
            {
                "title": "Recent Consultations",
                "content": (
                    "Your previous consultations appear in the 'Recent Consultations' section.\n\n"
                    "Each card shows:\n"
                    "  - The consultation title (click to edit)\n"
                    "  - The consultation type\n"
                    "  - Current status (In Progress or Complete)\n"
                    "  - Last modified date\n\n"
                    "Click 'Open' to continue a consultation, or 'Delete' to remove it."
                )
            },
            {
                "title": "Settings",
                "content": (
                    "Click the 'Settings' button to configure your AI provider.\n\n"
                    "You can choose between:\n"
                    "  - Local AI (Ollama, LM Studio) - runs on your computer, more private\n"
                    "  - Cloud AI (OpenAI, Anthropic) - requires API key, more powerful\n\n"
                    "Use 'Test Connection' to verify your AI is working before starting."
                )
            },
            {
                "title": "You're Ready!",
                "content": (
                    "That's everything you need to get started!\n\n"
                    "Tips for best results:\n"
                    "  - Be specific about your learning context\n"
                    "  - Describe your learners' needs\n"
                    "  - Ask follow-up questions if needed\n\n"
                    "The AI will provide recommendations based on UDL principles and "
                    "WCAG guidelines to help make your content more accessible.\n\n"
                    "Click 'Finish' to close this tutorial."
                )
            }
        ]
        self.setup_ui()

    def setup_ui(self):
        """Set up the tutorial UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_card']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Step indicator
        self.step_indicator = QLabel()
        self.step_indicator.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        layout.addWidget(self.step_indicator)

        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Content
        self.content_label = QLabel()
        self.content_label.setFont(QFont("Arial", 14))
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet(f"color: {COLORS['text']}; line-height: 1.5;")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.content_label, 1)

        # Navigation buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setProperty("class", "secondary")
        self.prev_btn.clicked.connect(self.prev_step)
        self.prev_btn.setMinimumHeight(44)
        btn_layout.addWidget(self.prev_btn)

        btn_layout.addStretch()

        self.skip_btn = QPushButton("Skip Tutorial")
        self.skip_btn.setProperty("class", "text")
        self.skip_btn.clicked.connect(self.reject)
        self.skip_btn.setMinimumHeight(44)
        btn_layout.addWidget(self.skip_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setMinimumHeight(44)
        self.next_btn.setMinimumWidth(100)
        btn_layout.addWidget(self.next_btn)

        layout.addLayout(btn_layout)

        self.update_content()

    def update_content(self):
        """Update the dialog content for current step."""
        step = self.steps[self.current_step]
        self.step_indicator.setText(f"Step {self.current_step + 1} of {len(self.steps)}")
        self.title_label.setText(step["title"])
        self.content_label.setText(step["content"])

        # Update button states
        self.prev_btn.setEnabled(self.current_step > 0)

        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next")

    def next_step(self):
        """Go to next step or finish."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_content()
        else:
            self.accept()

    def prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_content()


class SessionCard(QFrame):
    """Card widget for displaying a session."""

    open_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    title_changed = pyqtSignal(int, str)
    notes_requested = pyqtSignal(int, str)  # session_id, session_title

    def __init__(self, session: Session):
        super().__init__()
        self.session_id = session.id
        self.session_title = session.title or "Untitled Consultation"
        self.original_title = self.session_title
        self.setup_ui(session)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def setup_ui(self, session: Session):
        """Set up the card UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_card']};
                border-radius: 12px;
                padding: 16px;
            }}
            QFrame:hover {{
                background-color: {COLORS['dark_input']};
            }}
        """)
        self.setMinimumWidth(250)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Content area - holds all text elements
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(6)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Editable Title
        self.title_input = QLineEdit(session.title or "Untitled Consultation")
        self.title_input.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['dark_input']};
                border-radius: 6px;
                padding: 6px 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        self.title_input.setAccessibleName("Edit consultation title")
        self.title_input.editingFinished.connect(self.on_title_changed)
        content_layout.addWidget(self.title_input)

        # Type badge
        type_name = CONSULTATION_TYPES.get(session.template_type, {}).get("name", "Custom")
        type_label = QLabel(type_name)
        type_label.setStyleSheet(f"""
            background-color: {COLORS['secondary']};
            color: {COLORS['text']};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        """)
        type_label.setMaximumWidth(120)
        type_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        content_layout.addWidget(type_label)

        # Status
        status_text = "Complete" if session.completed else f"In Progress - {session.current_phase}"
        status = QLabel(status_text)
        status.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        status.setWordWrap(True)
        content_layout.addWidget(status)

        # Last modified
        if session.updated_at:
            modified = session.updated_at.strftime("%b %d, %Y at %I:%M %p")
        else:
            modified = "Unknown"
        modified_label = QLabel(f"Last modified: {modified}")
        modified_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        modified_label.setWordWrap(True)
        content_layout.addWidget(modified_label)

        layout.addWidget(content_widget)

        # Spacer to push buttons to bottom
        layout.addStretch(1)

        # Actions row - separate widget with fixed height
        actions_widget = QWidget()
        actions_widget.setFixedHeight(28)
        actions_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        actions = QHBoxLayout(actions_widget)
        actions.setSpacing(6)
        actions.setContentsMargins(0, 4, 0, 0)

        # Open button (green)
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
                min-height: 20px;
                max-height: 24px;
                min-width: 40px;
                max-width: 50px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        open_btn.setFixedSize(50, 24)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.session_id))
        open_btn.setAccessibleName(f"Open {session.title}")
        actions.addWidget(open_btn)

        # Notes button
        notes_btn = QPushButton("Notes")
        notes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
                min-height: 20px;
                max-height: 24px;
                min-width: 45px;
                max-width: 55px;
            }}
            QPushButton:hover {{
                background-color: #5849c4;
            }}
        """)
        notes_btn.setFixedSize(55, 24)
        notes_btn.clicked.connect(lambda: self.notes_requested.emit(self.session_id, self.session_title))
        notes_btn.setAccessibleName(f"Notes for {session.title}")
        actions.addWidget(notes_btn)

        actions.addStretch()

        # Delete button (smaller text)
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['error']};
                border: 1px solid {COLORS['error']};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                min-height: 18px;
                max-height: 22px;
                min-width: 40px;
                max-width: 50px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
                color: white;
            }}
        """)
        delete_btn.setFixedSize(50, 22)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.session_id))
        delete_btn.setAccessibleName(f"Delete {session.title}")
        actions.addWidget(delete_btn)

        layout.addWidget(actions_widget)

        # Accessibility
        self.setAccessibleName(f"{session.title}. {type_name}. {status_text}")
        self.setAccessibleDescription("Use Open button to open this consultation")

    def on_title_changed(self):
        """Handle title edit completion."""
        new_title = self.title_input.text().strip()
        if new_title and new_title != self.original_title:
            self.title_changed.emit(self.session_id, new_title)
            self.original_title = new_title


class NewSessionDialog(QDialog):
    """Dialog for creating a new session."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start New Consultation")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_card']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Start New Consultation")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Session name
        name_label = QLabel("Session Name")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name for this consultation")
        self.name_input.setAccessibleName("Session name input")
        self.name_input.setMinimumHeight(48)
        layout.addWidget(self.name_input)

        # Consultation type
        type_label = QLabel("Consultation Type")
        layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.setAccessibleName("Select consultation type")
        self.type_combo.setMinimumHeight(48)

        for key, value in CONSULTATION_TYPES.items():
            self.type_combo.addItem(value["name"], key)

        layout.addWidget(self.type_combo)

        # Type description
        self.type_description = QLabel()
        self.type_description.setWordWrap(True)
        self.type_description.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
        layout.addWidget(self.type_description)

        self.type_combo.currentIndexChanged.connect(self.update_type_description)
        self.update_type_description()

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(48)
        btn_layout.addWidget(cancel_btn)

        start_btn = QPushButton("Start Consultation")
        start_btn.clicked.connect(self.accept)
        start_btn.setMinimumHeight(48)
        btn_layout.addWidget(start_btn)

        layout.addLayout(btn_layout)

    def update_type_description(self):
        """Update the description based on selected type."""
        type_key = self.type_combo.currentData()
        if type_key:
            prompt = CONSULTATION_TYPES.get(type_key, {}).get("prompt", "")
            # Get first sentence
            desc = prompt.split(".")[0] + "." if prompt else ""
            self.type_description.setText(desc)

    def get_values(self) -> tuple[str, str]:
        """Get the entered values."""
        name = self.name_input.text().strip() or "New Consultation"
        type_key = self.type_combo.currentData()
        return name, type_key


class DashboardWidget(QWidget):
    """Main dashboard widget."""

    open_session = pyqtSignal(int)
    new_session = pyqtSignal(str, str)
    quick_action = pyqtSignal(str, str)  # For temporary sessions (not auto-saved)
    open_settings = pyqtSignal()
    logout = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        super().__init__()
        self.db = db_manager
        self.auth = auth_manager
        self.setup_ui()

    def setup_ui(self):
        """Set up the dashboard UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
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

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()

        title_section = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setAccessibleName("Dashboard heading")
        title_section.addWidget(title)

        user = self.auth.get_current_user()
        if user:
            welcome = QLabel(f"Welcome back, {user.email or 'Local User'}")
            welcome.setStyleSheet(f"color: {COLORS['text_muted']};")
            title_section.addWidget(welcome)

        header.addLayout(title_section)
        header.addStretch()

        # Header buttons
        tutorial_btn = QPushButton("Tutorial")
        tutorial_btn.setProperty("class", "secondary")
        tutorial_btn.setAccessibleName("Open tutorial")
        tutorial_btn.setToolTip("Learn how to use the dashboard")
        tutorial_btn.clicked.connect(self.show_tutorial)
        tutorial_btn.setMinimumHeight(44)
        header.addWidget(tutorial_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.setProperty("class", "secondary")
        settings_btn.setAccessibleName("Open settings")
        settings_btn.clicked.connect(self.open_settings.emit)
        settings_btn.setMinimumHeight(44)
        header.addWidget(settings_btn)

        logout_btn = QPushButton("Log Out")
        logout_btn.setProperty("class", "text")
        logout_btn.clicked.connect(self.logout.emit)
        logout_btn.setMinimumHeight(44)
        header.addWidget(logout_btn)

        layout.addLayout(header)

        # Quick actions section
        actions_label = QLabel("Quick Actions")
        actions_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(actions_label)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)

        quick_actions = [
            ("Start New Consultation", "custom", "Begin a comprehensive accessibility review"),
        ]

        for name, type_key, tooltip in quick_actions:
            btn = QPushButton(name)
            btn.setToolTip(tooltip)
            btn.setAccessibleDescription(tooltip)
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(180)

            if type_key == "custom":
                # Primary button for main action
                pass
            else:
                btn.setProperty("class", "secondary")

            btn.clicked.connect(lambda checked, t=type_key, n=name: self.start_quick_session(t, n))
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Recent sessions section
        sessions_header = QHBoxLayout()

        sessions_label = QLabel("Recent Consultations")
        sessions_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        sessions_header.addWidget(sessions_label)

        layout.addLayout(sessions_header)

        # Sessions scroll area
        self.sessions_area = QScrollArea()
        self.sessions_area.setWidgetResizable(True)
        self.sessions_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sessions_area.setAccessibleName("Recent consultation sessions")
        self.sessions_area.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.sessions_container = QWidget()
        self.sessions_layout = QGridLayout(self.sessions_container)
        self.sessions_layout.setSpacing(16)
        # Set columns to stretch equally
        self.sessions_layout.setColumnStretch(0, 1)
        self.sessions_layout.setColumnStretch(1, 1)
        self.sessions_layout.setColumnStretch(2, 1)

        self.sessions_area.setWidget(self.sessions_container)
        layout.addWidget(self.sessions_area)

        # Add scroll content to main scroll area
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.load_sessions()

    def load_sessions(self):
        """Load and display user sessions."""
        # Clear existing cards
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        user = self.auth.get_current_user()
        if not user:
            return

        sessions = self.db.get_user_sessions(user.id)

        if not sessions:
            empty_label = QLabel("No consultations yet. Start one above!")
            empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 16px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sessions_layout.addWidget(empty_label, 0, 0)
            return

        # Display in grid (3 columns)
        for i, session in enumerate(sessions[:12]):  # Show last 12
            row = i // 3
            col = i % 3

            card = SessionCard(session)
            card.open_requested.connect(self.open_session.emit)
            card.delete_requested.connect(self.confirm_delete_session)
            card.title_changed.connect(self.save_session_title)
            card.notes_requested.connect(self.show_notes_dialog)

            self.sessions_layout.addWidget(card, row, col)

    def start_quick_session(self, type_key: str, name: str):
        """Start a quick session with preset type (temporary, not auto-saved)."""
        if type_key == "custom":
            self.show_new_session_dialog()
        else:
            title = f"{name} - {datetime.now().strftime('%b %d, %Y')}"
            self.quick_action.emit(title, type_key)

    def show_new_session_dialog(self):
        """Show dialog to create new session."""
        dialog = NewSessionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, type_key = dialog.get_values()
            self.new_session.emit(title, type_key)

    def confirm_delete_session(self, session_id: int):
        """Confirm and delete a session."""
        reply = QMessageBox.question(
            self,
            "Delete Consultation",
            "Are you sure you want to delete this consultation? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_session(session_id)
            self.load_sessions()

    def save_session_title(self, session_id: int, new_title: str):
        """Save updated session title."""
        self.db.update_session(session_id, title=new_title)

    def refresh(self):
        """Refresh the dashboard."""
        self.load_sessions()

    def show_tutorial(self):
        """Show the dashboard tutorial."""
        dialog = TutorialDialog(self)
        dialog.exec()

    def show_notes_dialog(self, session_id: int, session_title: str):
        """Show the notes dialog for a session."""
        notes = self.db.get_session_notes(session_id)
        dialog = NotesDialog(session_id, session_title, notes, self)
        dialog.note_added.connect(self.save_note)
        dialog.exec()

    def save_note(self, session_id: int, note_content: str):
        """Save a note to a session."""
        self.db.add_session_note(session_id, note_content)
        QMessageBox.information(
            self,
            "Note Saved",
            "Your note has been saved with a timestamp."
        )
