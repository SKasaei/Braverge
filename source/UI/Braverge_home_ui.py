import os, json, platform, sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QHeaderView,QTreeWidgetItem,
    QListWidget, QListView, QPushButton, QLabel, QFileDialog,
    QStackedWidget, QTreeView, QLineEdit, QMessageBox,
    QFileSystemModel, QListWidgetItem, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize, QDir, QLocale
from PyQt5.QtGui import QIcon, QColor, QStandardItem, QStandardItemModel, QPixmap, QPainter, QPainterPath
from cryptography.fernet import Fernet

from controller.myGithub import myGithub
from controller.TreeNode import TreeNode
from UI.Braverge_TokenManager_ui import TokenManagerWindow
from UI.Braverge_BranchManager_ui import BranchManagerWindow
from UI.Braverge_MergeManager_ui import MergeManager
from UI.Braverge_ViewManager_ui import ViewManager_MainWindow
from UI.Braverge_GraphView_ui import GraphView
from controller.myBloom import myBloom
import hashlib



# Put at top of file
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



# --------- Global Helper ----------
def scale_ui(base_value, scale):
    """Returns an integer scaled proportionally to screen DPI."""
    return int(base_value * scale)

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12 , set_bold=False, color= QColor(0,0,0)):
        super().__init__()
        #fnt = QFont('Open sans', font_size)
        #fnt.setBold(set_bold)
        self.setEditable(False)
        #self.setFont(fnt)
        self.setText(txt)

class EnglishFileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.DisplayRole):
        value = super().data(index, role)

        # Size column = column 1
        if role == Qt.DisplayRole and index.column() == 1:

            info = self.fileInfo(index)

            # Directories → show empty size (like the default behavior)
            if info.isDir():
                return ""

            size = info.size()  # get file size in bytes

            # Format using English locale
            return QLocale(QLocale.English, QLocale.UnitedStates).formattedDataSize(size)

        return value


