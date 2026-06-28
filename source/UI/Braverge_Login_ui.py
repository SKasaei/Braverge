import os
import json
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QStackedWidget,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from github import Github

from UI.Braverge_home_ui import HomeWidget



# -----------------------------
# GitHub Configuration
# -----------------------------
GITHUB_TOKEN = "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"
REPO_OWNER = "sajadkasaei"
REPO_NAME = "Braverge-Tool"
FILE_PATH = "user/users.json"
BRANCH = "main"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")


# -----------------------------
# Helpers for JSON-based users
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users_from_github():
    """Load users.json from GitHub"""
    try:
        file = repo.get_contents(FILE_PATH, ref=BRANCH)
        content = file.decoded_content.decode("utf-8")
        users = json.loads(content)
        return users, file.sha
    except Exception:
        # If file doesn't exist or empty
        return {}, None


def save_users_to_github(users, sha=None):
    """Save updated users.json to GitHub"""
    content = json.dumps(users, indent=4)
    if sha:
        repo.update_file(FILE_PATH, "Update users.json", content, sha, branch=BRANCH)
    else:
        repo.create_file(FILE_PATH, "Create users.json", content, branch=BRANCH)


def register_user(username, password_hash):
    users, sha = load_users_from_github()
    if username in users:
        raise Exception("Username already exists.")
    users[username] = {"password": password_hash, "tokens": []}
    save_users_to_github(users, sha)


def verify_user(username, password_hash):
    users, _ = load_users_from_github()
    if username in users and users[username]["password"] == password_hash:
        
        return True
    return False


# -----------------------------
# PyQt5 UI
# -----------------------------
class LoginPage(QWidget):
    def __init__(self, stacked_widget, scale_factor):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.scale_factor = scale_factor

        layout = QVBoxLayout()
        layout.setSpacing(int(15 * scale_factor))
        layout.setContentsMargins(int(50 * scale_factor), int(40 * scale_factor),
                                  int(50 * scale_factor), int(40 * scale_factor))

        title = QLabel("Braverge Login")
        title.setFont(QFont("Arial", int(18 * scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Arial", int(12 * scale_factor)))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", int(12 * scale_factor)))

        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont("Arial", int(12 * scale_factor)))
        self.register_btn = QPushButton("New User? Register")
        self.register_btn.setFont(QFont("Arial", int(12 * scale_factor)))

        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.go_to_register)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        try:
            if verify_user(username, hash_password(password)):
                QMessageBox.information(self, "Welcome", f"Login successful. Hello {username}!")
                # Close stacked widget
                self.parent().hide()
                # Open main HomeWidget
                self.main_window = HomeWidget("TokenAccess", username, self.scale_factor)
                self.main_window.show()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_to_register(self):
        self.stacked_widget.setCurrentIndex(1)


class RegisterPage(QWidget):
    def __init__(self, stacked_widget, scale_factor):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        layout.setSpacing(int(15 * scale_factor))
        layout.setContentsMargins(int(50 * scale_factor), int(40 * scale_factor),
                                  int(50 * scale_factor), int(40 * scale_factor))

        title = QLabel("Braverge Registration")
        title.setFont(QFont("Arial", int(18 * scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setFont(QFont("Arial", int(12 * scale_factor)))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", int(12 * scale_factor)))

        self.register_btn = QPushButton("Register")
        self.register_btn.setFont(QFont("Arial", int(12 * scale_factor)))
        self.back_btn = QPushButton("Back to Login")
        self.back_btn.setFont(QFont("Arial", int(12 * scale_factor)))

        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

        self.register_btn.clicked.connect(self.register)
        self.back_btn.clicked.connect(self.go_back)

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both fields.")
            return

        try:
            register_user(username, hash_password(password))
            QMessageBox.information(self, "Success", "User registered successfully!")
            self.stacked_widget.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)


class MainWindow(QStackedWidget):
    def __init__(self, scale_factor):
        super().__init__()
        self.login_page = LoginPage(self, scale_factor)
        self.register_page = RegisterPage(self, scale_factor)

        self.addWidget(self.login_page)
        self.addWidget(self.register_page)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                color: black;
                font-size: {int(14 * scale_factor)}px;
            }}
            QLineEdit {{
                padding: {int(8 * scale_factor)}px;
                border: 1px solid black;
                border-radius: 5px;
            }}
            QPushButton {{
                background-color: black;
                color: white;
                padding: {int(8 * scale_factor)}px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
        """)

    def center_on_screen(self):
        """Centers the window on the current screen."""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
