import math
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QAbstractItemView,
    QHBoxLayout, QMessageBox, QInputDialog, QLineEdit, QFormLayout, QApplication, QTreeView, QDialog, QDialogButtonBox, QListWidgetItem
)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtGui, QtWidgets

from github import Github, GithubException
from controller.myGithub import myGithub
import json

# -----------------------------
# GitHub Configuration
# -----------------------------
GITHUB_TOKEN = "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"
REPO_OWNER = "sajadkasaei"
REPO_NAME = "Braverge-Tool"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# -----------------------------
# Branch Manager Window
# -----------------------------
class BranchManagerWindow(QWidget):
    def __init__(self, Current_USER, githubobj,  workSpacePath, Selected_Dir_tree_view_selected_item , Selected_Repository_name, branchID, pivotID, collaborators, branchPattern, branchScope, Versions_ID, tree_Model, tree_view_clicked):
        super().__init__()
        self.workSpacePath = workSpacePath
        self.Selected_Dir_tree_view_selected_item=Selected_Dir_tree_view_selected_item
        self.Selected_Repository_name = Selected_Repository_name
        self.githubobj = myGithub("empty")
        self.githubobj = githubobj
        self.Versions_ID = Versions_ID
        self.Current_USER = Current_USER
        self.highlighted_items = []

        self.usernames_Scope = []

        # --- Responsive scaling based on screen size ---
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        width, height = screen_rect.width(), screen_rect.height()

        # Scale factor based on 1080p baseline
        self.scale_factor = round(min(width / 1920, height / 1080), 2)
        if self.scale_factor < 0.75:
            self.scale_factor = 0.75
        if self.scale_factor > 1.5:
            self.scale_factor = 1.5

        # --- Window setup ---
        self.setWindowTitle("Braverge Branch Manager")
        self.resize(int(1000 * self.scale_factor), int(700 * self.scale_factor))

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(
            int(40 * self.scale_factor), int(30 * self.scale_factor),
            int(40 * self.scale_factor), int(30 * self.scale_factor)
        )
        main_layout.setSpacing(int(25 * self.scale_factor))

        title = QLabel("Manage Braverge Branches")
        title.setFont(QFont("Arial", int(22 * self.scale_factor), QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # --- Branch list ---
        # self.branch_list = QListWidget()
        # self.branch_list.setFont(QFont("Consolas", int(13 * self.scale_factor)))
        # self.branch_list.setAlternatingRowColors(True)
        # self.branch_list.setSelectionMode(QListWidget.SingleSelection)

        self.contents_tree_view = QTreeView(self)
        self.contents_tree_view.setHeaderHidden(True)
        self.contents_tree_view.setAlternatingRowColors(True)
        # 🔒 Disable selection completely
        self.contents_tree_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.contents_tree_view.setFocusPolicy(Qt.NoFocus)
        # self.contents_tree_view.clicked.connect(self.on_branch_selected)
        self.contents_tree_view.setStyleSheet("""
            QTreeView {
                border: 1px solid #e6e9ef;
                border-radius: 8px;
                background: #fcfcfd;
                selection-background-color: #eaf2ff;
                alternate-background-color: #f7f9fb;
            }
            QTreeView::item:hover {
                background: #a5beff;
            }
        """)

        self.contents_tree_view.setModel(tree_Model)
        self.contents_tree_view.expandAll()

        self.highlight_hierarchy(tree_view_clicked)


        
        # --- Branch info form ---
        form_layout = QFormLayout()
        self.branch_id = QLineEdit()
        self.branch_id.setText(branchID)
        self.branch_id.setEnabled(False)
        self.Divergence_Point = QLineEdit()
        self.Divergence_Point.setText(pivotID)
        self.Divergence_Point.setEnabled(False)
        
        self.branch_pattern = QLineEdit()
        self.branch_pattern.setText(branchPattern)
        self.branch_pattern.setEnabled(False)
        self.branch_scope = QLineEdit()
        self.branch_scope.setText(branchScope)
        self.branch_scope.setEnabled(False)
        self.branch_collaborators = QLineEdit()
        self.branch_collaborators.setText(collaborators)
        self.branch_collaborators.setEnabled(False)

        form_layout.addRow("Branch ID:", self.branch_id)
        form_layout.addRow("Divergence Point:", self.Divergence_Point)
        form_layout.addRow("Branch Pattern:", self.branch_pattern)
        form_layout.addRow("Branch Scope:", self.branch_scope)
        form_layout.addRow("Collaborators (comma separated):", self.branch_collaborators)

        # --- Buttons ---
        btn_layout = QHBoxLayout()

        self.update_btn = QPushButton("💾 Update Info")
        self.create_btn = QPushButton("➕ Create Branch")
        self.delete_btn = QPushButton("🗑️ Delete Branch")
        self.Scope_btn = QPushButton("🧩 Toggle Scope")
        self.Pattern_btn = QPushButton("🔐 Toggle Pattern")
        self.set_collab_btn = QPushButton("🌍 Manage Collaborators")  # Unified collaborator management

        # Apply style and layout
        for b in [
            self.update_btn, self.create_btn, self.delete_btn,
            self.Scope_btn, self.Pattern_btn, self.set_collab_btn
        ]:
            b.setFont(QFont("Arial", int(14 * self.scale_factor)))
            b.setMinimumHeight(int(40 * self.scale_factor))
            btn_layout.addWidget(b)

        # --- Layout assembly ---
        main_layout.addWidget(title)
        main_layout.addWidget(self.contents_tree_view, stretch=1)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # --- Connect signals ---
        self.update_btn.clicked.connect(self.update_info_branch)
        self.create_btn.clicked.connect(self.create_branch)
        self.delete_btn.clicked.connect(self.delete_branch)
        self.Scope_btn.clicked.connect(self.update_branch_scope)
        self.Pattern_btn.clicked.connect(self.toggle_branch_pattern)
        self.set_collab_btn.clicked.connect(self.set_collaborators)  # ← unified collaborator manager

        # --- Style ---
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #fafafa;
                font-size: {int(14 * self.scale_factor)}px;
            }}
            QListWidget {{
                border: 1px solid #aaa;
                border-radius: 8px;
                background-color: white;
                padding: {int(10 * self.scale_factor)}px;
            }}
            QPushButton {{
                background-color: #000;
                color: white;
                border-radius: 8px;
                padding: {int(8 * self.scale_factor)}px {int(14 * self.scale_factor)}px;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
            QLineEdit {{
                padding: {int(6 * self.scale_factor)}px;
                border: 1px solid #777;
                border-radius: 5px;
            }}
        """)

        index = self.contents_tree_view.currentIndex()
        #tempitem = self.contents_tree_view.model().itemFromIndex(index)
        #self.item = tempitem.copy()
        self.item = self.contents_tree_view.model().itemFromIndex(index)
        

    def update_info_branch(self):
        
        self.githubobj.update_branch_metadata(self.workSpacePath + "/", self.Selected_Dir_tree_view_selected_item, self.Selected_Repository_name,
                                              self.branch_id.text(), self.Divergence_Point.text(), self.branch_collaborators.text(),
                                              self.branch_pattern.text(), self.branch_scope.text(), self.Versions_ID)
        QMessageBox.information(
            self,
            "Update Complete 🚀",
            "Boom! Your information is now up to date!"
        )

    def delete_branch(self):
        
        cleanup_confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirmation",
            "Do you want to delete highlighted branches and versions?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if cleanup_confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            # Perform deletion
            self.githubobj.delete_branch(
                self.Selected_Dir_tree_view_selected_item,
                self.Selected_Repository_name,
                self.highlighted_items
            )

            QtWidgets.QMessageBox.information(
                self,
                "Delete Complete 🚀",
                "Branch deletion completed successfully!"
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Operation Cancelled 🛑",
                "All good! The operation was cancelled — nothing was changed."
            )



    def create_branch(self):
        
        Selected_file_tree_view_selected_item = self.item.data(Qt.UserRole)

        cleanup_confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Do you want to create new branch on {self.item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if cleanup_confirm == QMessageBox.StandardButton.Yes:
        
            Json_branchInfo_file = ""
            workSpacePath= self.workSpacePath + "/"
            self.repoContents = self.githubobj.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
            while self.repoContents:
                oneItem = self.repoContents.pop(0)
                if "Branch_Info" in oneItem.name:
                    Json_branchInfo_file = json.loads(oneItem.decoded_content)
                    if Selected_file_tree_view_selected_item in Json_branchInfo_file['Versions_ID']:
                    
                        modelselectedfile_name = Selected_file_tree_view_selected_item + ".xmi"
                        #accsess to the repository
                        myFile = '/' + Json_branchInfo_file['branch_ID'] + ".xmi"
                        self.githubobj.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, modelselectedfile_name)

                        list_vid = []
                        for vId in Json_branchInfo_file['Versions_ID']:
                            list_vid.append(vId)
                        list_vid.reverse()
                        
                        for vId in list_vid:
                            if vId == Selected_file_tree_view_selected_item:
                                
                                break

                            else:
                                myFile = '/' + vId + "Version_Info.json"
                                self.githubobj.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Version_Info.json")
                                self.githubobj.create_previous_version(self.workSpacePath, modelselectedfile_name , modelselectedfile_name)
                                
                        self.githubobj.create_new__short_branch(workSpacePath, modelselectedfile_name, self.Selected_Dir_tree_view_selected_item, Selected_file_tree_view_selected_item , self.Selected_Repository_name, self.Current_USER)
                        QMessageBox.information(self, "Success", f"Version '{Selected_file_tree_view_selected_item}' successfully downloaded.")
                        QMessageBox.information(self, "Information", f"Switching in local branch.")
                    
                        break  # Exit 
        else:
            QMessageBox.information(
                self,
                "Operation Cancelled 🛑",
                "All good! The operation was cancelled — nothing was changed."
            )

    def toggle_text_field(self, widget, option1, option2, message):
        current = widget.text()
        widget.setText(option2 if current == option1 else option1)
        QMessageBox.information(self, "Info", message)

    def update_branch_scope(self):
        # Get current branch_scope text
        current_scope_text = self.branch_scope.text()
        
        # Extract usernames if branch_scope is not "full"
        if current_scope_text.lower() != "full" and current_scope_text.strip():
            usernames = [u.strip() for u in current_scope_text.split(",")]
        else:
            usernames = []

        # Open dialog with current scope and usernames
        dialog = BranchDialog(
            current_scope=current_scope_text, 
            usernames=usernames, 
            scale_factor=self.scale_factor
        )

        if dialog.exec_() == QDialog.Accepted:
            new_scope, new_usernames = dialog.get_data()
            if not new_usernames:  # Empty or None
                self.branch_scope.setText("full")
                self.usernames = []
            else:
                self.usernames = new_usernames
                self.branch_scope.setText(", ".join(new_usernames))

    def toggle_branch_pattern(self):
        self.toggle_text_field(self.branch_pattern, "long", "short", "Branch pattern is updated.")

    def on_branch_selected(self, index):
            self.clear_highlights(self.contents_tree_view.model())
            if not index.isValid():
                return
            # Get the selected item from the model
            item = self.contents_tree_view.model().itemFromIndex(index)
            if not item:
                return
            # Display name (e.g., "Version 1")
            branch_name = item.text()
            # Original ID stored in UserRole
            branch_id = item.data(Qt.UserRole)
            # Get parent item (if any)
            parent_item = item.parent()
            parent_branch_name = parent_item.text() if parent_item else "MASTER"
            parent_branch_id = parent_item.data(Qt.UserRole) if parent_item else None

    def clear_highlights(self, model):
        """Remove background color from all items in the model."""
        root = model.invisibleRootItem()
        stack = [root]
        while stack:
            item = stack.pop()
            item.setBackground(QtGui.QBrush(QtCore.Qt.transparent))
            for row in range(item.rowCount()):
                stack.append(item.child(row))

    def highlight_descendants(self, item, level=1):
        """
        Recursively highlight all children and deeper descendants,
        and store custom filenames in self.highlighted_items based on
        each item's text() and data(Qt.UserRole).
        """

        # Choose color based on depth level
        if level == 1:
            color = QtGui.QColor(255, 255, 180)  # light yellow for children
        elif level == 2:
            color = QtGui.QColor(200, 255, 200)  # pale green for grandchildren
        else:
            color = QtGui.QColor(220, 255, 255)  # very light cyan for deeper nodes

        brush = QtGui.QBrush(color)

        for row in range(item.rowCount()):
            child = item.child(row)
            if not child:
                continue

            # --- Highlight the item ---
            child.setBackground(brush)

            # --- Retrieve its data and text ---
            data = child.data(QtCore.Qt.UserRole)
            text = child.text()

            if data is not None:
                if text == "Branch":
                    # Remove Version_Info.json if it was previously added
                    version_file = f"{data}Version_Info.json"
                    if version_file in self.highlighted_items:
                        self.highlighted_items.remove(version_file)

                    # Append Branch files
                    self.highlighted_items.append(f"{data}Branch_Info.json")
                    self.highlighted_items.append(f"{data}.xmi")
                else:
                    # Append Version_Info.json only if .xmi not already added
                    if f"{data}.xmi" not in self.highlighted_items:
                        self.highlighted_items.append(f"{data}Version_Info.json")

            # --- Recurse deeper ---
            self.highlight_descendants(child, level + 1)

    def highlight_hierarchy(self, tree_view_clicked):
        """
        Highlights:
        - The clicked node (bright yellow)
        - Its parent (dark yellow)
        - All descendants of the parent (progressively lighter colors)
        Also builds self.highlighted_items — a list of filenames based on each node's
        text() and data(Qt.UserRole).
        """

        model = self.contents_tree_view.model()
        if not model:
            return

        # --- 1. Clear old highlights ---
        self.clear_highlights(model)

        # --- 2. Reset the collected items list ---
        self.highlighted_items = []

        # --- 3. Get clicked item ---
        index = tree_view_clicked
        item = model.itemFromIndex(index)
        if not item:
            return

        # --- 4. Highlight the clicked item ---
        clicked_brush = QtGui.QBrush(QtGui.QColor(255, 255, 100))  # bright yellow
        item.setBackground(clicked_brush)
        self.contents_tree_view.setCurrentIndex(index)

        # Add the clicked item to the tracking list
        data = item.data(QtCore.Qt.UserRole)
        text = item.text()
        if data is not None:
            if text == "Branch":
                # Remove Version_Info.json if it was previously added
                version_file = f"{data}Version_Info.json"
                if version_file in self.highlighted_items:
                    self.highlighted_items.remove(version_file)

                # Append Branch files
                self.highlighted_items.append(f"{data}Branch_Info.json")
                self.highlighted_items.append(f"{data}.xmi")
            else:
                # Append Version_Info.json only if .xmi not already added
                if f"{data}.xmi" not in self.highlighted_items:
                    self.highlighted_items.append(f"{data}Version_Info.json")

        # --- 5. Highlight parent (if exists) ---
        parent_index = index.parent()
        if parent_index.isValid():
            parent_item = model.itemFromIndex(parent_index)
            if parent_item:
                parent_brush = QtGui.QBrush(QtGui.QColor(255, 204, 0))  # dark yellow
                parent_item.setBackground(parent_brush)

                data = parent_item.data(QtCore.Qt.UserRole)
                text = parent_item.text()
                if data is not None:
                    if text == "Branch":
                        # Remove Version_Info.json if it was previously added
                        version_file = f"{data}Version_Info.json"
                        if version_file in self.highlighted_items:
                            self.highlighted_items.remove(version_file)

                        # Append Branch files
                        self.highlighted_items.append(f"{data}Branch_Info.json")
                        self.highlighted_items.append(f"{data}.xmi")
                    else:
                        if f"{data}.xmi" not in self.highlighted_items:
                            self.highlighted_items.append(f"{data}Version_Info.json")

                # Scroll to parent
                self.contents_tree_view.scrollTo(parent_index, QtWidgets.QAbstractItemView.PositionAtCenter)

                # --- 6. Highlight all descendants (children, grandchildren, etc.) ---
                self.highlight_descendants(parent_item, level=1)
        else:
            # Root node — highlight its descendants directly
            self.highlight_descendants(item, level=1)

        # --- 7. Ensure the clicked node is visible ---
        self.contents_tree_view.scrollTo(index, QtWidgets.QAbstractItemView.PositionAtCenter)

        # --- 8. Optional: Remove duplicates (if needed) ---
        self.highlighted_items = list(dict.fromkeys(self.highlighted_items))

    def set_collaborators(self):
        # --- Determine current mode ---
        current_text = self.branch_collaborators.text().strip()
        is_public = current_text.lower() == "public"

        # --- Main mode selection ---
        options = ["🌍 Public (Everyone can access)", "🔒 Private (Manage collaborators)"]
        default_index = 0 if is_public else 1

        choice, ok = QInputDialog.getItem(
            self,
            "Collaborator Settings",
            "Choose branch access level:",
            options,
            default_index,
            False
        )

        if not ok:
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return

        # --- Handle Public Mode ---
        if "Public" in choice:
            self.branch_collaborators.setText("public")
            QMessageBox.information(
                self,
                "Public Access 🌍",
                "This branch is now public — everyone can access it!\n"
                "Collaborator management is disabled."
            )
            return

        # --- Handle Private Mode ---
        collaborators = [
            c.strip() for c in current_text.split(",")
            if c.strip() and c.lower() != "public"
        ]

        # Submenu for managing collaborators
        action_options = ["➕ Add Collaborator", "❌ Remove Collaborator", "🧾 View Collaborators", "⬅️ Done"]
        while True:
            action, ok = QInputDialog.getItem(
                self,
                "Private Access Management",
                f"Current collaborators:\n{', '.join(collaborators) if collaborators else '(none)'}\n\nSelect an action:",
                action_options,
                0,
                False
            )

            if not ok or "Done" in action:
                break

            # --- Add collaborator ---
            if "Add" in action:
                collab, ok = QInputDialog.getText(self, "Add Collaborator", "Enter username:")
                if not ok or not collab.strip():
                    continue
                collab = collab.strip()
                if collab in collaborators:
                    QMessageBox.information(self, "Info", f"Collaborator '{collab}' already exists.")
                    continue
                collaborators.append(collab)
                QMessageBox.information(self, "Success 🎉", f"Collaborator '{collab}' added.")

            # --- Remove collaborator ---
            elif "Remove" in action:
                if not collaborators:
                    QMessageBox.warning(self, "Empty List", "There are no collaborators to remove.")
                    continue

                collab, ok = QInputDialog.getItem(
                    self,
                    "Remove Collaborator",
                    "Select a collaborator to remove:",
                    collaborators,
                    0,
                    False
                )
                if ok and collab:
                    collaborators.remove(collab)
                    QMessageBox.information(self, "Removed ✅", f"Collaborator '{collab}' removed.")

            # --- View collaborators ---
            elif "View" in action:
                QMessageBox.information(
                    self,
                    "Current Collaborators",
                    ", ".join(collaborators) if collaborators else "No collaborators added yet."
                )

        # --- Update field ---
        self.branch_collaborators.setText(", ".join(collaborators))
        QMessageBox.information(
            self,
            "Private Access 🔒",
            f"Branch access limited to: {', '.join(collaborators) if collaborators else '(none)'}"
        )








# ------------------ Dialog Window ------------------
class BranchDialog(QDialog):
    def __init__(self, current_scope="", usernames=None, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.setWindowTitle("Manage Branch Scope")
        self.resize(int(350 * self.scale_factor), int(400 * self.scale_factor))

        self.branch_scope = current_scope
        self.usernames_Scope = usernames if usernames else []

        # --- Widgets ---
        self.user_list = QListWidget()
        self.user_list.setSelectionMode(QListWidget.MultiSelection)
        for user in self.usernames_Scope:
            self.user_list.addItem(user)
        self.user_list.setFont(QFont("Arial", int(12 * self.scale_factor)))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFont(QFont("Arial", int(12 * self.scale_factor)))

        self.add_button = QPushButton("➕ Add Username")
        self.add_button.setFont(QFont("Arial", int(12 * self.scale_factor)))
        self.add_button.clicked.connect(self.add_username)

        self.delete_button = QPushButton("❌ Delete Selected")
        self.delete_button.setFont(QFont("Arial", int(12 * self.scale_factor)))
        self.delete_button.clicked.connect(self.delete_username)

        self.full_button = QPushButton("🧩 Set Branch Scope to FULL")
        self.full_button.setFont(QFont("Arial", int(12 * self.scale_factor)))
        self.full_button.clicked.connect(self.set_full_scope)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.setFont(QFont("Arial", int(12 * self.scale_factor)))
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.user_list)
        layout.addWidget(self.username_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.delete_button)
        layout.addLayout(btn_layout)

        layout.addWidget(self.full_button)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # --- Apply same style as BranchManagerWindow ---
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #fafafa;
                font-size: {int(14 * self.scale_factor)}px;
            }}
            QListWidget {{
                border: 1px solid #aaa;
                border-radius: 8px;
                background-color: white;
                padding: {int(10 * self.scale_factor)}px;
            }}
            QPushButton {{
                background-color: #000;
                color: white;
                border-radius: 8px;
                padding: {int(8 * self.scale_factor)}px {int(14 * self.scale_factor)}px;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
            QLineEdit {{
                padding: {int(6 * self.scale_factor)}px;
                border: 1px solid #777;
                border-radius: 5px;
            }}
        """)

    def add_username(self):
        username = self.username_input.text().strip()
        if username:
            # Avoid duplicates
            existing_users = [self.user_list.item(i).text() for i in range(self.user_list.count())]
            if username in existing_users:
                QMessageBox.information(self, "Info", f"Username '{username}' already exists.")
                return
            self.user_list.addItem(username)
            self.username_input.clear()

    def delete_username(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "No username selected to delete.")
            return
        for item in selected_items:
            self.user_list.takeItem(self.user_list.row(item))

    def set_full_scope(self):
        self.user_list.clear()
        self.usernames_Scope.clear()
        self.branch_scope = "full"
        QMessageBox.information(self, "Info", "Branch scope set to FULL.")
    
    def get_data(self):
        # Return updated scope and usernames
        usernames = [self.user_list.item(i).text() for i in range(self.user_list.count())]
        return self.branch_scope, usernames