"""Database models and setup."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


def get_data_directory() -> Path:
    """Get the appropriate data directory for the application."""
    # Use ~/Library/Application Support on macOS
    if sys.platform == "darwin":
        app_support = Path.home() / "Library" / "Application Support" / "Inclusive Design Wizard"
    else:
        # Fallback for other platforms
        app_support = Path.home() / ".inclusive-design-wizard"

    app_support.mkdir(parents=True, exist_ok=True)
    return app_support


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_local_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings_json = Column(Text, default="{}")
    security_question_1 = Column(String(255), nullable=True)
    security_answer_1 = Column(String(255), nullable=True)
    security_question_2 = Column(String(255), nullable=True)
    security_answer_2 = Column(String(255), nullable=True)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    @property
    def settings(self) -> dict:
        return json.loads(self.settings_json or "{}")

    @settings.setter
    def settings(self, value: dict):
        self.settings_json = json.dumps(value)


class Session(Base):
    """Consultation session model."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Consultation")
    template_type = Column(String(50), default="custom")
    current_phase = Column(String(50), default="context")
    current_question_index = Column(Integer, default=0)
    conversation_json = Column(Text, default="[]")
    decisions_json = Column(Text, default="{}")
    notes_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")

    @property
    def conversation(self) -> list:
        return json.loads(self.conversation_json or "[]")

    @conversation.setter
    def conversation(self, value: list):
        self.conversation_json = json.dumps(value)

    @property
    def decisions(self) -> dict:
        return json.loads(self.decisions_json or "{}")

    @decisions.setter
    def decisions(self, value: dict):
        self.decisions_json = json.dumps(value)

    @property
    def notes(self) -> list:
        return json.loads(self.notes_json or "[]")

    @notes.setter
    def notes(self, value: list):
        self.notes_json = json.dumps(value)

    def add_note(self, content: str):
        """Add a timestamped note."""
        notes_list = self.notes
        notes_list.append({
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.notes = notes_list

    def add_message(self, role: str, content: str, reasoning: dict = None):
        """Add a message to the conversation."""
        conv = self.conversation
        conv.append({
            "role": role,
            "content": content,
            "reasoning": reasoning or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        self.conversation = conv


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use the proper application data directory
            data_dir = get_data_directory()
            self.db_path = data_dir / "inclusive_design.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)

        # Run migrations for new columns
        self._migrate_database()

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _migrate_database(self):
        """Add new columns if they don't exist."""
        from sqlalchemy import inspect, text
        inspector = inspect(self.engine)

        # Check if users table has security question columns
        user_columns = [col['name'] for col in inspector.get_columns('users')]

        with self.engine.connect() as conn:
            if 'security_question_1' not in user_columns:
                conn.execute(text('ALTER TABLE users ADD COLUMN security_question_1 VARCHAR(255)'))
            if 'security_answer_1' not in user_columns:
                conn.execute(text('ALTER TABLE users ADD COLUMN security_answer_1 VARCHAR(255)'))
            if 'security_question_2' not in user_columns:
                conn.execute(text('ALTER TABLE users ADD COLUMN security_question_2 VARCHAR(255)'))
            if 'security_answer_2' not in user_columns:
                conn.execute(text('ALTER TABLE users ADD COLUMN security_answer_2 VARCHAR(255)'))
            conn.commit()

        # Check if sessions table has notes column
        session_columns = [col['name'] for col in inspector.get_columns('sessions')]

        with self.engine.connect() as conn:
            if 'notes_json' not in session_columns:
                conn.execute(text('ALTER TABLE sessions ADD COLUMN notes_json TEXT DEFAULT "[]"'))
            conn.commit()

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def create_user(self, email: str = None, password_hash: str = None, is_local: bool = False,
                    security_question_1: str = None, security_answer_1: str = None,
                    security_question_2: str = None, security_answer_2: str = None) -> User:
        """Create a new user."""
        session = self.get_session()
        try:
            user = User(
                email=email,
                password_hash=password_hash,
                is_local_mode=is_local,
                security_question_1=security_question_1,
                security_answer_1=security_answer_1.lower() if security_answer_1 else None,
                security_question_2=security_question_2,
                security_answer_2=security_answer_2.lower() if security_answer_2 else None
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def get_local_user(self) -> User:
        """Get or create local mode user."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.is_local_mode == True).first()
            if not user:
                user = User(is_local_mode=True)
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def create_session(self, user_id: int, title: str, template_type: str) -> Session:
        """Create a new consultation session."""
        session = self.get_session()
        try:
            new_session = Session(
                user_id=user_id,
                title=title,
                template_type=template_type
            )
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
            return new_session
        finally:
            session.close()

    def get_user_sessions(self, user_id: int) -> list:
        """Get all sessions for a user."""
        session = self.get_session()
        try:
            return session.query(Session).filter(
                Session.user_id == user_id
            ).order_by(Session.updated_at.desc()).all()
        finally:
            session.close()

    def get_session_by_id(self, session_id: int) -> Session:
        """Get session by ID."""
        session = self.get_session()
        try:
            return session.query(Session).filter(Session.id == session_id).first()
        finally:
            session.close()

    def update_session(self, session_id: int, **kwargs):
        """Update session fields."""
        db_session = self.get_session()
        try:
            sess = db_session.query(Session).filter(Session.id == session_id).first()
            if sess:
                for key, value in kwargs.items():
                    if hasattr(sess, key):
                        setattr(sess, key, value)
                db_session.commit()
        finally:
            db_session.close()

    def delete_session(self, session_id: int):
        """Delete a session."""
        session = self.get_session()
        try:
            sess = session.query(Session).filter(Session.id == session_id).first()
            if sess:
                session.delete(sess)
                session.commit()
        finally:
            session.close()

    def add_session_note(self, session_id: int, note_content: str):
        """Add a timestamped note to a session."""
        db_session = self.get_session()
        try:
            sess = db_session.query(Session).filter(Session.id == session_id).first()
            if sess:
                sess.add_note(note_content)
                db_session.commit()
        finally:
            db_session.close()

    def get_session_notes(self, session_id: int) -> list:
        """Get all notes for a session."""
        db_session = self.get_session()
        try:
            sess = db_session.query(Session).filter(Session.id == session_id).first()
            return sess.notes if sess else []
        finally:
            db_session.close()

    def update_user_password(self, user_id: int, new_password_hash: str) -> bool:
        """Update a user's password."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.password_hash = new_password_hash
                session.commit()
                return True
            return False
        finally:
            session.close()
