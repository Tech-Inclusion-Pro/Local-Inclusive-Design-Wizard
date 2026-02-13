"""Chat interface for consultations."""

import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTextEdit, QSplitter, QProgressBar,
    QDialog, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor

from config.settings import COLORS, PHASES, PHASE_ORDER
from prompts.system_prompts import get_phase_reasoning
from core.ai_manager import AIManager
from core.conversation import ConversationManager


class ChatTutorialDialog(QDialog):
    """Interactive tutorial dialog for the chat page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chat Tutorial")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.current_step = 0
        self.steps = [
            {
                "title": "Welcome to Your Consultation",
                "content": (
                    "This is where you'll have a conversation with your AI accessibility consultant.\n\n"
                    "The AI will guide you through a series of questions based on UDL (Universal Design "
                    "for Learning) and WCAG (Web Content Accessibility Guidelines) frameworks.\n\n"
                    "Click 'Next' to learn how to use this page."
                )
            },
            {
                "title": "The Chat Area",
                "content": (
                    "The main chat area shows your conversation history.\n\n"
                    "  - Your messages appear on the right\n"
                    "  - AI responses appear on the left\n"
                    "  - The AI will ask questions to understand your needs\n\n"
                    "Answer the questions naturally - there are no wrong answers! "
                    "The more detail you provide, the better recommendations you'll receive."
                )
            },
            {
                "title": "Sending Messages",
                "content": (
                    "At the bottom of the chat, you'll find the message input area.\n\n"
                    "To send a message:\n"
                    "  1. Type your response in the text box\n"
                    "  2. Click 'Send' or press Enter\n\n"
                    "Take your time to think about each question. You can provide "
                    "as much or as little detail as you'd like."
                )
            },
            {
                "title": "Progress Sidebar",
                "content": (
                    "The sidebar on the right shows your consultation progress.\n\n"
                    "  - See which phases you've completed\n"
                    "  - Track your current position in the consultation\n"
                    "  - View helpful resource links\n\n"
                    "The consultation covers multiple phases to ensure comprehensive "
                    "accessibility recommendations."
                )
            },
            {
                "title": "Saving & Exporting",
                "content": (
                    "Your work is important! Here's how to preserve it:\n\n"
                    "  - 'Save' button: Saves your consultation to Recent Consultations "
                    "(appears for new consultations)\n"
                    "  - 'Export' button: Download your consultation as a Word document\n"
                    "  - '← Back' button: Return to the dashboard\n\n"
                    "Your conversation is automatically saved as you go."
                )
            },
            {
                "title": "Tips for Best Results",
                "content": (
                    "To get the most out of your consultation:\n\n"
                    "  - Be specific about your learning context and audience\n"
                    "  - Describe any known accessibility challenges\n"
                    "  - Mention the types of content you're creating\n"
                    "  - Ask follow-up questions if you need clarification\n\n"
                    "The AI is here to help - feel free to ask for more details "
                    "on any recommendation!\n\n"
                    "Click 'Finish' to start your consultation."
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


class AIWorker(QThread):
    """Worker thread for AI responses."""

    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, ai_manager: AIManager, message: str, phase_context: dict = None):
        super().__init__()
        self.ai_manager = ai_manager
        self.message = message
        self.phase_context = phase_context
        self._had_error = False

    def run(self):
        """Run the AI generation."""
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def generate():
                try:
                    async for chunk in self.ai_manager.generate_response(
                        self.message, self.phase_context
                    ):
                        self.chunk_received.emit(chunk)
                except Exception as e:
                    self._had_error = True
                    self.error.emit(f"AI generation error: {str(e)}")

            loop.run_until_complete(generate())

            # Only emit finished if no error occurred
            if not self._had_error:
                self.finished.emit()

        except Exception as e:
            self.error.emit(f"Worker error: {str(e)}")
        finally:
            if loop:
                try:
                    loop.close()
                except Exception:
                    pass


class MessageBubble(QFrame):
    """Chat message bubble widget."""

    def __init__(self, role: str, content: str, reasoning: dict = None):
        super().__init__()
        self.role = role
        self.reasoning = reasoning or {}
        self.setup_ui(content)

    def setup_ui(self, content: str):
        """Set up the message bubble UI."""
        is_user = self.role == "user"
        border_color = COLORS['tertiary'] if is_user else COLORS.get('dark_border', '#1c2a4a')

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary'] if is_user else COLORS['dark_card']};
                border: 1px solid {border_color};
                border-radius: 16px;
                padding: 16px 20px;
                margin: 8px 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Role label
        role_text = "You" if is_user else "AI Consultant"
        role_label = QLabel(role_text)
        role_label.setStyleSheet(f"font-weight: bold; font-size: 12px; color: {COLORS['text_muted']};")
        layout.addWidget(role_label)

        # Content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(content_label)

        # Accessibility
        self.setAccessibleName(f"{role_text} says: {content[:100]}...")

    def update_content(self, content: str):
        """Update the message content."""
        # Find the content label and update it
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.wordWrap():
                    widget.setText(content)
                    break

    def update_style(self):
        """Re-apply bubble style with current colors."""
        from config.settings import get_colors
        c = get_colors()
        is_user = self.role == "user"
        border_color = c['tertiary'] if is_user else c.get('dark_border', '#1c2a4a')
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['primary'] if is_user else c['dark_card']};
                border: 1px solid {border_color};
                border-radius: 16px;
                padding: 16px 20px;
                margin: 8px 0;
            }}
        """)


