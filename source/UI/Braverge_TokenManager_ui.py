import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from github import Github
from cryptography.fernet import Fernet
import os

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
# Encryption Setup
# -----------------------------
KEY_FILE = "key.key"

def load_key():
    """Load or generate encryption key."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

ENCRYPTION_KEY = load_key()
CIPHER = Fernet(ENCRYPTION_KEY)

# -----------------------------
# GitHub JSON Helpers
# -----------------------------
def load_users_from_github():
    try:
        file = repo.get_contents(FILE_PATH, ref=BRANCH)
        content = file.decoded_content.decode("utf-8")
        users = json.loads(content)
        return users, file.sha
    except Exception:
        return {}, None

def save_users_to_github(users, sha=None):
    content = json.dumps(users, indent=4)
    if sha:
        repo.update_file(FILE_PATH, "Update users.json", content, sha, branch=BRANCH)
    else:
        repo.create_file(FILE_PATH, "Create users.json", content, branch=BRANCH)

def load_user_tokens(username):
    users, _ = load_users_from_github()
    if username in users:
        return users[username].get("tokens", [])
    return []

def save_user_tokens(username, tokens):
    users, sha = load_users_from_github()
    if username in users:
        users[username]["tokens"] = tokens
        save_users_to_github(users, sha)
    else:
        raise Exception("User not found.")

# -----------------------------
# Token Encryption Helpers
# -----------------------------
def encrypt_token(token: str) -> str:
    return CIPHER.encrypt(token.encode()).decode()

def decrypt_token(token_enc: str) -> str:
    return CIPHER.decrypt(token_enc.encode()).decode()

# -----------------------------
# Token Manager Window
# -----------------------------
class TokenManagerWindow(QWidget):
    def __init__(self, username, scale_factor=1.0):
        super().__init__()
        self.username = username
        self.scale_factor = scale_factor

        self.setWindowTitle(f"Braverge - Token Manager ({username})")
        self.resize(int(800 * scale_factor), int(600 * scale_factor))

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        title = QLabel(f"Manage Tokens for {username}")
        title.setFont(QFont("Arial", int(20 * scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.token_list = QListWidget()
        self.token_list.setFont(QFont("Consolas", int(12 * scale_factor)))
        self.token_list.setAlternatingRowColors(True)
        self.token_list.setSelectionMode(QListWidget.ExtendedSelection)

        self.load_tokens()

        self.add_btn = QPushButton("➕  Add Token")
        self.del_btn = QPushButton("🗑️  Delete Selected")
        self.add_btn.setFont(QFont("Arial", int(14 * scale_factor)))
        self.del_btn.setFont(QFont("Arial", int(14 * scale_factor)))

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(self.token_list, stretch=1)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.add_btn.clicked.connect(self.add_token)
        self.del_btn.clicked.connect(self.delete_token)

        # Styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f9f9f9;
                color: #222;
                font-size: {int(14 * scale_factor)}px;
            }}
            QListWidget {{
                border: 1px solid #888;
                border-radius: 8px;
                padding: {int(10 * scale_factor)}px;
                background-color: white;
            }}
            QPushButton {{
                background-color: #000;
                color: white;
                border-radius: 8px;
                padding: {int(10 * scale_factor)}px {int(18 * scale_factor)}px;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
        """)

    def load_tokens(self):
        encrypted_tokens = load_user_tokens(self.username)
        self.token_list.clear()
        if encrypted_tokens:
            for t in encrypted_tokens:
                try:
                    self.token_list.addItem(decrypt_token(t))
                except:
                    self.token_list.addItem("(Invalid Token)")
        else:
            self.token_list.addItem("(No tokens found)")

    def add_token(self):
        token, ok = QInputDialog.getText(self, "Add Token", "Enter new token:")
        if ok and token.strip():
            encrypted_token = encrypt_token(token.strip())
            tokens = load_user_tokens(self.username)
            tokens.append(encrypted_token)
            save_user_tokens(self.username, tokens)
            self.load_tokens()

    def delete_token(self):
        selected_items = self.token_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a token to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_items)} token(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        tokens = load_user_tokens(self.username)
        decrypted_tokens = [decrypt_token(t) for t in tokens]
        for item in selected_items:
            if item.text() in decrypted_tokens:
                idx = decrypted_tokens.index(item.text())
                tokens.pop(idx)
                decrypted_tokens.pop(idx)
        save_user_tokens(self.username, tokens)
        self.load_tokens()