class HomeWidget(QMainWindow):
    
    def __init__(self, token , username, scale_factor):
        super().__init__()
        self.gitACCESSTOKEN = token
        self.Current_USER = username
        self.GitHub_Object = None
        self.Selected_Repository_name = None
        self.Selected_Dir_tree_view_selected_item = None
        self.scale_factor = scale_factor
        self.scale = lambda v: int(v * scale_factor)
        self.setWindowTitle("Braverge Desktop" + " - " + "Welcome " + self.Current_USER + "!")
        # self.setWindowIcon(QIcon('Logo.png'))
        # Build UI
        self.init_sidebar()
        self.init_pages()
        self.apply_layout()
        # Light theme only
        self.set_light_theme()

    # ---------------- Sidebar ----------------
    def init_sidebar(self):
        sidebar = QListWidget()
        sidebar.setViewMode(QListView.ListMode)
        sidebar.setIconSize(QSize(self.scale(18), self.scale(18)))
        sidebar.setFixedWidth(self.scale(200))
        sidebar.setSpacing(self.scale(4))
        sidebar.setObjectName("leftSidebar")

        # Make the sidebar selectable but avoid it stealing focus unnecessarily
        sidebar.setFocusPolicy(Qt.NoFocus)  # <-- disables keyboard focus
        sidebar.setSelectionMode(QListWidget.SingleSelection)  # only one item selectable at a time
        sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # optional, cleaner look

        pages = [
            ("Home", "go-home"),
            ("Repository", "Repository-manager"),
            ("Merge/Update", "merge-manager"),
            ("View", "view-manager"),
            ("About", "help-about"),
            ("Help", "preferences-system"),
        ]
        for name, icon_name in pages:
            item = QListWidgetItem(QIcon.fromTheme(icon_name), name)
            item.setSizeHint(QSize(self.scale(180), self.scale(34)))
            sidebar.addItem(item)

        sidebar.setCurrentRow(0)
        sidebar.currentRowChanged.connect(self.display_page)
        self.sidebar = sidebar

    # ---------------- Pages ----------------
    def init_pages(self):
        self.stack = QStackedWidget()

        self.page_home_widget = self.page_home()
        self.page_repo_widget = self.page_repository()
        self.page_merge_widget = self.page_merge()
        self.page_view_widget = self.page_view()
        self.page_settings_widget = self.page_settings()
        self.page_about_widget = self.page_about()

        for page in [
            self.page_home_widget,
            self.page_repo_widget,
            self.page_merge_widget,
            self.page_view_widget,
            self.page_about_widget,
            self.page_settings_widget,
        ]:
            self.stack.addWidget(page)

    def apply_layout(self):
        main = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(self.scale(0), self.scale(0), self.scale(0), self.scale(0))
        main_layout.setSpacing(0)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        main.setLayout(main_layout)
        self.setCentralWidget(main)

    def display_page(self, index):
        self.stack.setCurrentIndex(index)

    # ---------------- Home Page ----------------
    def page_home(self):
        page = QWidget()
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(self.scale(12), self.scale(8), self.scale(12), self.scale(8))
        root_layout.setSpacing(self.scale(12))

        # Left column: stacked cards (vertical)
        left_col = QVBoxLayout()
        left_col.setSpacing(self.scale(10))

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("🏠 Home")
        title.setStyleSheet(f"font-size: {int(18 * self.scale_factor)}px; font-weight: bold;")
        header_row.addWidget(title)
        header_row.addStretch()

        # Card: Metamodel & Workspace
        metamodel_layout = QVBoxLayout()
        metamodel_layout.setSpacing(self.scale(8))
        path_row = QHBoxLayout()
        self.metamodel_path = QLineEdit()
        self.metamodel_path.setPlaceholderText("No metamodel selected")
        self.workspace_path = QLineEdit()
        self.workspace_path.setPlaceholderText("No workspace selected")
        path_row.addWidget(self.workspace_path)
        path_row.addWidget(self.metamodel_path)
        metamodel_layout.addLayout(path_row)

        action_row = QHBoxLayout()
        btn_meta = QPushButton(QIcon.fromTheme("document-open"), "Select Metamodel")
        btn_meta.setMaximumWidth(self.scale(160))
        btn_meta.clicked.connect(self.select_metamodel)
        btn_ws = QPushButton(QIcon.fromTheme("folder"), "Select Workspace")
        btn_ws.setMaximumWidth(self.scale(160))
        btn_ws.clicked.connect(self.select_workspace)
        btn_open_ws = QPushButton(QIcon.fromTheme("system-run"), "Open Workspace")
        btn_open_ws.clicked.connect(self.open_workspace)
        action_row.addWidget(btn_ws)
        action_row.addWidget(btn_open_ws)
        action_row.addWidget(btn_meta)
        action_row.addStretch()
        metamodel_layout.addLayout(action_row)

        left_col.addWidget(self.card_section("Workspace & Metamodel", metamodel_layout))

        # Card: Tokens
        token_layout = QVBoxLayout()
        token_layout.setSpacing(self.scale(6))
        self.token_list = QListWidget()
        self.token_list.itemClicked.connect(self.token_list_clicked)
        self.token_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        token_layout.addWidget(self.token_list)
        token_row = QHBoxLayout()
        btn_refresh = QPushButton(QIcon.fromTheme("view-refresh"), "Refresh")
        btn_refresh.clicked.connect(self.refresh_tokens)
        btn_manager = QPushButton(QIcon.fromTheme("preferences-system"), "Open Token Manager")
        btn_manager.clicked.connect(self.open_token_manager)
        token_row.addWidget(btn_refresh)
        token_row.addWidget(btn_manager)
        token_row.addStretch()
        token_layout.addLayout(token_row)
        left_col.addWidget(self.card_section("Tokens", token_layout))

        # Card: Repositories
        repo_layout = QVBoxLayout()
        repo_layout.setSpacing(self.scale(6))
        self.repo_list = QListWidget()
        self.repo_list.itemClicked.connect(self.open_repository)
        self.repo_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        repo_layout.addWidget(self.repo_list)
        repo_btn_row = QHBoxLayout()
        btn_refresh_repos = QPushButton(QIcon.fromTheme("view-refresh"), "Refresh")
        btn_refresh_repos.clicked.connect(self.refresh_repositories)
        btn_new_repo = QPushButton(QIcon.fromTheme("document-new"), "New Repository")
        btn_new_repo.clicked.connect(self.create_new_repo)
        repo_btn_row.addWidget(btn_refresh_repos)
        repo_btn_row.addWidget(btn_new_repo)
        repo_btn_row.addStretch()
        repo_layout.addLayout(repo_btn_row)
        left_col.addWidget(self.card_section("Repositories", repo_layout))

        # Card: Directories
        
        dir_layout = QVBoxLayout()
        self.Dir_tree_view = QTreeView(self)
        self.Dir_tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.Dir_tree_view.setHeaderHidden(True)
        dir_layout.addWidget(self.Dir_tree_view)
        self.Dir_tree_view.clicked.connect(self.Dir_tree_view_doubleClicked)


        dir_row = QHBoxLayout()
        btn_refresh_dirs = QPushButton(QIcon.fromTheme("view-refresh"), "Refresh")
        btn_refresh_dirs.clicked.connect(self.refresh_directories)
        dir_row.addWidget(btn_refresh_dirs)
        dir_row.addStretch()
        dir_layout.addLayout(dir_row)
        left_col.addWidget(self.card_section("Directories", dir_layout))

        left_col.addStretch()

        # Right column: Recent Activity + Workspace Preview
        right_col = QVBoxLayout()
        right_col.setSpacing(self.scale(10))

        # Recent Activity card
        activity_layout = QVBoxLayout()
        self.recent_activity = QListWidget()
        self.recent_activity.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        activity_layout.addWidget(self.recent_activity)
        btn_clear = QPushButton("Clear Activity")
        btn_clear.clicked.connect(self.clear_activity)
        activity_layout.addWidget(btn_clear, alignment=Qt.AlignRight)
        right_col.addWidget(self.card_section("Recent Activity", activity_layout))

        # Workspace Preview
        tree_preview_layout = QVBoxLayout()
        self.repo_tree = QTreeView()
        self.repo_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.model = QFileSystemModel()
        self.model = EnglishFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.repo_tree.setModel(self.model)
        self.repo_tree.setRootIndex(self.model.index(QDir.rootPath()))
        self.repo_tree.setStyleSheet(f"""
            QTreeView {{
                border: none;
                background: #f9f9fb;
                selection-background-color: #eaf2ff;
            }}
        """)
        tree_preview_layout.addWidget(self.repo_tree)
        right_col.addWidget(self.card_section("Workspace Preview", tree_preview_layout))

        # Combine left and right
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root_layout.addWidget(left_widget, 3)   # 3/5 width
        root_layout.addWidget(right_widget, 2)  # 2/5 width

        page.setLayout(root_layout)

        # Populate default content
        #self.refresh_tokens()
        #self.refresh_repositories()
        #self.refresh_directories()
        self.add_activity("Logged in as " + self.Current_USER)

        return page

    def page_repository(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(self.scale(16), self.scale(12), self.scale(16), self.scale(12))
        layout.setSpacing(self.scale(14))

        # Title
        title = QLabel("📂 My Repository")
        title.setStyleSheet(f"""
            font-size: {int(20 * self.scale_factor)}px; 
            font-weight: 600; 
            color: #1e2a38;
        """)
        layout.addWidget(title)

        # Card container
        repo_card = QFrame()
        repo_card.setObjectName("repoCard")
        repo_card.setStyleSheet(f"""
            QFrame#repoCard {{
                background-color: #ffffff;
                border: 1px solid #e3e7ef;
                border-radius: {self.scale(12)}px;
            }}
        """)
        repo_layout = QVBoxLayout(repo_card)
        repo_layout.setContentsMargins(self.scale(16), self.scale(14), self.scale(16), self.scale(14))
        repo_layout.setSpacing(self.scale(12))

        # --- Toolbar Buttons Row ---
        button_row = QHBoxLayout()
        button_row.setSpacing(self.scale(10))

        button_definitions = [
            ("➕ New Project", "list-add", "Start a new project by submitting the first version.", self.create_project_clicked),
            ("⬇️ Checkout", "emblem-downloads", "Retrieve any version (latest or historical) of a model from a branch.", self.checkout_version_clicked),
            ("🔄 Pull", "go-down", "Download the most recent version from the local branch.", self.pull_changes_clicked),
            ("📝 Commit", "document-save", "Commit your current changes.", self.commit_changes_clicked),
            ("🔃 Refresh", "view-refresh", "Refresh the history of project evolution.", self.Dir_tree_view_doubleClicked),
            ("🌿 Branch Manager", "user-group", "Manage your branches (create, delete, switch).", self.Branch_Manager_button_clicked),
        ]

        for text, icon, tooltip, action in button_definitions:
            btn = QPushButton(text)
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setIconSize(QSize(self.scale(18), self.scale(18)))
            btn.setFixedHeight(self.scale(32))
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #f9fafc;
                    border: 1px solid #d7dbe5;
                    border-radius: {self.scale(8)}px;
                    padding: {self.scale(6)}px {self.scale(12)}px;
                    font-size: {int(14 * self.scale_factor)}px;
                }}
                QPushButton:hover {{
                    background: #eef3ff;
                    border-color: #b4c8f5;
                }}
                QPushButton:pressed {{
                    background: #dde6ff;
                }}
            """)
            btn.clicked.connect(action)
            button_row.addWidget(btn)

        button_row.addStretch()
        repo_layout.addLayout(button_row, stretch=0)

        # --- Project Tree View ---
        self.contents_tree_view = QTreeView(self)
        self.contents_tree_view.setHeaderHidden(True)
        self.contents_tree_view.setAlternatingRowColors(True)
        self.contents_tree_view.clicked.connect(self.on_branch_selected)
        self.tree_view_clicked = False
        self.contents_tree_view.setStyleSheet(f"""
            QTreeView {{
                border: 1px solid #e6e9ef;
                border-radius: {self.scale(8)}px;
                background: #fcfcfd;
                selection-background-color: #eaf2ff;
                alternate-background-color: #f7f9fb;
                font-size: {int(14 * self.scale_factor)}px;
            }}
            QTreeView::item:hover {{
                background: #a5beff;
            }}
        """)

        # Graphical representation of tree
        self.graph_view = GraphView(QStandardItemModel(), self)

        # Splitter side by side
        tree_graph_splitter = QSplitter(Qt.Horizontal)
        tree_graph_splitter.addWidget(self.contents_tree_view)
        tree_graph_splitter.addWidget(self.graph_view)
        tree_graph_splitter.setSizes([2, 1])  # tree 2/3, graph 1/3 proportion
        tree_graph_splitter.setStretchFactor(0, 2)
        tree_graph_splitter.setStretchFactor(1, 1)
        tree_graph_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.contents_tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        repo_layout.addWidget(tree_graph_splitter, stretch=1)

        # --- Empty State Message ---
        self.empty_label = QWidget()
        empty_layout = QVBoxLayout(self.empty_label)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel("✨")
        empty_icon.setStyleSheet(f"font-size: {int(32 * self.scale_factor)}px; margin-bottom: {self.scale(6)}px;")
        empty_layout.addWidget(empty_icon)

        empty_text = QLabel("No projects yet.\nStart by creating your first one!")
        empty_text.setAlignment(Qt.AlignCenter)
        empty_text.setStyleSheet(f"color: #6c7a89; font-size: {int(14 * self.scale_factor)}px; font-style: italic;")
        empty_layout.addWidget(empty_text)

        repo_layout.addWidget(self.empty_label, stretch=0)

        layout.addWidget(repo_card)
        page.setLayout(layout)

        # Initial visibility
        self.update_empty_message()

        return page

    def update_empty_message(self):
        """Show empty message label if tree view is empty, hide otherwise."""
        model = self.contents_tree_view.model()
        if model is None or model.rowCount() == 0 or self.is_treeview_only_master():
            self.contents_tree_view.hide()
            self.empty_label.show()
        else:
            self.contents_tree_view.show()
            self.empty_label.hide()

    def is_treeview_only_master(self):
        model = self.contents_tree_view.model()
        if not model:
            return True  # No model = empty
        root_count = model.rowCount()
        if root_count != 1:
            return False  # More than one root node => not empty
        # Get the only root index (row 0, column 0)
        root_index = model.index(0, 0)
        root_text = model.data(root_index)
        # Check if root text is "MASTER"
        if root_text != "MASTER":
            return False
        # Check if root node has children
        if model.hasChildren(root_index):
            return False  # MASTER node has children, so not empty
        # Only one root node named MASTER with no children => treat as empty
        return True

    def create_project_clicked(self):
        if self.workspace_path.text() == "" or self.metamodel_path.text() == "":
            QMessageBox.critical(self,"Error","Please select your workspace and metamodel path!",QMessageBox.StandardButton.Ok)
        else:

            workSpacePath= self.workspace_path.text()
            fname = QFileDialog.getOpenFileName(self,'Open file', workSpacePath, 'model (*.xmi);;xmi files (*.xmi)')
            if fname[0]:
                file_name = os.path.basename(fname[0])
                fileDirP = self.Selected_Dir_tree_view_selected_item
                self.GitHub_Object.create_new_project_modeling(fname[0], file_name, fileDirP, self.Selected_Repository_name, self.Current_USER)

                self.Dir_tree_view_doubleClicked()
                QMessageBox.information(self, "Success", f"Project is created successfully.")


    # ---------------- Merge Page ----------------
    def page_merge(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(self.scale(12), self.scale(6), self.scale(12), self.scale(6))
        main_layout.setSpacing(self.scale(16))

        # -------------------------
        # Title
        # -------------------------
        title = QLabel("🔀 Merge Manager")
        title.setStyleSheet(f"""
            font-size: {int(20 * self.scale_factor)}px;
            font-weight: 600;
            color: #1e2a38;
        """)
        main_layout.addWidget(title)

        # -------------------------
        # Info Card
        # -------------------------
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e3e7ef;
                border-radius: {self.scale(12)}px;
                padding: 12px;
            }}
            QLabel {{
                font-size: {int(14*self.scale_factor)}px;
                color: #333;
            }}
        """)
        info_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(self.scale(8))

        # Helper function to add sections
        def add_section(header_text, header_color, labels, add_divider=True):
            header = QLabel(header_text)
            header.setStyleSheet(f"""
                background-color: {header_color};
                color: white;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: {int(13*self.scale_factor)}px;
            """)
            info_layout.addWidget(header)

            for lbl in labels:
                info_layout.addWidget(lbl)

            if add_divider:
                divider = QFrame()
                divider.setFrameShape(QFrame.HLine)
                divider.setFrameShadow(QFrame.Sunken)
                divider.setStyleSheet("color: #e3e7ef;")
                info_layout.addWidget(divider)

        # -------------------------
        # Labels
        # -------------------------
        self.lbl_selected_Version_ID = QLabel("Selected Version ID: None")
        self.lbl_selected_Version = QLabel("Selected Version: None")
        self.lbl_selected_Branch_ID = QLabel("Selected Branch ID: None")
        self.lbl_selected_Branch = QLabel("Selected Branch: None")
        self.lbl_parent = QLabel("Parent Branch: None")
        self.lbl_parent_ID = QLabel("Parent Branch ID: None")

        # -------------------------
        # Sections
        # -------------------------
        add_section("Version", "#403c6c", [self.lbl_selected_Version_ID, self.lbl_selected_Version])
        add_section("Branch", "#403c6c", [self.lbl_selected_Branch_ID, self.lbl_selected_Branch])
        add_section("Parent", "#403c6c", [self.lbl_parent, self.lbl_parent_ID], add_divider=False)

        main_layout.addWidget(info_card)

        # -------------------------
        # Buttons Row (responsive)
        # -------------------------
        btn_row = QHBoxLayout()
        btn_row.setSpacing(self.scale(10))

        btn_Versions_Preparation = QPushButton(QIcon.fromTheme("git-merge"), "Versions Preparation")
        btn_Versions_Preparation.clicked.connect(self.Versions_Preparation_button_clicked)
        self.btn_merge = QPushButton(QIcon.fromTheme("git-merge"), "Open Merge Manager")
        self.btn_merge.clicked.connect(self.Merge_Manager_button_clicked)
        self.btn_merge.setEnabled(False)
        self.btn_update = QPushButton(QIcon.fromTheme("view-refresh"), "Open Update Manager")
        self.btn_update.setEnabled(False)
        self.btn_update.clicked.connect(self.Update_Manager_button_clicked)

        # Add stretchable buttons
        for btn, color in zip(
            [btn_Versions_Preparation, self.btn_merge, self.btn_update],
            ["#0078d7", "#0078d7", "#0078d7"]
        ):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setIconSize(QSize(self.scale(16), self.scale(16)))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: {int(14*self.scale_factor)}px;
                }}
                QPushButton:hover {{ background-color: #407cac; }}
            """)
            btn_row.addWidget(btn)

        main_layout.addLayout(btn_row)
        main_layout.addStretch()

        return page


   # ---------------- View Page ----------------
    def page_view(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")  # Page background
        layout = QVBoxLayout(page)
        layout.setSpacing(self.scale(16))
        layout.setContentsMargins(self.scale(12), self.scale(6), self.scale(12), self.scale(6))

        # -------------------------
        # Header
        # -------------------------
        header = QLabel("👁️ View Manager")
        header.setStyleSheet(f"font-size: {int(20 * self.scale_factor)}px; font-weight: 600; color: #222;")
        layout.addWidget(header)

        # -------------------------
        # Info Card
        # -------------------------
        info_card = QFrame()
        info_card.setObjectName("infoCard")
        info_card.setFrameShape(QFrame.StyledPanel)
        info_card.setStyleSheet(f"""
            QFrame#infoCard {{
                background-color: #ffffff;
                border: 1px solid #e3e7ef;
                border-radius: {self.scale(12)}px;
                padding: 12px;
            }}
            QLabel {{
                font-size: {int(14 * self.scale_factor)}px;
                color: #333;
            }}
        """)
        info_layout = QVBoxLayout()
        self.lbl_view_selected_branch = QLabel("Selected Branch: None")
        self.lbl_view_selected_version = QLabel("Parent Branch: None")
        info_layout.addWidget(self.lbl_view_selected_branch)
        info_layout.addWidget(self.lbl_view_selected_version)
        info_card.setLayout(info_layout)
        layout.addWidget(info_card)

        # -------------------------
        # Buttons Card
        # -------------------------
        btn_card = QFrame()
        btn_card.setObjectName("btnCard")
        btn_card.setFrameShape(QFrame.StyledPanel)
        btn_card.setStyleSheet(f"""
            QFrame#btnCard {{
                background-color: #ffffff;
                border: 1px solid #e3e7ef;
                border-radius: {self.scale(12)}px;
                padding: 10px;
            }}
        """)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(self.scale(10))

        self.btn_create_version = QPushButton("Create Selected Version")
        self.btn_create_version.clicked.connect(self.btn_create_request_Version_button_clicked)
        self.btn_create_version.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(14 * self.scale_factor)}px;
            }}
            QPushButton:hover {{ background-color: #008af0; }}
        """)

        self.btn_open_view_manager = QPushButton("Open View Manager")
        self.btn_open_view_manager.clicked.connect(self.View_Manager_button_clicked)
        self.btn_open_view_manager.setEnabled(False)
        self.btn_open_view_manager.setStyleSheet(f"""
            QPushButton {{
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(14 * self.scale_factor)}px;
            }}
            QPushButton:hover {{ background-color: #666; }}
        """)

        btn_row.addWidget(self.btn_create_version)
        btn_row.addWidget(self.btn_open_view_manager)
        btn_row.addStretch()
        btn_card.setLayout(btn_row)
        layout.addWidget(btn_card)

        # -------------------------
        # Tree Card
        # -------------------------
        tree_card = QFrame()
        tree_card.setObjectName("treeCard")
        tree_card.setFrameShape(QFrame.StyledPanel)
        tree_card.setStyleSheet(f"""
            QFrame#treeCard {{
                background-color: #ffffff;
                border: 1px solid #e3e7ef;
                border-radius: {self.scale(12)}px;
                padding: 10px;
            }}
        """)
        tree_layout = QVBoxLayout()
        self.tree_model_in_viewPage = QTreeWidget()
        self.tree_model_in_viewPage.setColumnCount(1)
        self.tree_model_in_viewPage.setHeaderLabels(["Model Tree Viewer"])
        self.tree_model_in_viewPage.setStyleSheet(f"""
            QTreeWidget {{
                background-color: #ffffff;
                border: none;
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background-color: #0078d7;
                color: white;
                padding: 4px;
                border: none;
            }}
        """)
        self.tree_model_in_viewPage.setAlternatingRowColors(True)
        self.tree_model_in_viewPage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.style_tree_header(self.tree_model_in_viewPage.header(), "#003661 ", "#ffffff")

        # Placeholder item
        element_data = {"element_type": "Click 'Create Selected Version' to view your version."}
        self.add_element_to_tree(self.tree_model_in_viewPage.invisibleRootItem(), element_data)

        tree_layout.addWidget(self.tree_model_in_viewPage)
        tree_card.setLayout(tree_layout)
        layout.addWidget(tree_card, stretch=1)

        layout.addStretch()
        return page


    def btn_create_request_Version_button_clicked(self):
        self.limitedAccess = False
        #self.selected_parent_branch = self.lbl_parent_ID.text().replace("Parent Branch ID: ", "")
        self.repoContents = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
        selectedbranchID  = self.lbl_view_selected_branch.text().replace("Selected Branch ID: ", "")
        #if self.selected_parent_branch == "MASTER": selectedbranchID = self.lbl_selected_Version_ID.text().replace("Selected Branch ID: ", "")
        while self.repoContents:
            oneItem = self.repoContents.pop(0)
        
            if "Branch_Info" in oneItem.name:
                Json_branchInfo_file = json.loads(oneItem.decoded_content)
                if selectedbranchID in Json_branchInfo_file['Versions_ID']:

                    if (self.Current_USER not in Json_branchInfo_file['collaborators']):
                        if "public" not in Json_branchInfo_file['collaborators']:
                            if (self.Current_USER not in Json_branchInfo_file['branch_Scope']):
                                QMessageBox.warning(self, "Access Denied", "You do not have permission to access this version.")
                                self.btn_open_view_manager.setEnabled(False)
                                return False
                            else:  self.limitedAccess= True
                    
        myFile = selectedbranchID + ".xmi"
        self.GitHub_Object.downloadFile_fromGitHub(self.workspace_path.text() +'/' , '/'+ myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, myFile)
        self.myBloom_Object = myBloom(self.metamodel_path.text())
        MyMetaModel = self.myBloom_Object.importMetaModel(self.metamodel_path.text())
        root_m = self.myBloom_Object.importModel(self.workspace_path.text() + "/" + myFile, MyMetaModel)
        model_json = self.myBloom_Object.all_properties_of_model(root_m)
        self.tree_model_in_viewPage.clear()
        self.add_element_to_tree(self.tree_model_in_viewPage.invisibleRootItem(), model_json)

        self.btn_open_view_manager.setEnabled(True)
        QMessageBox.information(self, "Success", f"Version is created successfully.")
        


    def add_element_to_tree(self, parent, element_data):
        """Recursively add element data to QTreeWidgetItem."""
        element_label = element_data.get('element_type', 'Unknown')
        element_id = element_data.get('element_id')
        if element_id:
            element_label += f" (ID: {element_id})"

        # Create a new item for the element
        element_item = QTreeWidgetItem([element_label])
        parent.addChild(element_item)

        # Recursively add properties
        for prop in element_data.get('properties', []):
            prop_name = prop.get('feature_name', 'unknown')
            val = prop.get('value')

            if isinstance(val, dict) and 'element_type' in val:
                # Nested element
                prop_item = QTreeWidgetItem([prop_name])
                element_item.addChild(prop_item)
                self.add_element_to_tree(prop_item, val)
            elif isinstance(val, list):
                # List of values or elements
                prop_item = QTreeWidgetItem([prop_name])
                element_item.addChild(prop_item)
                for item in val:
                    if isinstance(item, dict) and 'element_type' in item:
                        self.add_element_to_tree(prop_item, item)
                    else:
                        QTreeWidgetItem(prop_item, [str(item)])
            else:
                # Simple property
                prop_item = QTreeWidgetItem([f"{prop_name}: {val}"])
                element_item.addChild(prop_item)

        return element_item

    def style_tree_header(self, header: QHeaderView, color_start: str, color_end: str):
        """Apply horizontal gradient background to QTreeWidget header."""
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_start},
                    stop:1 {color_end}
                );
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 4px;
                border: 1px solid #999999;
            }}
        """)

    # ---------------- help Page ----------------
    def page_settings(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(self.scale(12), self.scale(6), self.scale(12), self.scale(6))
        title = QLabel("⚙️ Help")
        title.setStyleSheet(f"""
            font-size: {int(20 * self.scale_factor)}px; 
            font-weight: 600; 
            color: #1e2a38;
        """)
        #title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Help page coming soon...!"))
        layout.addStretch()
        page.setLayout(layout)
        return page

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.getcwd())
        return os.path.join(base_path, relative_path)


    # ---------------- About Page ----------------
    def page_about(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(self.scale(20), self.scale(20), self.scale(20), self.scale(20))
        layout.setSpacing(self.scale(12))

        # --- Logo (Rounded with Shadow + Placeholder) ---
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        size = self.scale(90)  # Slightly larger for crispness
        pixmap = QPixmap(self.resource_path('UI/icons/app.ico') )

        if not pixmap.isNull():
            # Use high-quality transformation & preserve details
            pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Create rounded version
            rounded = QPixmap(size, size)
            rounded.fill(Qt.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            logo.setPixmap(rounded)
        else:
            # --- Placeholder (gray circle with 'B') ---
            placeholder = QPixmap(size, size)
            placeholder.fill(Qt.transparent)
            painter = QPainter(placeholder)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#BDC3C7"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.setPen(QColor("white"))
            font = painter.font()
            font.setPointSize(int(size / 2.5))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(placeholder.rect(), Qt.AlignCenter, "B")
            painter.end()
            logo.setPixmap(placeholder)

        logo.setAlignment(Qt.AlignCenter)

        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        logo.setGraphicsEffect(shadow)

        logo_layout.addWidget(logo)
        layout.addWidget(logo_container)

        # --- Title ---
        title = QLabel("About Braverge")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: {int(20 * self.scale_factor)}px; 
            font-weight: bold; 
            color: #2C3E50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # --- Version ---
        version = QLabel("Braverge Desktop — Version 1.6")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 14px; color: #555; margin-bottom: 10px;")
        layout.addWidget(version)

        # --- Description ---
        description = QLabel(
            "Braverge is a modern framework and toolkit for managing the evolution of software models.\n"
            "It supports intelligent versioning, branching, and merging of models — essential for\n"
            "collaborative, model-driven engineering.\n\n"
            "Braverge also enables Multi-view Modeling, allowing users to define their own preferences\n"
            "and access the parts of models that belong to them. This ensures flexibility, clarity,\n"
            "and better collaboration across teams."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 13px; color: #333; line-height: 1.4;")
        layout.addWidget(description)

        # --- Separator ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # --- GitHub Link ---
        github_label = QLabel("Project Repository")
        github_label.setAlignment(Qt.AlignCenter)
        github_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C3E50; margin-top: 10px;")
        layout.addWidget(github_label)

        github_link = QLabel("<a href='https://github.com/SKasaei/Braverge'>github.com/SKasaei/Braverge</a>")
        github_link.setAlignment(Qt.AlignCenter)
        github_link.setOpenExternalLinks(True)
        github_link.setStyleSheet("font-size: 13px; color: #2980B9;")
        layout.addWidget(github_link)

        # --- Contact Section ---
        contact_label = QLabel("Contact Us")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C3E50; margin-top: 10px;")
        layout.addWidget(contact_label)

        contact_info = QLabel("Email: <a href='mailto:smskasaei@gmail.com'>smskasaei@gmail.com</a>")
        contact_info.setAlignment(Qt.AlignCenter)
        contact_info.setOpenExternalLinks(True)
        contact_info.setStyleSheet("font-size: 13px; color: #2980B9;")
        layout.addWidget(contact_info)

        layout.addStretch()
        return page





    # ---------------- Section Card ----------------
    def card_section(self, title, inner_layout):
        frame = QFrame()
        frame.setObjectName("cardFrame")
        frame.setFrameShape(QFrame.StyledPanel)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(self.scale(10), self.scale(8), self.scale(10), self.scale(8))
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        vbox.addWidget(label)
        if isinstance(inner_layout, (QVBoxLayout, QHBoxLayout)):
            vbox.addLayout(inner_layout)
        else:
            vbox.addWidget(inner_layout)
        frame.setLayout(vbox)
        return frame

    # ---------------- Logic ----------------
    def select_metamodel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Metamodel File", self.workspace_path.text(), 'model (*.ecore);;ecore files (*.ecore)')
        if path:
            self.metamodel_path.setText(path)
            self.add_activity("Selected Metamodel")

    def select_workspace(self):
        path = QFileDialog.getExistingDirectory(self, "Select Workspace Folder")
        if path:
            self.workspace_path.setText(path)
            self.add_activity("Selected Workspace")
            try:
                self.repo_tree.setRootIndex(self.model.index(path))
            except Exception:
                pass

    def refresh_tokens(self):
        self.token_list.clear()
        #self.token_list.addItem("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")
        g = myGithub("empty")
        encrypted_tokens = g.load_user_tokens(self.Current_USER)
        if encrypted_tokens:
            for t in encrypted_tokens:
                try:
                    self.token_list.addItem(self.decrypt_token(t))
                except:
                    self.token_list.addItem("(Invalid Token)")
        else:
            self.token_list.addItem("(No tokens found)")
        
        self.add_activity("Refreshed Tokens")

    def decrypt_token(self, token_enc: str) -> str:
        ENCRYPTION_KEY = self.load_key()
        CIPHER = Fernet(ENCRYPTION_KEY)

        return CIPHER.decrypt(token_enc.encode()).decode()

    def load_key(self):
        KEY_FILE = "key.key"
        """Load or generate encryption key."""
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key

            



    







    def open_token_manager(self):
        self.add_activity("Opened Token Manager")

        self.token_window = TokenManagerWindow(self.Current_USER, self.scale_factor)
        self.token_window.show()

    def refresh_repositories(self):
        if not self.repo_list.selectedItems():
            self.repo_list.clear()
            self.repo_list.addItems(["Please select your token!"])
        else:
            self.repo_list.clear()
            counter = 0
            for x in self.GitHub_Object.getRepos():
                self.repo_list.insertItem(counter, x.name)
                counter = counter + 1
        
        self.add_activity("Refreshed Repositories")

    def refresh_directories(self):
        model = self.Dir_tree_view.model()
        if model is not None:
            model.clear()
        self.add_activity("Refreshed Directories")
        #self.dir_list.addItems(["/path/to/dir1", "/path/to/dir2", "/path/to/dir3"])

    # def refresh_tree_view(self):
    #     path = self.workspace_path.text() or QDir.rootPath()
    #     self.repo_tree.setRootIndex(self.model.index(path))

    def clear_highlights(self, model):
        """Remove background color from all items in the model."""
        root = model.invisibleRootItem()
        stack = [root]
        while stack:
            item = stack.pop()
            item.setBackground(QtGui.QBrush(QtCore.Qt.transparent))
            for row in range(item.rowCount()):
                stack.append(item.child(row))

    def on_branch_selected(self, index):
        self.add_activity("Selected Item")

        self.clear_highlights(self.contents_tree_view.model())
        self.tree_view_clicked = index

        item = self.contents_tree_view.model().itemFromIndex(index)
        self.graph_view.highlight_node(item)

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
        try:
            # Show the friendly version number to the user
            
            if (branch_name == "Branch" or branch_name == "MASTER"):
                self.lbl_view_selected_branch.setText(f"Selected Branch ID: {branch_id}")
                self.lbl_view_selected_version.setText(f"Selected Version ID: None")
                self.lbl_selected_Branch.setText(f"Selected Branch: {branch_name}")
                self.lbl_selected_Branch_ID.setText(f"Selected Branch ID: {branch_id}")
                self.lbl_selected_Version.setText(f"Selected Version: None")
                self.lbl_selected_Version_ID.setText(f"Selected Version ID: None")
                
                if (branch_name == "MASTER"):
                    self.lbl_parent_ID.setText(f"Parent Branch ID: None")
                    self.lbl_parent.setText(f"Parent Branch: None")
                else:
                    self.lbl_parent.setText(f"Parent Branch: {item.parent().parent().text()}")
                    self.lbl_parent_ID.setText(f"Parent Branch ID: {item.parent().parent().data(Qt.UserRole)}")
            else:
                self.lbl_view_selected_branch.setText(f"Selected Branch ID: {item.parent().data(Qt.UserRole)}")
                self.lbl_view_selected_version.setText(f"Selected Version ID: {branch_id}")
                self.lbl_selected_Branch.setText(f"Selected Branch: {item.parent().text()}")
                self.lbl_selected_Branch_ID.setText(f"Selected Branch ID: {item.parent().data(Qt.UserRole)}")
                self.lbl_selected_Version.setText(f"Selected Version: {branch_name}")
                self.lbl_selected_Version_ID.setText(f"Selected Version ID: {branch_id}")
                
                if (item.parent().text() == "MASTER"):
                    self.lbl_parent_ID.setText(f"Parent Branch ID: None")
                    self.lbl_parent.setText(f"Parent Branch: None")
                else:
                    self.lbl_parent.setText(f"Parent Branch: {item.parent().parent().parent().text()}")
                    self.lbl_parent_ID.setText(f"Parent Branch ID: {item.parent().parent().parent().data(Qt.UserRole)}")

                # if (item.parent().data(Qt.UserRole) == None):
                #     self.lbl_selected_Branch_ID.setText(f"Parent Branch ID: MASTER")

            


            
            # Optionally, show real IDs in another label (or use them internally)
            # if branch_id:
            #     #self.lbl_selected_Version_ID.setText(f"Selected Version ID: {branch_id}")
            #     self.lbl_view_selected.setText(f"Selected ID: {branch_id}")
            # if parent_branch_id:
            #     self.lbl_view_parent.setText(f"Parent ID: {parent_branch_id}")
        except Exception:
            pass

    def create_new_repo(self):
        self.add_activity("Created Repository")
        QMessageBox.information(self, "New Repository", "Creating a new repository...")

    def open_repository(self, item):
        self.add_activity("Selected Repository")

        self.Selected_Repository_name = item.text()
        self.tree_Model = QStandardItemModel()
        self.rootnode = self.tree_Model.invisibleRootItem()                      
        self.Repo_content_LVL0 = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, "")
        all_dir = []
        self.tree_root_Item = StandardItem(self.Selected_Repository_name+"/", 12, set_bold=True)
        self.rootnode.appendRow(self.tree_root_Item)

        while self.Repo_content_LVL0:
            file_content = self.Repo_content_LVL0.pop(0)
            if file_content.type == "dir":
                dfile = str(file_content).replace('ContentFile(path="','').replace('")','') + "/"
                all_dir.append(dfile)
            
        for dir in  all_dir:
            self.tree_Item = StandardItem(dir, 10)
            self.tree_root_Item.appendRow(self.tree_Item)
            self.Repo_content_LVL = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, dir)
            
            for item in self.Find_dir_dir_Repo(self.Repo_content_LVL, dir):
                self.tree_Item2 = StandardItem(item, 10)
                self.tree_Item.appendRow(self.tree_Item2)

        self.Dir_tree_view.setModel(self.tree_Model)
        self.Dir_tree_view.expandAll()            

    def Find_dir_dir_Repo(self, contents, dir):
        all_dir = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                all_dir.append(str(file_content).replace('ContentFile(path="'+ dir ,'').replace('")',''))
        return all_dir
    
    def Dir_tree_view_doubleClicked(self):
        self.add_activity("Refreshed Directory")
        self.add_activity("Created Version Histrory")
        for x in self.Dir_tree_view.selectedIndexes():
            if x.data().find('/') != -1:
                self.Selected_Dir_tree_view_selected_item = x.data()

        ####################################################
        self.tree_Model = QStandardItemModel()
        self.rootnode = self.tree_Model.invisibleRootItem()
        self.tree_root_Item = StandardItem("MASTER", 12, set_bold=True)
        self.rootnode.appendRow(self.tree_root_Item)
        root_tree_Text = TreeNode("MASTER")
        Selected_file_directory = self.Selected_Dir_tree_view_selected_item
        node_tree_id = []
        node_tree_id_Text = []
        branch_info_files = []
        self.Repo_content_OBJq = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, Selected_file_directory)

        if self.Repo_content_OBJq is not None:
            while self.Repo_content_OBJq:
                file_content = self.Repo_content_OBJq.pop(0)
                if file_content.type != "dir":
                    if "Branch_Info" in file_content.name:
                        mydata = json.loads(file_content.decoded_content)
                        branch_info_files.append(mydata['branch_ID'])
        
        self.Repo_content_OBJ = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, Selected_file_directory)

        node_tree_id_data = []
    
        if self.Repo_content_OBJ is not None:
            while self.Repo_content_OBJ:
                file_content = self.Repo_content_OBJ.pop(0)
                if file_content.type != "dir":
                    if "Branch_Info" in file_content.name:
                        
                        mydata = json.loads(file_content.decoded_content)

                        if mydata['branch_ID'] == mydata['pivot_ID']:
                            self.tree_root_Item.setData(mydata['branch_ID'], role=Qt.UserRole)
                            version_number = 1
                            for vid in mydata['Versions_ID']:
                                display_name = f"Version {version_number}"
                                self.tree_Item1 = StandardItem(display_name, 10)
                                
                                # store original ID inside item data for later use
                                self.tree_Item1.setData(vid, role=Qt.UserRole)
                                
                                self.tree_root_Item.appendRow(self.tree_Item1)
                                node_tree_id.append(self.tree_Item1)
                                node_tree_id_data.append(vid)

                                child_tree_Text = TreeNode(display_name)
                                root_tree_Text.add_child(child_tree_Text)
                                node_tree_id_Text.append(child_tree_Text)

                                version_number += 1

                            branch_info_files.remove(mydata['branch_ID'])
        
                        else:
                            if mydata['pivot_ID'] in branch_info_files:
                                self.Repo_content_OBJ.append(file_content)
                            else:
                                if mydata['pivot_ID'] not in node_tree_id_data:
                                    self.Repo_content_OBJ.append(file_content)
                                else:
                                    branch_info_files.remove(mydata['branch_ID']) 

                                    node_tree_id_temp = []
                                    node_tree_id_temp_Text = []

                                    child_tree_branch_Text = TreeNode("Branch" + ":" + mydata['branch_ID'])
                                    tree_Item_branch = StandardItem("Branch", 10, set_bold=True)
                                    tree_Item_branch.setData(mydata['branch_ID'], role=Qt.UserRole)  # keep original ID

                                    version_number = 1
                                    for xs in mydata['Versions_ID']:
                                        display_name = f"Version {version_number}"

                                        self.tree_Item2 = StandardItem(display_name, 10)
                                        self.tree_Item2.setData(xs, role=Qt.UserRole)  # keep original ID
                                        
                                        tree_Item_branch.appendRow(self.tree_Item2)
                                        node_tree_id_temp.append(self.tree_Item2)
                                        node_tree_id_data.append(xs)
                                        
                                        child_tree_Text = TreeNode(display_name)
                                        child_tree_branch_Text.add_child(child_tree_Text)
                                        node_tree_id_temp_Text.append(child_tree_Text)

                                        version_number += 1
                                    
                                    for treeItm in node_tree_id:    
                                        if treeItm.data(Qt.UserRole) == mydata['pivot_ID']:
                                            treeItm.appendRow(tree_Item_branch)

                                    for treeItm_TEXT in node_tree_id_Text:
                                        if mydata['pivot_ID'] == treeItm_TEXT.get_name():
                                            treeItm_TEXT.add_child(child_tree_branch_Text)                         

                                    node_tree_id_Text.extend(node_tree_id_temp_Text)
                                    node_tree_id.extend(node_tree_id_temp)

            self.contents_tree_view.setModel(self.tree_Model)
            self.contents_tree_view.expandAll()

            self.update_empty_message()

            
            self.graph_view.draw_model(self.tree_Model)   # refresh graph

            

  

    

    def token_list_clicked(self, item):
        self.add_activity("Selected Token")

        if self.metamodel_path.text().strip():
            self.create_object_myGithub = myGithub(item.text())
            self.GitHub_Object = myGithub(item.text())
            self.GitHub_Object.setMETAMODEL_PATH_FILE(self.metamodel_path.text())
            self.repo_list.clear()
            counter = 0
            for x in self.create_object_myGithub.getRepos():
                self.repo_list.insertItem(counter, x.name)
                counter = counter + 1
        else:
            QMessageBox.critical(self,"Error","Please select your metamodel path!",QMessageBox.StandardButton.Ok)

    def open_workspace(self):
        self.add_activity("Opened Workspace")

        path = self.workspace_path.text()
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            os.system(f'open "{path}"')
        elif system == "Linux":
            os.system(f'xdg-open "{path}"')
        else:
            raise OSError("Unsupported operating system")

    def add_activity(self, text):
        self.recent_activity.addItem(text)

    def clear_activity(self):
        self.recent_activity.clear()
        self.add_activity("Cleared Activities")

    def Branch_Manager_button_clicked(self):
        tempFind = False
        self.add_activity("Opened Branch Manager")
        workSpacePath= self.workspace_path.text() 

        if self.tree_view_clicked == False:
            QMessageBox.warning(self, "Selection Error", "Kindly select a version.")
        else:
            selected_version_id = self.lbl_selected_Version_ID.text().replace("Selected Version ID: ", "")
            repo_contents = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
            while repo_contents:
                item = repo_contents.pop(0)
                if "Branch_Info" in item.name:
                    branch_info = json.loads(item.decoded_content)
                    if selected_version_id in branch_info['Versions_ID']:
                        tempFind = True
                        if self.Current_USER in branch_info['collaborators'] or "public" in branch_info['collaborators']:
                            self.branch_window = BranchManagerWindow(self.Current_USER, self.GitHub_Object, workSpacePath, self.Selected_Dir_tree_view_selected_item , self.Selected_Repository_name,
                                                                    branch_info['branch_ID'], branch_info['pivot_ID'], branch_info['collaborators'],
                                                                    branch_info['branch_Pattern'], branch_info['branch_Scope'], branch_info['Versions_ID'], self.tree_Model, self.tree_view_clicked)
                            self.branch_window.show()   
                        else:
                            QMessageBox.warning(self, "Access Denied", "You do not have permission to access this version.")
                        break  # Exit once the relevant branch info is found
        if not tempFind:
            QMessageBox.warning(self, "Selection Error", "Kindly select a version.")











        

    # def commit_changes_clicked(self):
    #     global Selected_Repository_name, GitHub_Object

    #     work_space_path = self.workspace_path.text()
    #     file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', work_space_path, 'model (*.xmi);;xmi files (*.xmi)')

    #     if not file_path:
    #         return  # No file selected, exit early

    #     confirm = QMessageBox.question(
    #         self,
    #         'Confirmation',
    #         'Do you want to commit on the current branch?',
    #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #     )

    #     if confirm == QMessageBox.StandardButton.Yes:
    #         file_name = os.path.basename(file_path)
    #         file_dir = Selected_Dir_tree_view_selected_item  # Assuming global or accessible variable
    #         try:
    #             GitHub_Object.uploadFile(file_path, file_name, file_dir, Selected_Repository_name)
    #             QMessageBox.information(self, "Success", f"File '{file_name}' committed successfully.")
    #         except Exception as e:
    #             QMessageBox.critical(self, "Upload Failed", f"Failed to commit changes:\n{str(e)}")
    #     else:
    #         QMessageBox.information(
    #             self,
    #             "Information",
    #             ("Selecting Commit will submit your changes to the current branch. "
    #             "If this is not your intended action, please choose an alternative option.")
    #         )

    def pull_changes_clicked(self):
        self.add_activity("Pulled Changes")

        selected_version_id = self.lbl_selected_Version_ID.text().replace("Selected Version ID: ", "")
        workspace_path = self.workspace_path.text().rstrip('/') + '/'
        repo_contents = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
        while repo_contents:
            item = repo_contents.pop(0)
            if "Branch_Info" in item.name:
                branch_info = json.loads(item.decoded_content)
                if selected_version_id in branch_info['Versions_ID']:
                    if self.Current_USER in branch_info['collaborators'] or "public" in branch_info['collaborators']:
                        model_file_name = f"{branch_info['branch_ID']}.xmi"
                        remote_file_path = f"/{branch_info['branch_ID']}.xmi"
                        remote_Branch_file_path = f"/{branch_info['branch_ID']}Branch_Info.json"
                        
                        self.GitHub_Object.downloadFile_fromGitHub(
                            workspace_path, remote_file_path, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, model_file_name
                        )
                        self.GitHub_Object.downloadFile_fromGitHub(
                            workspace_path, remote_Branch_file_path, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Branch_Info.json"
                        )
                        QMessageBox.information(self, "Success", f"Version '{self.lbl_selected_Version.text().replace("Selected Version: ", "")}' successfully downloaded.")
                    else:
                        QMessageBox.warning(self, "Access Denied", "You do not have permission to access this version.")
                    break  # Exit once the relevant branch info is found

    def checkout_version_clicked(self):
        self.add_activity("Checkout Version")

        Selected_file_tree_view_selected_item = self.lbl_selected_Version_ID.text().replace("Selected Version ID: ", "")
        Json_branchInfo_file = ""
        workSpacePath= self.workspace_path.text() + '/'
        self.repoContents = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
        while self.repoContents:
            oneItem = self.repoContents.pop(0)
            if "Branch_Info" in oneItem.name:
                Json_branchInfo_file = json.loads(oneItem.decoded_content)
                if Selected_file_tree_view_selected_item in Json_branchInfo_file['Versions_ID']:
                    if self.Current_USER in Json_branchInfo_file['collaborators'] or "public" in Json_branchInfo_file['collaborators']:

                        modelselectedfile_name = Selected_file_tree_view_selected_item + ".xmi"

                        #accsess to the repository
                        myFile = '/' + Json_branchInfo_file['branch_ID'] + ".xmi"
                        self.GitHub_Object.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, modelselectedfile_name)
                        
                        list_vid = []
                        for vId in Json_branchInfo_file['Versions_ID']:
                            list_vid.append(vId)

                        list_vid.reverse()
                        
                        for vId in list_vid:
                            if vId == Selected_file_tree_view_selected_item:
                                
                                break

                            else:
                                myFile = '/' + vId + "Version_Info.json"
                                self.GitHub_Object.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Version_Info.json")
                                self.GitHub_Object.create_previous_version(self.workspace_path.text(), modelselectedfile_name , modelselectedfile_name)
                                
                        self.GitHub_Object.create_new__short_branch(workSpacePath, modelselectedfile_name, self.Selected_Dir_tree_view_selected_item, Selected_file_tree_view_selected_item , self.Selected_Repository_name, self.Current_USER)
                        QMessageBox.information(self, "Success", f"Version '{Selected_file_tree_view_selected_item}' successfully downloaded.")
                        QMessageBox.information(self, "Information", f"Switching in local branch.")
                    else:
                        QMessageBox.warning(self, "Access Denied", "You do not have permission to access this version.")
                    break  # Exit 

    def commit_changes_clicked(self):
        self.add_activity("Commit to Branch")


        work_space_path = self.workspace_path.text()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', work_space_path, 'model (*.xmi);;xmi files (*.xmi)')

        if not file_path:
            return  # No file selected, exit early

        confirm = QMessageBox.question(
            self,
            'Confirmation',
            'Do you want to commit on the current branch?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            file_name = os.path.basename(file_path)
            file_dir = self.Selected_Dir_tree_view_selected_item  # Assuming global or accessible variable
            try:
                self.GitHub_Object.uploadFile(file_path, file_name, file_dir, self.Selected_Repository_name)
                QMessageBox.information(self, "Success", f"File '{file_name}' committed successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Upload Failed", f"Failed to commit changes:\n{str(e)}")
        else:
            QMessageBox.information(
                self,
                "Information",
                ("Selecting Commit will submit your changes to the current branch. "
                "If this is not your intended action, please choose an alternative option.")
            )


    def Merge_Manager_button_clicked(self):

        user_confirm = QMessageBox.question(
            self,
            "Confirmation",
            "Do you want to propagate your changes on the parent branch?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if user_confirm != QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                None,
                "Information",
                "By selecting the merge operation, your changes will be submitted to the parent branch. "
                "If this is not your intention, please choose a different operation."
            )
            return
        
        self.add_activity("Opened Merge Manager")
        newVersionID = self.Merged_version_ID
        operation_flag = "merge"
        self.merge_window = MergeManager(self.workspace_path.text(), self.GitHub_Object, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, newVersionID, self.metamodel_path.text(),operation_flag, self.scale_factor)
        self.merge_window.show()

    def Update_Manager_button_clicked(self):
        user_confirm = QMessageBox.question(
            self,
            "Confirmation",
            "Would you like to receive the latest changes from the parent branch?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if user_confirm != QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Information",
                "By choosing the update operation, you will receive the latest modifications from the parent branch. "
                "If this is not what you intended, please select a different operation."
            )
            return
        
        self.add_activity("Opened Update Manager")
        newVersionID = self.Update_version_ID
        operation_flag = "update"
        self.merge_window = MergeManager(self.workspace_path.text(), self.GitHub_Object, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, newVersionID, self.metamodel_path.text(),operation_flag, self.scale_factor)
        self.merge_window.show()

    def View_Manager_button_clicked(self):
        self.add_activity("Opened View Manager")
        selected_version_id = self.lbl_selected_Version_ID.text().replace("Selected Version ID: ", "")

        self.view_window = ViewManager_MainWindow(self.workspace_path.text(), self.metamodel_path.text(), self.GitHub_Object, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, selected_version_id, self.metamodel_path.text(), self.limitedAccess, self.scale_factor)
        self.view_window.show()

    # ------------------ Theme ------------------
    def set_light_theme(self):
        self.setStyleSheet(f"""
        QMainWindow {{ background-color: #f5f6f8; }}
        #leftSidebar {{
            background-color: #ffffff;
            border-right: 1px solid #e6e9ef;
        }}
        QListWidget#leftSidebar::item {{
            padding: {self.scale(8)}px;
            margin: {self.scale(4)}px;
            border-radius: {self.scale(6)}px;
        }}
        QListWidget#leftSidebar::item:selected {{
            background-color: #eaf2ff;
            color: #0b3d91;
            font-weight: 600;
            border-left: 4px solid #2f7ef6;
        }}
        QFrame#cardFrame {{
            background-color: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 8px;
        }}
        QPushButton {{
            background-color: #f0f2f5;
            border: 1px solid #d7dbe0;
            padding: {self.scale(6)}px {self.scale(10)}px;
            border-radius: {self.scale(6)}px;
        }}
        QPushButton:hover {{ background-color: #e6f0ff; }}
        QLineEdit {{ background: white; border: 1px solid #d7dbe0; padding: {self.scale(6)}px; border-radius: {self.scale(6)}px; }}
        QTreeView, QListWidget {{ background: white; border: 1px solid #e6e9ef; }}
        """)









    def Versions_Preparation_button_clicked(self):
        self.repo_name = self.Selected_Repository_name
        self.git = self.GitHub_Object
        self.selected_branch = self.lbl_selected_Branch_ID.text().replace("Selected Branch ID: ", "")
        self.file_name = f"{self.selected_branch}.xmi"
        res = self._create_base_left_right(self.file_name)
        if res:
            self.btn_merge.setEnabled(True)
            self.btn_update.setEnabled(True)
            QMessageBox.information(None, "Information", "Versions are created successfully!")

            # branch_info = self._prepare_versions()
            # if not branch_info:
            #     QMessageBox.warning(None, "Warning", "Failed to locate branch info for merging.")
            #     return

            # self._create_base_left_right(branch_info)
            # self._perform_merge(branch_info)
            # self._upload_merged_version(branch_info)
            # self._post_merge_cleanup_prompt()


    # ------------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------------

    def _create_base_left_right(self, file_name):
        ###
        #create Base version
        pivot_ID = ""
        Selected_file_tree_view_selected_item = str(file_name).replace('.xmi','') 
        Json_branchInfo_file = ""
        workSpacePath= self.workspace_path.text() + '/'
        self.selected_parent_branch = self.lbl_parent_ID.text().replace("Parent Branch ID: ", "")
        self.repoContents = self.GitHub_Object.getRepos_contents(self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item)
        while self.repoContents:
            oneItem = self.repoContents.pop(0)
        
            if "Branch_Info" in oneItem.name:
                Json_branchInfo_file = json.loads(oneItem.decoded_content)
                if Selected_file_tree_view_selected_item in Json_branchInfo_file['Versions_ID']:

                    if (self.Current_USER not in Json_branchInfo_file['collaborators']):
                        if "public" not in Json_branchInfo_file['collaborators']:
                            QMessageBox.warning(self, "Access Denied", "You do not have permission to access this version.")
                            return False
                    
                    modelselectedfile_name = Selected_file_tree_view_selected_item + ".xmi"
                    #accsess to the repository
                    myFile = '/' + Json_branchInfo_file['branch_ID'] + ".xmi"
                    self.GitHub_Object.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, modelselectedfile_name)
                    list_vid = []
                    for vId in Json_branchInfo_file['Versions_ID']:
                        list_vid.append(vId)
                    list_vid.reverse()
                    pivot_ID = '/' + Json_branchInfo_file['pivot_ID'] + ".xmi"
                    for vId in list_vid:
                        if vId == Selected_file_tree_view_selected_item:
                            
                            break

                        else:
                            myFile = '/' + vId + "Version_Info.json"
                            self.GitHub_Object.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Version_Info.json")
                            self.GitHub_Object.create_previous_version(self.workspace_path.text(), modelselectedfile_name , modelselectedfile_name)

                    modelfile_name = "/" + self.selected_parent_branch + ".xmi"
                    branchInfojson = "/" + self.selected_parent_branch + "Branch_Info.json"

                if (self.selected_parent_branch == Json_branchInfo_file['branch_ID']) or (self.selected_parent_branch == "MASTER" and Json_branchInfo_file['branch_ID'] == Json_branchInfo_file['pivot_ID']):
                    modelfile_name = "/" + Json_branchInfo_file['branch_ID'] + ".xmi"
                    branchInfojson = "/" + Json_branchInfo_file['branch_ID'] + "Branch_Info.json"
        
        self.Merged_version_ID =  self.selected_parent_branch   + ".xmi"    
        src= workSpacePath + file_name # fname[0]
        dst= str(workSpacePath + file_name).replace(file_name,'Base.xmi')
        os.replace(src, dst)
        #self.text_browser_Merge_report.setText(self.text_browser_Merge_report.toPlainText() + "\n>> The base version has been created.")
        myFile = '/' + file_name
        self.Update_version_ID =   file_name
        self.GitHub_Object.downloadFile_fromGitHub(workSpacePath , myFile, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Right.xmi")
        #self.text_browser_Merge_report.setText(self.text_browser_Merge_report.toPlainText() + "\n>> The right version has been created.")
        ### creating left version -- on pivot branch
        self.GitHub_Object.downloadFile_fromGitHub(workSpacePath ,  modelfile_name, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Left.xmi")
        ## downloading the branch info file of parent branch
        self.GitHub_Object.downloadFile_fromGitHub(workSpacePath ,  branchInfojson, self.Selected_Repository_name, self.Selected_Dir_tree_view_selected_item, "Branch_Info.json")
        #self.text_browser_Merge_report.setText(self.text_browser_Merge_report.toPlainText() + "\n>> The left version has been created.")
        # #self.text_browser_Merge_report.setText(self.text_browser_Merge_report.toPlainText() + "\n>> Merging has started.")
        # self.GitHub_Object.GitHub_Merge_Models(workSpacePath, self.Set_Metamodel_lineEdit.text())
        # src= workSpacePath + 'Target.xmi'
        # dst= workSpacePath + Json_branchInfo_file['pivot_ID'] + ".xmi"
        # shutil.copy(src,dst)
        # self.text_browser_Merge_report.setText(self.text_browser_Merge_report.toPlainText() + "\n>> The merged version has been successfully created.")
        # ## uploading merged version on the parent branch 
        # self.GitHub_Object.uploadFile(dst, Json_branchInfo_file['pivot_ID'] + ".xmi", fileDirP, Selected_Repository_name)
        return True

   


    # def _upload_merged_version(self, branch_info):
    #     """Upload the merged model back to the parent branch."""
    #     merged_file = os.path.join(self.workspace_path, f"{branch_info['pivot_ID']}.xmi")
    #     self.git.uploadFile(merged_file, f"{branch_info['pivot_ID']}.xmi", self.file_dir, self.repo_name)
    #     self.append_report("Merged version uploaded to the parent branch.")


    # def _post_merge_cleanup_prompt(self):
    #     """Ask whether to destroy or preserve branch history after integration."""
    #     cleanup_confirm = QMessageBox.question(
    #         self,
    #         "Confirmation",
    #         "Do you want to destroy the branch history after the integration?",
    #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #     )

    #     if cleanup_confirm == QMessageBox.StandardButton.Yes:
    #         print("TO DO: Cleanup branch history")
    #         QMessageBox.information(None, "Information", "TO DO: Cleanup branch history")
    #     else:
    #         print("TO DO: Preserve branch history")
    #         QMessageBox.information(None, "Information", "TO DO: Preserve branch history")