class PhaseIndicator(QFrame):
    """Phase progress indicator widget."""

    def __init__(self, phase_key: str, phase_name: str, status: str):
        super().__init__()
        self.phase_key = phase_key
        self.status = status
        self.setup_ui(phase_name)

    def setup_ui(self, phase_name: str):
        """Set up the indicator UI."""
        if self.status == "completed":
            bg_color = COLORS['success']
            icon = "✓"
        elif self.status == "current":
            bg_color = COLORS['primary']
            icon = "→"
        else:
            bg_color = COLORS['dark_input']
            icon = "○"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 10px 14px;
                margin: 2px 0;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(icon_label)

        name_label = QLabel(phase_name)
        name_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(name_label)

        layout.addStretch()

        # Accessibility
        status_text = "completed" if self.status == "completed" else "current" if self.status == "current" else "pending"
        self.setAccessibleName(f"{phase_name}: {status_text}")


class ReasoningDialog(QDialog):
    """Dialog showing AI reasoning and framework alignment."""

    def __init__(self, reasoning: dict, phase_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Reasoning")
        self.setModal(True)
        self.setMinimumSize(600, 550)
        self.setup_ui(reasoning, phase_name)

    def setup_ui(self, reasoning: dict, phase_name: str):
        """Set up the dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['dark_card']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title (fixed at top)
        title_container = QWidget()
        title_container.setStyleSheet(f"background-color: {COLORS['dark_card']};")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(24, 24, 24, 16)

        title = QLabel("AI Reasoning & Sources")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_layout.addWidget(title)

        subtitle = QLabel("Understanding how recommendations are generated")
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        title_layout.addWidget(subtitle)

        main_layout.addWidget(title_container)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 8, 24, 24)

        # Current phase section
        phase_section = self._create_section(
            "Current Phase",
            phase_name,
            COLORS['dark_input'],
            is_header=True
        )
        layout.addWidget(phase_section)

        # Framework Applied
        if reasoning.get("framework"):
            framework_section = self._create_section(
                "Framework Applied",
                reasoning["framework"],
                COLORS['dark_input'],
                highlight_color=COLORS['primary']
            )
            layout.addWidget(framework_section)

        # Connection to Your Task
        if reasoning.get("connection"):
            connection_section = self._create_section(
                "How This Connects to Your Task",
                reasoning["connection"],
                COLORS['dark_input']
            )
            layout.addWidget(connection_section)

        # Source Materials
        if reasoning.get("sources"):
            sources_section = QFrame()
            sources_section.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['dark_input']};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            sources_layout = QVBoxLayout(sources_section)
            sources_layout.setSpacing(8)

            sources_label = QLabel("Source Materials & Guidelines")
            sources_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            sources_layout.addWidget(sources_label)

            for source in reasoning["sources"]:
                source_item = QLabel(f"• {source}")
                source_item.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; padding-left: 8px;")
                source_item.setWordWrap(True)
                sources_layout.addWidget(source_item)

            layout.addWidget(sources_section)

        # Confidence Level
        if reasoning.get("confidence"):
            confidence_section = QFrame()
            confidence_section.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['dark_input']};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            confidence_layout = QVBoxLayout(confidence_section)
            confidence_layout.setSpacing(8)

            confidence_label = QLabel("Recommendation Confidence")
            confidence_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            confidence_layout.addWidget(confidence_label)

            # Confidence indicator
            confidence_row = QHBoxLayout()
            confidence_value = reasoning["confidence"]

            # Color based on confidence level
            if "High" in confidence_value:
                conf_color = COLORS['success']
            elif "Medium" in confidence_value:
                conf_color = COLORS['warning']
            else:
                conf_color = COLORS['text_muted']

            conf_badge = QLabel(confidence_value)
            conf_badge.setStyleSheet(f"""
                background-color: {conf_color};
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            """)
            conf_badge.setMaximumWidth(100)
            confidence_row.addWidget(conf_badge)
            confidence_row.addStretch()
            confidence_layout.addLayout(confidence_row)

            if reasoning.get("confidence_reason"):
                conf_reason = QLabel(reasoning["confidence_reason"])
                conf_reason.setWordWrap(True)
                conf_reason.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; margin-top: 8px;")
                confidence_layout.addWidget(conf_reason)

            layout.addWidget(confidence_section)

        # Why it matters
        if reasoning.get("why"):
            why_section = self._create_section(
                "Why This Matters for Disability Justice",
                reasoning["why"],
                COLORS['dark_input']
            )
            layout.addWidget(why_section)

        # Connected Principle
        if reasoning.get("principle"):
            principle_section = QFrame()
            principle_section.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['secondary']};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            principle_layout = QVBoxLayout(principle_section)

            principle_label = QLabel("Guiding Principle")
            principle_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            principle_layout.addWidget(principle_label)

            principle_text = QLabel(f'"{reasoning["principle"]}"')
            principle_text.setWordWrap(True)
            principle_text.setFont(QFont("Arial", 14))
            principle_text.setStyleSheet("font-style: italic;")
            principle_layout.addWidget(principle_text)

            layout.addWidget(principle_section)

        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Close button (fixed at bottom)
        btn_container = QWidget()
        btn_container.setStyleSheet(f"background-color: {COLORS['dark_card']};")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(24, 16, 24, 24)

        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(44)
        close_btn.setMinimumWidth(120)
        btn_layout.addWidget(close_btn)

        main_layout.addWidget(btn_container)

    def _create_section(self, label: str, content: str, bg_color: str,
                        highlight_color: str = None, is_header: bool = False) -> QFrame:
        """Create a styled section frame."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(4)

        section_label = QLabel(label)
        section_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        section_layout.addWidget(section_label)

        content_label = QLabel(content)
        content_label.setWordWrap(True)

        if is_header:
            content_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        elif highlight_color:
            content_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            content_label.setStyleSheet(f"color: {highlight_color};")
        else:
            content_label.setStyleSheet("font-size: 14px;")

        section_layout.addWidget(content_label)
        return section


class ChatWidget(QWidget):
    """Main chat interface widget."""

    back_to_dashboard = pyqtSignal()
    session_saved = pyqtSignal()

    def __init__(self, ai_manager: AIManager, conversation_manager: ConversationManager):
        super().__init__()
        self.ai = ai_manager
        self.conversation = conversation_manager
        self.current_ai_bubble = None
        self.ai_worker = None
        self.is_temporary = False
        self.current_response = ""
        self.setup_ui()

    def setup_ui(self):
        """Set up the chat UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Chat
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(24, 16, 16, 16)
        chat_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setProperty("class", "text")
        back_btn.clicked.connect(self.back_to_dashboard.emit)
        back_btn.setAccessibleName("Back to dashboard")
        back_btn.setMinimumHeight(44)
        header.addWidget(back_btn)

        self.session_title = QLabel("Consultation")
        self.session_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.addWidget(self.session_title)

        header.addStretch()

        # Save button (only visible for temporary/unsaved sessions)
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        self.save_btn.clicked.connect(self.save_session)
        self.save_btn.setAccessibleName("Save consultation to recent consultations")
        self.save_btn.setMinimumHeight(44)
        self.save_btn.hide()  # Hidden by default
        header.addWidget(self.save_btn)

        tutorial_btn = QPushButton("Tutorial")
        tutorial_btn.setProperty("class", "secondary")
        tutorial_btn.clicked.connect(self.show_tutorial)
        tutorial_btn.setAccessibleName("Open chat tutorial")
        tutorial_btn.setToolTip("Learn how to use this page")
        tutorial_btn.setMinimumHeight(44)
        header.addWidget(tutorial_btn)

        export_btn = QPushButton("Export")
        export_btn.setProperty("class", "secondary")
        export_btn.clicked.connect(self.export_session)
        export_btn.setAccessibleName("Export consultation to document")
        export_btn.setMinimumHeight(44)
        header.addWidget(export_btn)

        chat_layout.addLayout(header)

        # Messages area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messages_scroll.setAccessibleName("Chat messages")

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.addStretch()

        self.messages_scroll.setWidget(self.messages_container)
        chat_layout.addWidget(self.messages_scroll)

        # Input area
        input_area = QHBoxLayout()

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your response here...")
        self.message_input.setAccessibleName("Message input")
        self.message_input.setMaximumHeight(120)
        self.message_input.setMinimumHeight(60)
        self.message_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['dark_input']};
                color: {COLORS['text']};
                border: 1px solid {COLORS.get('dark_border', '#1c2a4a')};
                border-radius: 12px;
                padding: 14px;
                font-size: 16px;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        input_area.addWidget(self.message_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.setAccessibleName("Send message")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setMinimumHeight(60)
        self.send_btn.setMinimumWidth(100)
        input_area.addWidget(self.send_btn)

        chat_layout.addLayout(input_area)

        splitter.addWidget(chat_panel)

        # Right panel - Progress sidebar with scroll
        sidebar_container = QWidget()
        sidebar_container.setStyleSheet(f"""
            background-color: {COLORS['dark_card']};
            border-left: 1px solid {COLORS.get('dark_border', '#1c2a4a')};
        """)
        sidebar_container.setMinimumWidth(280)
        sidebar_container.setMaximumWidth(350)

        sidebar_container_layout = QVBoxLayout(sidebar_container)
        sidebar_container_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_container_layout.setSpacing(0)

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['dark_card']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['dark_input']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['primary']};
            }}
        """)

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(16)

        # Progress header
        progress_label = QLabel("Progress")
        progress_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        sidebar_layout.addWidget(progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAccessibleName("Consultation progress")
        self.progress_bar.setMinimumHeight(20)
        sidebar_layout.addWidget(self.progress_bar)

        self.progress_text = QLabel("0% complete")
        self.progress_text.setStyleSheet(f"color: {COLORS['text_muted']};")
        sidebar_layout.addWidget(self.progress_text)

        # Phase indicators
        phases_label = QLabel("Phases")
        phases_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        phases_label.setStyleSheet("margin-top: 16px;")
        sidebar_layout.addWidget(phases_label)

        self.phases_container = QWidget()
        self.phases_layout = QVBoxLayout(self.phases_container)
        self.phases_layout.setSpacing(4)
        sidebar_layout.addWidget(self.phases_container)

        sidebar_layout.addStretch()

        # AI Reasoning button
        self.reasoning_btn = QPushButton("AI Reasoning")
        self.reasoning_btn.setProperty("class", "secondary")
        self.reasoning_btn.clicked.connect(self.show_reasoning)
        self.reasoning_btn.setAccessibleName("View AI reasoning, sources, and confidence levels")
        self.reasoning_btn.setToolTip("See how the AI generates recommendations")
        self.reasoning_btn.setMinimumHeight(44)
        sidebar_layout.addWidget(self.reasoning_btn)

        # Resources link
        resources_label = QLabel("Resources")
        resources_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        resources_label.setStyleSheet("margin-top: 16px;")
        sidebar_layout.addWidget(resources_label)

        resources = [
            ("UDL Guidelines", "https://udlguidelines.cast.org"),
            ("WCAG 2.1", "https://www.w3.org/WAI/WCAG21/quickref/"),
            ("A11Y Project", "https://www.a11yproject.com"),
        ]

        for name, url in resources:
            link = QLabel(f'<a href="{url}" style="color: {COLORS["primary_text"]};">{name}</a>')
            link.setOpenExternalLinks(True)
            link.setStyleSheet("font-size: 14px;")
            sidebar_layout.addWidget(link)

        # Add sidebar to scroll area
        sidebar_scroll.setWidget(sidebar)
        sidebar_container_layout.addWidget(sidebar_scroll)

        splitter.addWidget(sidebar_container)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

    def load_session(self, session_id: int):
        """Load a session into the chat."""
        session = self.conversation.load_session(session_id)
        if not session:
            return

        self.is_temporary = False
        self.save_btn.hide()  # Hide save button for saved sessions

        self.session_title.setText(session.title or "Consultation")
        self.ai.set_consultation_type(session.template_type)
        self.ai.reset_conversation()

        # Clear existing messages
        while self.messages_layout.count() > 1:  # Keep the stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Load existing conversation
        for msg in self.conversation.get_conversation():
            bubble = MessageBubble(msg["role"], msg["content"], msg.get("reasoning"))
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

            # Restore AI history
            self.ai.add_to_history(msg["role"], msg["content"])

        self.update_progress()

        # If no messages, start with AI greeting
        if not self.conversation.get_conversation():
            self.start_consultation()

        self.scroll_to_bottom()

    def load_temporary_session(self):
        """Load a temporary session (not saved to database yet)."""
        session = self.conversation.current_session
        if not session:
            return

        self.is_temporary = True
        self.save_btn.show()  # Show save button for temporary sessions

        self.session_title.setText(session.title or "Consultation")
        self.ai.set_consultation_type(session.template_type)
        self.ai.reset_conversation()

        # Clear existing messages
        while self.messages_layout.count() > 1:  # Keep the stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.update_progress()

        # Start with AI greeting
        self.start_consultation()
        self.scroll_to_bottom()

    def save_session(self):
        """Save a temporary session to the database."""
        if not self.is_temporary:
            return

        saved_session = self.conversation.save_temporary_session()
        if saved_session:
            self.is_temporary = False
            self.save_btn.hide()
            self.session_saved.emit()

            QMessageBox.information(
                self,
                "Session Saved",
                "Your consultation has been saved to Recent Consultations."
            )

    def start_consultation(self):
        """Start the consultation with an AI greeting."""
        phase = self.conversation.get_current_phase()
        question = self.conversation.get_current_question()

        if question:
            greeting = f"Welcome! I'm your inclusive design consultant. Let's work together to create an accessible learning experience.\n\nTo get started, {question}"

            # Add AI message
            self.add_ai_message(greeting)

    def send_message(self):
        """Send user message and get AI response."""
        try:
            message = self.message_input.toPlainText().strip()
            if not message:
                return

            # Disable input while processing
            self.message_input.setEnabled(False)
            self.send_btn.setEnabled(False)

            # Add user message
            user_bubble = MessageBubble("user", message)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, user_bubble)

            # Save to conversation
            self.conversation.add_message("user", message)

            self.message_input.clear()
            self.scroll_to_bottom()

            # Get AI response
            self.get_ai_response(message)
        except Exception as e:
            # Re-enable input on error
            self.message_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            QMessageBox.warning(self, "Error", f"Failed to send message: {str(e)}")

    def get_ai_response(self, user_message: str):
        """Get response from AI."""
        try:
            # Advance the question tracker
            self.conversation.advance_question()

            # Get context for AI
            phase = self.conversation.get_current_phase()
            reasoning = self.conversation.get_phase_reasoning()
            next_question = self.conversation.get_current_question()

            # Build context
            phase_context = {
                "phase_name": phase.get("name", "Unknown"),
                "framework": reasoning.get("framework", "UDL/WCAG") if reasoning else "UDL/WCAG",
                "why": reasoning.get("why", "") if reasoning else "",
                "next_question": next_question
            }

            # Create placeholder bubble for streaming
            self.current_ai_bubble = MessageBubble("assistant", "Thinking...")
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.current_ai_bubble)
            self.current_response = ""

            # Start worker thread
            self.ai_worker = AIWorker(self.ai, user_message, phase_context)
            self.ai_worker.chunk_received.connect(self.on_chunk_received)
            self.ai_worker.finished.connect(self.on_response_finished)
            self.ai_worker.error.connect(self.on_response_error)
            self.ai_worker.start()
        except Exception as e:
            # Re-enable input on error
            self.message_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            if self.current_ai_bubble:
                self.current_ai_bubble.update_content(f"Error: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to get AI response: {str(e)}")

    @pyqtSlot(str)
    def on_chunk_received(self, chunk: str):
        """Handle received chunk from AI."""
        self.current_response += chunk
        if self.current_ai_bubble:
            self.current_ai_bubble.update_content(self.current_response)
        self.scroll_to_bottom()

    @pyqtSlot()
    def on_response_finished(self):
        """Handle AI response completion."""
        try:
            # Save message to conversation
            reasoning = self.conversation.get_phase_reasoning()
            self.conversation.add_message("assistant", self.current_response, reasoning)

            # Update progress
            self.update_progress()

            # Check if complete
            if self.conversation.is_complete():
                self.show_completion_message()
        except Exception as e:
            print(f"Error in on_response_finished: {e}")
        finally:
            # Always re-enable input
            self.message_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.message_input.setFocus()
            self.current_ai_bubble = None

    @pyqtSlot(str)
    def on_response_error(self, error: str):
        """Handle AI response error."""
        try:
            if self.current_ai_bubble:
                self.current_ai_bubble.update_content(f"Error: {error}\n\nPlease check your AI settings and try again.")
        except Exception as e:
            print(f"Error updating bubble: {e}")
        finally:
            self.message_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.current_ai_bubble = None

    def add_ai_message(self, content: str):
        """Add an AI message to the chat."""
        reasoning = self.conversation.get_phase_reasoning()
        bubble = MessageBubble("assistant", content, reasoning)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

        self.conversation.add_message("assistant", content, reasoning)
        self.scroll_to_bottom()

    def update_progress(self):
        """Update the progress indicators."""
        progress = self.conversation.get_progress()

        self.progress_bar.setValue(int(progress["percent"]))
        self.progress_text.setText(f"{int(progress['percent'])}% complete ({progress['completed_questions']}/{progress['total_questions']} questions)")

        # Update phase indicators
        while self.phases_layout.count():
            item = self.phases_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for phase_info in progress["phases"]:
            indicator = PhaseIndicator(
                phase_info["key"],
                phase_info["name"],
                phase_info["status"]
            )
            self.phases_layout.addWidget(indicator)

    def scroll_to_bottom(self):
        """Scroll messages to bottom."""
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_reasoning(self):
        """Show the AI reasoning dialog."""
        phase = self.conversation.get_current_phase()
        reasoning = self.conversation.get_phase_reasoning()

        dialog = ReasoningDialog(reasoning, phase["name"], self)
        dialog.exec()

    def show_completion_message(self):
        """Show completion message."""
        QMessageBox.information(
            self,
            "Consultation Complete",
            "Congratulations! You've completed this inclusive design consultation.\n\n"
            "You can export your session to a document for reference, or review the conversation above.\n\n"
            "Remember: Accessibility is an ongoing process. Continue gathering feedback from learners with disabilities!"
        )

    def export_session(self):
        """Export the session to DOCX."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Consultation",
            "inclusive_design_consultation.docx",
            "Word Document (*.docx)"
        )

        if filepath:
            if not filepath.endswith(".docx"):
                filepath += ".docx"

            success = self.conversation.export_to_docx(filepath)
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Consultation exported to:\n{filepath}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export consultation. Please try again."
                )

    def refresh_styles(self):
        """Re-apply styles after accessibility settings change."""
        # Update existing message bubbles with new colors
        for i in range(self.messages_layout.count()):
            item = self.messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageBubble):
                item.widget().update_style()

    def show_tutorial(self):
        """Show the chat tutorial."""
        dialog = ChatTutorialDialog(self)
        dialog.exec()
