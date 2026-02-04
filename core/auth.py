"""Authentication module with bcrypt."""

import bcrypt
from .database import DatabaseManager, User


class AuthManager:
    """Handle user authentication."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_user: User = None

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def register(self, email: str, password: str,
                 security_question_1: str = None, security_answer_1: str = None,
                 security_question_2: str = None, security_answer_2: str = None) -> tuple[bool, str]:
        """Register a new user."""
        if not email or not password:
            return False, "Email and password are required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not security_question_1 or not security_answer_1:
            return False, "Security question 1 is required"

        if not security_question_2 or not security_answer_2:
            return False, "Security question 2 is required"

        existing = self.db.get_user_by_email(email)
        if existing:
            return False, "An account with this email already exists"

        try:
            hashed = self.hash_password(password)
            user = self.db.create_user(
                email=email,
                password_hash=hashed,
                security_question_1=security_question_1,
                security_answer_1=security_answer_1,
                security_question_2=security_question_2,
                security_answer_2=security_answer_2
            )
            self.current_user = user
            return True, "Account created successfully"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    def get_security_questions(self, email: str) -> tuple[bool, str, str, str]:
        """Get security questions for a user by email."""
        user = self.db.get_user_by_email(email)
        if not user:
            return False, "No account found with this email", None, None

        if not user.security_question_1 or not user.security_question_2:
            return False, "No security questions set for this account", None, None

        return True, "Questions found", user.security_question_1, user.security_question_2

    def verify_security_answers(self, email: str, answer_1: str, answer_2: str) -> tuple[bool, str]:
        """Verify security question answers (case-insensitive)."""
        user = self.db.get_user_by_email(email)
        if not user:
            return False, "No account found with this email"

        # Compare answers case-insensitively
        if user.security_answer_1 and user.security_answer_2:
            if (answer_1.lower().strip() == user.security_answer_1.lower().strip() and
                answer_2.lower().strip() == user.security_answer_2.lower().strip()):
                return True, "Answers verified"

        return False, "Security answers do not match"

    def reset_password(self, email: str, new_password: str) -> tuple[bool, str]:
        """Reset a user's password."""
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"

        user = self.db.get_user_by_email(email)
        if not user:
            return False, "No account found with this email"

        try:
            hashed = self.hash_password(new_password)
            success = self.db.update_user_password(user.id, hashed)
            if success:
                return True, "Password reset successfully"
            return False, "Failed to reset password"
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"

    def login(self, email: str, password: str) -> tuple[bool, str]:
        """Log in an existing user."""
        if not email or not password:
            return False, "Email and password are required"

        user = self.db.get_user_by_email(email)
        if not user:
            return False, "No account found with this email"

        if not self.verify_password(password, user.password_hash):
            return False, "Incorrect password"

        self.current_user = user
        return True, "Login successful"

    def login_local_mode(self) -> tuple[bool, str]:
        """Enter local mode without account."""
        try:
            user = self.db.get_local_user()
            self.current_user = user
            return True, "Local mode activated"
        except Exception as e:
            return False, f"Failed to enter local mode: {str(e)}"

    def logout(self):
        """Log out the current user."""
        self.current_user = None

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None

    def get_current_user(self) -> User:
        """Get the current authenticated user."""
        return self.current_user

    def update_user_settings(self, settings: dict) -> bool:
        """Update current user's settings."""
        if not self.current_user:
            return False

        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.id == self.current_user.id).first()
            if user:
                current_settings = user.settings
                current_settings.update(settings)
                user.settings = current_settings
                session.commit()
                self.current_user = user
                return True
            return False
        finally:
            session.close()
