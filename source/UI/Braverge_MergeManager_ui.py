import sys, os, shutil, re
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QMessageBox, QFrame, QSizePolicy,
    QProgressBar, QScrollArea, QFileDialog, QListWidgetItem, QTextBrowser
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QLocale

from controller.myGithub import myGithub
from controller.myBloom import myBloom
from UI.Braverge_elementViewer_QTreeWidget import ElementViewer 
from controller.ViewManagement import ViewManagement

from graphviz import Digraph




class MergeManager(QWidget):
    def __init__(self, workSpacePath, GitHub_Object, Selected_Repository_name, fileDirP, VersionID_parent_or_child, MetamodelPath, operation_flag, scale=1.0):
        super().__init__()
        self.scale = scale
        self.workSpacePath = workSpacePath
        self.GitHub_Object = myGithub("empty")
        self.GitHub_Object = GitHub_Object
        self.Selected_Repository_name = Selected_Repository_name
        self.fileDirP = fileDirP
        self.newVersionID = VersionID_parent_or_child
        self.MetamodelPath = MetamodelPath
        self.Conflict_Decision_List = []
        self.Conflict_Decision_Keep_list = []
        self.operation_flag = operation_flag

        if self.operation_flag == "merge":
            self.setWindowTitle("Braverge Merge Manager")
        else:
            self.setWindowTitle("Braverge Update Manager")

        # --- Root Layout ---
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setLayout(root_layout)

        # --- Topbar ---
        topbar = QFrame()
        topbar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #ddd;")
        topbar_layout = QHBoxLayout()
        topbar_layout.setContentsMargins(20, 10, 20, 10)

        title_text = (
            "🔀 Braverge Merge Manager"
            if self.operation_flag == "merge"
            else "🔀 Braverge Update Manager"
        )

        app_title = QLabel(title_text)

        app_title.setStyleSheet(f"""
            font-size: {int(20 * self.scale)}px; 
            font-weight: Bold; 
            color: #1e2a38;
        """)

        topbar_layout.addWidget(app_title)
        topbar_layout.addStretch()

        topbar.setLayout(topbar_layout)
        root_layout.addWidget(topbar)

        # --- Body Layout ---
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addLayout(body_layout)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #f9f9f9; border-right: 1px solid #ddd;")
        self.sidebar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        body_layout.addWidget(self.sidebar)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(15)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)

        # --- Track active sidebar button ---
        self.active_sidebar_button = None
        self.sidebar_buttons = []

        # --- Sidebar Sections ---
        title_text = (
            "Merge Options"
            if self.operation_flag == "merge"
            else "Update Options"
        )
        self.add_sidebar_section(sidebar_layout, title_text, [
            ("⚡ Automatic", self.show_auto_mode),
            ("✏️ Semi-Automatic", self.show_manual_mode)
        ])
        self.add_sidebar_section(sidebar_layout, "Reports", [
            ("📄 Automatic Report", self.show_auto_report),
            ("📄 Semi-Automatic Report", self.show_manual_report)
        ])
        self.add_sidebar_section(sidebar_layout, "Settings", [
            ("⚙️ Preferences", self.show_preferences),
            ("🛈 Help", self.show_help)
        ], add_divider=False)
        sidebar_layout.addStretch()

        # --- Main Content ---
        self.content = QFrame()
        self.content.setStyleSheet("background: #fafafa;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        self.content.setLayout(content_layout)
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout.addWidget(self.content, stretch=1)

        # --- Header ---
        title_text = (
            "Automatic Merge"
            if self.operation_flag == "merge"
            else "Automatic Update"
        )
        self.header_label = QLabel(title_text)
        content_layout.addWidget(self.header_label)

        # --- Summary Cards with Icons ---
        self.summary_frame = QHBoxLayout()
        self.cards = {}

        card_data = [
            ("Changes", self.resource_path("UI/icons/total.png")),
            ("Conflicts", self.resource_path("UI/icons/conflict.png")),
            ("Resolved", self.resource_path("UI/icons/resolved.png")),
            ("Remaining", self.resource_path("UI/icons/remaining.png")),
        ]

        for metric, icon_path in card_data:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 24px;
                }
            """)
            cl = QVBoxLayout()
            cl.setContentsMargins(15, 15, 15, 15)

            title_layout = QHBoxLayout()
            title_layout.setAlignment(Qt.AlignVCenter)

            icon_label = QLabel()
            pixmap = QPixmap(icon_path)

            if not pixmap.isNull():
                pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)

            icon_label.setFixedSize(50, 50)
            icon_label.setStyleSheet("background: transparent;")

            title_label = QLabel(metric)

            title_layout.addWidget(icon_label)
            title_layout.addSpacing(10)
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            value_label = QLabel("0")
            value_label.setAlignment(Qt.AlignCenter)

            cl.addLayout(title_layout)
            cl.addSpacing(5)
            cl.addWidget(value_label)
            cl.addStretch()
            card.setLayout(cl)
            self.cards[metric] = value_label
            self.summary_frame.addWidget(card)

        content_layout.addLayout(self.summary_frame)

        # --- Card Container (Scrollable) ---
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {background:white; border:1px solid #ddd; border-radius:12px;}
        """)
        self.card_layout = QVBoxLayout()
        self.card_layout.setContentsMargins(15, 15, 15, 15)
        self.card.setLayout(self.card_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.card)
        content_layout.addWidget(scroll, stretch=1)

        # --- Progress Bar + Status ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {border:1px solid #ccc; border-radius:10px; height:22px; text-align:center;}
            QProgressBar::chunk {background-color:#4285f4; border-radius:10px;}
        """)
        self.status_label = QLabel("")
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.status_label)

        # --- Buttons Layout ---
        buttons_MC_layout = QHBoxLayout()

        # --- Left Side Buttons ---
        left_buttons_layout = QHBoxLayout()
        left_buttons_layout.setSpacing(10)

        self.ElementViewer_btn = QPushButton("Element Viewer")
        self.AskGemini_btn = QPushButton("Ask AI")
        self.ConflictDetection_btn = QPushButton("Conflict Detection")

        # Common style for left buttons
        for btn in (self.ElementViewer_btn, self.AskGemini_btn, self.ConflictDetection_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #4285f4;
                    color: white;
                    border-radius: 12px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #7891BB;
                }
            """)
            left_buttons_layout.addWidget(btn)

        # --- Right Side Buttons ---
        right_buttons_layout = QHBoxLayout()
        right_buttons_layout.setSpacing(10)

        title_text = (
            "▶ Perform Merge"
            if self.operation_flag == "merge"
            else "▶ Perform Update"
        )
        self.merge_auto_btn = QPushButton(title_text)
        self.merge_manu_btn = QPushButton(title_text)

        # Common style for right buttons
        for btn in (self.merge_manu_btn, self.merge_auto_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #4285f4;
                    color: white;
                    border-radius: 12px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #7891BB;
                }
            """)
            right_buttons_layout.addWidget(btn)

        # --- Assemble Main Buttons Layout ---
        buttons_MC_layout.addLayout(left_buttons_layout)  # left buttons
        buttons_MC_layout.addStretch()                     # push right buttons to the right
        buttons_MC_layout.addLayout(right_buttons_layout) # right buttons

        # Add to main content layout
        content_layout.addLayout(buttons_MC_layout)
        
        # --- Persistent Widgets ---
        self.report_view = QTextEdit()
        self.report_view.setReadOnly(True)
        self.report_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
        self.conflict_list = QListWidget()
        self.conflict_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        title_text = (
            "▶ Perform Merge"
            if self.operation_flag == "merge"
            else "▶ Perform Update"
        )
        self.conflicts = [
            "Click the 'Conflict Detection' button to identify potential conflicts.",
            f"After resolving all conflicts, click '{title_text}' to begin the integration process.",
        ]
        self.conflict_list.addItems(self.conflicts)
        self.conflict_list.setEnabled(False)

        self.conflict_actions = QHBoxLayout()
        self.accept_left = QPushButton("← Accept Parent Change")
        self.accept_right = QPushButton("Accept Child Change →")
        self.skip_btn = QPushButton("Skip Both ✖")
        for btn in (self.accept_left, self.accept_right, self.skip_btn):
            btn.setStyleSheet("""
                QPushButton {background:#f5f5f5; border:1px solid #ccc; border-radius:10px; padding:8px 12px;}
                QPushButton:hover {background:#eaeaea;}
            """)
            self.conflict_actions.addWidget(btn)

        self.card_layout.addWidget(self.conflict_list)
        self.card_layout.addLayout(self.conflict_actions)
        self.set_conflict_buttons_visible(False)
        self.conflict_list.setVisible(False)

        self.save_btn = QPushButton("💾 Save Report")
        self.save_btn.setStyleSheet("""
            QPushButton {background:#34a853; color:white; border-radius:12px; padding:10px 16px;}
            QPushButton:hover {background:#2c8f45;}
        """)
        self.save_btn.setEnabled(False)

        # --- Manual Mode Info Panel ---
        self.info_panel = QFrame()
        self.info_panel_layout = QHBoxLayout()
        self.info_panel.setLayout(self.info_panel_layout)
        self.info_panel.setVisible(False)

        self.left_view = QTextEdit()
        self.left_view.setReadOnly(True)
        self.left_view.setPlaceholderText("Left version element...")

        self.right_view = QTextEdit()
        self.right_view.setReadOnly(True)
        self.right_view.setPlaceholderText("Right version element...")

        self.info_panel_layout.addWidget(self.left_view)
        self.info_panel_layout.addWidget(self.right_view)

        # --- Data ---
        self.merge_decisions = []
        self.final_report_auto = None
        self.final_report_manual = None

        # --- Connections ---
        
        self.merge_auto_btn.clicked.connect(self.perform_Auto_merge)
        self.merge_manu_btn.clicked.connect(self.perform_Manu_merge)
        self.ConflictDetection_btn.clicked.connect(self.perform_conflict_detection)
        self.AskGemini_btn.clicked.connect(self._AskGemini_function)
        self.ElementViewer_btn.clicked.connect(self.Open_ElementViewer)
        self.accept_left.clicked.connect(lambda: self.resolve_conflict("Left"))
        self.accept_right.clicked.connect(lambda: self.resolve_conflict("Right"))
        self.skip_btn.clicked.connect(lambda: self.resolve_conflict("Skipped"))
        self.save_btn.clicked.connect(self.save_report)
        self.conflict_list.itemClicked.connect(self.show_conflict_info)

        # Default view
        self.show_auto_mode()

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.getcwd())
        return os.path.join(base_path, relative_path)

    # ------------------- Sidebar Helper -------------------
    def add_sidebar_section(self, layout, section_name, buttons, add_divider=True):
        header = QLabel(section_name)
        header.setStyleSheet(f"""
            font-size: {int(12 * self.scale)}px; 
            font-weight: 600; 
            color: #1e2a38;
        """)
        layout.addWidget(header)

        if "Merge" in section_name:
            hover_color = "#e3f2fd"
        elif "Reports" in section_name:
            hover_color = "#e8f5e9"
        elif "Settings" in section_name:
            hover_color = "#fff3e0"
        else:
            hover_color = "#f0f0f0"

        for text, callback in buttons:
            btn = QPushButton(text)
            # Removed explicit font setting for buttons
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #ffffff; 
                    border: 1px solid #ccc; 
                    border-radius: 10px; 
                    padding: 10px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background:{hover_color};
                }}
            """)
            # use default args to capture callback/button correctly
            btn.clicked.connect(lambda checked, b=btn, cb=callback: self.sidebar_button_clicked(b, cb))
            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        if add_divider:
            divider = QFrame()
            divider.setFrameShape(QFrame.HLine)
            divider.setFrameShadow(QFrame.Sunken)
            layout.addWidget(divider)

        layout.addSpacing(5)

    def sidebar_button_clicked(self, button, callback):
        # Reset previous active (safely)
        if self.active_sidebar_button and self.active_sidebar_button != button:
            # restore background white by re-applying the same base style
            base_style = self.active_sidebar_button.styleSheet().replace("background: #d0e8ff;", "background: #ffffff;")
            self.active_sidebar_button.setStyleSheet(base_style)

        # Set new active
        btn_style = button.styleSheet().replace("background: #ffffff;", "background: #d0e8ff;")
        button.setStyleSheet(btn_style)
        self.active_sidebar_button = button

        # Call original callback
        callback()

    # ------------------- Card clearing (safe) -------------------
    def clear_card(self):
        """
        Remove all non-persistent widgets/layouts from self.card_layout.
        Persistent widgets/layouts: self.conflict_list, self.conflict_actions layout,
        self.info_panel, self.report_view, self.save_btn
        """
        persistent_widgets = {self.conflict_list, self.info_panel, self.report_view, self.save_btn}
        persistent_layouts = {self.conflict_actions}

        # iterate from end to start to safely remove items
        for i in reversed(range(self.card_layout.count())):
            item = self.card_layout.itemAt(i)
            # skip persistent layouts
            if item.layout() and item.layout() in persistent_layouts:
                # keep the layout but hide its widgets
                continue

            widget = item.widget()
            if widget and widget in persistent_widgets:
                # keep the widget (but hide it), do not remove
                widget.setVisible(False)
                continue

            # otherwise remove and delete
            if widget:
                self.card_layout.removeWidget(widget)
                widget.setParent(None)
            elif item.layout():
                # remove entire layout and its children
                layout = item.layout()
                # if it's one of the persistent layouts, skip (handled above)
                if layout in persistent_layouts:
                    continue
                # clear children
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
                    elif child.layout():
                        # recursively clear nested layouts if any
                        sub = child.layout()
                        while sub.count():
                            sub_child = sub.takeAt(0)
                            if sub_child.widget():
                                sub_child.widget().setParent(None)
                self.card_layout.removeItem(layout)

    def set_conflict_buttons_visible(self, visible=True):
        for i in range(self.conflict_actions.count()):
            widget = self.conflict_actions.itemAt(i).widget()
            if widget:
                widget.setVisible(visible)

        # also toggle the conflict_list visibility
        self.conflict_list.setVisible(visible)

    # ------------------- Modes -------------------
    def show_auto_mode(self):
        title_text = (
            "Automatic Merge"
            if self.operation_flag == "merge"
            else "Automatic Update"
        )
        self.header_label.setText(title_text)
        self.header_label.setStyleSheet(f"""
            font-size: {int(16 * self.scale)}px; 
            font-weight: 600; 
            color: #1e2a38;
        """)
        # font = self.header_label.font()
        # font.setBold(True)
        # self.header_label.setFont(font)
        self.clear_card()

        title_text = (
            "▶ Perform Merge"
            if self.operation_flag == "merge"
            else "▶ Perform Update"
        )
        label = QLabel(f"Click {title_text} to start the process.")
        # Removed explicit font setting
        label.setWordWrap(True)
        self.card_layout.addWidget(label)

        self.merge_auto_btn.setVisible(True)
        self.merge_auto_btn.setEnabled(True)

        self.merge_manu_btn.setVisible(False)

        # hide manual widgets
        self.set_conflict_buttons_visible(False)
        self.info_panel.setVisible(False)
        self.save_btn.setEnabled(False)
        self.ConflictDetection_btn.setVisible(False)
        self.ElementViewer_btn.setVisible(False)
        self.AskGemini_btn.setVisible(False)

    def show_manual_mode(self):
        self.header_label.setText("Semi-Automatic Conflict Resolution")
        self.clear_card()
        #self.card_layout.addWidget(QLabel("Conflicts to resolve:"))

        # add persistent conflict_list (it may have been hidden)
        if self.conflict_list.parent() != self.card:
            self.card_layout.addWidget(self.conflict_list)
        self.conflict_list.setVisible(True)

        # add persistent conflict actions layout (only if not already present)
        # We can't check parent for layouts easily; if first child is not a layout we add it
        found_conflict_actions = any(
            isinstance(self.card_layout.itemAt(i).layout(), QHBoxLayout) and
            self.card_layout.itemAt(i).layout() is self.conflict_actions
            for i in range(self.card_layout.count())
        )
        if not found_conflict_actions:
            self.card_layout.addLayout(self.conflict_actions)

        # Info panel (will be shown after selecting a conflict)
        if self.info_panel.parent() != self.card:
            self.card_layout.addWidget(self.info_panel)
        self.info_panel.setVisible(False)

        # Show conflict buttons and disable merge until resolved
        self.set_conflict_buttons_visible(True)
        self.merge_auto_btn.setVisible(False)
        
        self.merge_manu_btn.setVisible(True)
        self.merge_manu_btn.setEnabled(False)


        self.save_btn.setEnabled(False)
        self.ConflictDetection_btn.setVisible(True)
        self.AskGemini_btn.setVisible(True)
        self.ElementViewer_btn.setVisible(True)

    # ------------------- Reports -------------------
    def show_auto_report(self):
        
        self.header_label.setText("Automatic Operation Report")
        self.clear_card()
        self.report_view.setFontFamily("Consolas")  # or "Courier New"
        self.report_view.setFontPointSize(10)
        if self.final_report_auto:
            self.report_view.setText(json.dumps(self.final_report_auto, indent=4, ensure_ascii=False))
            self.save_btn.setEnabled(True)
        else:
            self.report_view.setText("No automatic operation report available.")
            self.save_btn.setEnabled(False)

        if self.report_view.parent() != self.card:
            self.card_layout.addWidget(self.report_view)
        self.report_view.setVisible(True)

        # add save button to layout (if not present already)
        if self.save_btn.parent() != self.card:
            # wrap save button in a right-aligned container
            right_box = QHBoxLayout()
            right_box.addStretch()
            right_box.addWidget(self.save_btn)
            self.card_layout.addLayout(right_box)
        self.merge_manu_btn.setVisible(False)
        self.merge_auto_btn.setVisible(False)
        self.ConflictDetection_btn.setVisible(False)
        self.AskGemini_btn.setVisible(False)
        self.ElementViewer_btn.setVisible(False)
        self.set_conflict_buttons_visible(False)

    def show_manual_report(self):
        
        self.header_label.setText("Semi-Automatic Operation Report")
        self.clear_card()
        self.report_view.setFontFamily("Consolas")  # or "Courier New"
        self.report_view.setFontPointSize(10)
        if self.final_report_manual:
            self.report_view.setText(json.dumps(self.final_report_manual, indent=4, ensure_ascii=False))
            self.save_btn.setEnabled(True)
        else:
            self.report_view.setText("No Semi-Automatic operation report available.")
            self.save_btn.setEnabled(False)

        if self.report_view.parent() != self.card:
            self.card_layout.addWidget(self.report_view)
        self.report_view.setVisible(True)

        if self.save_btn.parent() != self.card:
            right_box = QHBoxLayout()
            right_box.addStretch()
            right_box.addWidget(self.save_btn)
            self.card_layout.addLayout(right_box)
        self.merge_manu_btn.setVisible(False)
        self.merge_auto_btn.setVisible(False)
        self.ConflictDetection_btn.setVisible(False)
        self.AskGemini_btn.setVisible(False)
        self.ElementViewer_btn.setVisible(False)

        self.set_conflict_buttons_visible(False)

    # ------------------- Conflict handling -------------------
    def show_conflict_info(self, item):
        conflict_text = item.text()
        conflict_item = item.data(Qt.UserRole)
        
        if (len(conflict_item) == 4):
            self.Element_Left = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[2]['internal_id'], self.myBloom_Object.Version_Left)
            json_left = self.myBloom_Object.find_all_properties_of_element(self.Element_Left)
            self.left_view.setText(f"Left version element:\n{conflict_text}\n{json_left}")

            self.Element_Right = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[3]['internal_id'], self.myBloom_Object.Version_Right)
            json_right = self.myBloom_Object.find_all_properties_of_element(self.Element_Right)
            self.right_view.setText(f"Right version element:\n{conflict_text}\n{json_right}")
        else:
            self.Element_Left = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[0]['internal_id'], self.myBloom_Object.Version_Left)
            self.Element_Right = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[1]['internal_id'], self.myBloom_Object.Version_Right)
            if self.Element_Left is None: self.Element_Left = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[0]['internal_id'], self.myBloom_Object.Version_Base)
            if self.Element_Right is None: self.Element_Right = self.myBloom_Object.find_element_in_model_by_ID(conflict_item[1]['internal_id'], self.myBloom_Object.Version_Base)

            json_left = self.myBloom_Object.find_all_properties_of_element(self.Element_Left)
            self.left_view.setText(f"Left version element:\n{conflict_text}\n{json_left}")

            
            json_right = self.myBloom_Object.find_all_properties_of_element(self.Element_Right)
            self.right_view.setText(f"Right version element:\n{conflict_text}\n{json_right}")

        self.info_panel.setVisible(True)

    def resolve_conflict(self, decision):
        try:
            row = self.conflict_list.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No Selection", "Select a conflict to resolve.")
                return
            #conflict_text = self.conflict_list.currentItem().text()
            #self.merge_decisions.append({"conflict type": conflict_text, "decision": decision})

            item = self.conflict_list.currentItem()
            numbered_text = item.text()  # e.g. "Conflict 3: Delete-Use-Old Conflict"
            conflict_item = item.data(Qt.UserRole)  # your actual conflict object or ID

            # selecting left means user wants to keep item 1.
            # selecting right means user wants to keep item 0.
            # item is change!
            if decision == "Left":
                # Therefore, user decide to keep left (item [1]). right (item [0]) will be ignored by adding in Conflict_Decision_List!
                # left is changes on the parent branch. right is changes on the current branch.
                if (len(conflict_item) == 4):
                    self.Conflict_Decision_Keep_list.append(conflict_item[1])
                    self.Conflict_Decision_Keep_list.append(conflict_item[3])

                    self.Conflict_Decision_List.append(conflict_item[0])
                    self.Conflict_Decision_List.append(conflict_item[2])
                else:
                    self.Conflict_Decision_Keep_list.append(conflict_item[1])

                    self.Conflict_Decision_List.append(conflict_item[0])
            elif decision == "Right":
                # item [1] will be ignored!
                if (len(conflict_item) == 4):
                    self.Conflict_Decision_Keep_list.append(conflict_item[0])
                    self.Conflict_Decision_Keep_list.append(conflict_item[2])

                    self.Conflict_Decision_List.append(conflict_item[1])
                    self.Conflict_Decision_List.append(conflict_item[3])
                else:
                    self.Conflict_Decision_Keep_list.append(conflict_item[0])
                    
                    self.Conflict_Decision_List.append(conflict_item[1])
            else:
                # item [0] and [1] will be ignored!
                if (len(conflict_item) == 4):
                    self.Conflict_Decision_List.append(conflict_item[0])
                    self.Conflict_Decision_List.append(conflict_item[1])
                    self.Conflict_Decision_List.append(conflict_item[2])
                    self.Conflict_Decision_List.append(conflict_item[3])
                else:
                    self.Conflict_Decision_List.append(conflict_item[0])
                    self.Conflict_Decision_List.append(conflict_item[1])
            
            # Extract the conflict id and type from the numbered text
            # Example text: "Conflict 3: Delete-Use-Old Conflict"
            # Let's parse it simply:
            conflict_id = numbered_text.split(":")[0].strip().lower().replace(" ", "_")  # 'conflict_3'
            conflict_type = numbered_text.split(":")[1].strip()  # 'Delete-Use-Old Conflict'

            element_left_conflict = next((m.group(0) for m in [re.search(r'\{.*\}', self.left_view.toPlainText(), re.DOTALL)] if m), None)
            element_right_conflict = next((m.group(0) for m in [re.search(r'\{.*\}', self.right_view.toPlainText(), re.DOTALL)] if m), None)

            # Append to merge_decisions list
            self.merge_decisions.append({
                "conflict id": conflict_id,
                "conflict type": conflict_type,
                "decision": decision,
                "element left version": element_left_conflict,
                "element right version": element_right_conflict

            })
            #"conflict data": conflict_item  # optional, if you want to store actual data

            self.conflict_list.takeItem(row)
            self.info_panel.setVisible(False)
            self.update_summary(int(self.cards["Changes"].text()), int(self.cards["Conflicts"].text()), resolved=int(self.cards["Resolved"].text()) + 1, remaining= int(self.cards["Remaining"].text()) - 1)

            if self.conflict_list.count() == 0:
                QMessageBox.information(self, "Operation Complete", "All conflicts resolved!")
                self.merge_manu_btn.setEnabled(True)  # enable merge now
                self.final_report_auto = None
                self.final_report_manual = {
                    "mode": "Semi-Automatic",
                    "summary": "Semi-Automatic operation completed",
                    "resolved_conflicts": self.merge_decisions
                }
                # update summary with example numbers (ideally real data should be passed)
                self.update_summary(int(self.cards["Changes"].text()), conflicts=len(self.merge_decisions), resolved=len(self.merge_decisions), remaining=0)
                # optionally show manual report automatically
                # self.show_manual_report()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ------------------- Merge Logic -------------------
    def perform_Manu_merge(self):
        
        CONFLICT_DELETE_UPDATE = self.myBloom_Object.CONFLICT_DELETE_UPDATE
        CONFLICT_DELETE_USE_OLD = self.myBloom_Object.CONFLICT_DELETE_USE_OLD
        CONFLICT_DELETE_MOVE = self.myBloom_Object.CONFLICT_DELETE_MOVE
        CONFLICT_DELETE_ADD = self.myBloom_Object.CONFLICT_DELETE_ADD
        CONFLICT_UPDATE_UPDATE = self.myBloom_Object.CONFLICT_UPDATE_UPDATE
        CONFLICT_MOVE_MOVE = self.myBloom_Object.CONFLICT_MOVE_MOVE
        CONFLICT_INSERT_INSERT = self.myBloom_Object.CONFLICT_INSERT_INSERT
        Conflicts_Number = len(CONFLICT_DELETE_UPDATE) + len(CONFLICT_DELETE_USE_OLD) + len(CONFLICT_DELETE_MOVE) + len(CONFLICT_DELETE_ADD) + len(CONFLICT_UPDATE_UPDATE) + len(CONFLICT_MOVE_MOVE) + len(CONFLICT_INSERT_INSERT)

        try:
            # reset progress and UI state
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0%")
            self.status_label.setText("Processing... Please wait")
            self.merge_manu_btn.setEnabled(False)

            def step_progress(step=0):
                if step <= 100:
                    self.progress_bar.setValue(min(step, 100))
                    self.progress_bar.setFormat(f"{min(step, 100)}%")
                    QTimer.singleShot(40, lambda: step_progress(step + 5))
                    if step == 50: 
                        self.GitHub_Object.GitHub_Merge_Models(self.workSpacePath + "/", self.MetamodelPath, self.Conflict_Decision_List, self.Conflict_Decision_Keep_list)
                        src= self.workSpacePath + "/" + 'Target.xmi'
                        dst= self.workSpacePath + "/" + self.newVersionID #+ ".xmi"
                        shutil.copy(src,dst)
                    if step == 80:
                        ## uploading merged version on the parent branch 
                        self.GitHub_Object.uploadFile(self.workSpacePath + "/" + self.newVersionID, self.newVersionID , self.fileDirP, self.Selected_Repository_name)

                else:
                    # finalization
                    self.progress_bar.setValue(100)
                    self.progress_bar.setFormat("100%")
                    self.status_label.setText("✅ Operation Completed!")
                    self.merge_manu_btn.setEnabled(True)
                    self.save_btn.setEnabled(True)
                    # update summary
                    self.update_summary(int(self.cards["Changes"].text()), conflicts= Conflicts_Number, resolved= Conflicts_Number, remaining=0)

            step_progress()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.merge_manu_btn.setEnabled(True)

    def Open_ElementViewer(self):
        if (self.conflict_list.count() == 0):
            QMessageBox.information(self, "Element Viewer", "There is no available conflict!")
        elif not self.conflict_list.selectedItems():
            QMessageBox.information(self, "Element Viewer", "There is no selected conflict!")
        else:
            element_data_left = self.myBloom_Object.find_all_properties_of_element(self.Element_Left)
            element_data_right = self.myBloom_Object.find_all_properties_of_element(self.Element_Right)
            self.element_viewer_window = ElementViewer(element_data_left, element_data_right, self.scale)
            self.element_viewer_window.show()

    def _AskGemini_function(self):
        try:
            self.gemini_object = ViewManagement()
            response = self.gemini_object.ask_Gemini_conflict_explanation(
                self.left_view.toPlainText() + self.right_view.toPlainText()
            )
            QMessageBox.information(self, "Ask AI", f"{response}")

        except ConnectionError:
            QMessageBox.critical(self, "Connection Error", "Cannot connect to Gemini. Please check your network or Gemini service status.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def perform_conflict_detection(self):
        self.myBloom_Object = myBloom(self.GitHub_Object.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.load_left_right_versions(self.MetamodelPath, self.workSpacePath + "/" + "Left.xmi",
                                                     self.workSpacePath + "/" + "Right.xmi",
                                                     self.workSpacePath + "/" + "Base.xmi")
        
        self.myBloom_Object.compare_two_models_UUID(self.MetamodelPath,
                                                    self.workSpacePath + "/" + "Left.xmi",
                                                    self.workSpacePath + "/" + "Base.xmi",
                                                    self.workSpacePath + "/")
        with open(self.workSpacePath + "/" + 'Version_Info.json', 'r') as jfile:
            dataJson_LEFT_BASE = json.load(jfile)
        jfile.close()
        self.myBloom_Object.compare_two_models_UUID(self.MetamodelPath,
                                                    self.workSpacePath + "/" + "Right.xmi",
                                                    self.workSpacePath + "/" + "Base.xmi",
                                                    self.workSpacePath + "/")
        with open(self.workSpacePath + "/" + 'Version_Info.json', 'r') as jfile:
            dataJson_Right_BASE = json.load(jfile)
        jfile.close()

        numberOfChanges = sum(
            len(d.get(k, []))
            for base in (dataJson_LEFT_BASE, dataJson_Right_BASE)
            for d in base
            for k in ('UPDATE', 'DELETE', 'ADD')
        )

        detected_Conflicts = self.myBloom_Object.Conflict_Detection(dataJson_LEFT_BASE, dataJson_Right_BASE)
        
        CONFLICT_DELETE_UPDATE = self.myBloom_Object.CONFLICT_DELETE_UPDATE
        CONFLICT_DELETE_USE_OLD = self.myBloom_Object.CONFLICT_DELETE_USE_OLD
        CONFLICT_DELETE_MOVE = self.myBloom_Object.CONFLICT_DELETE_MOVE
        CONFLICT_DELETE_ADD = self.myBloom_Object.CONFLICT_DELETE_ADD
        CONFLICT_UPDATE_UPDATE = self.myBloom_Object.CONFLICT_UPDATE_UPDATE
        CONFLICT_MOVE_MOVE = self.myBloom_Object.CONFLICT_MOVE_MOVE
        CONFLICT_INSERT_INSERT = self.myBloom_Object.CONFLICT_INSERT_INSERT

        Conflicts_Number = len(CONFLICT_DELETE_UPDATE) + len(CONFLICT_DELETE_USE_OLD) + len(CONFLICT_DELETE_MOVE) + len(CONFLICT_DELETE_ADD) + len(CONFLICT_UPDATE_UPDATE) + len(CONFLICT_MOVE_MOVE) + len(CONFLICT_INSERT_INSERT)

        self.cards["Changes"].setText(str(numberOfChanges))
        self.cards["Conflicts"].setText(str(Conflicts_Number))
        self.cards["Remaining"].setText(str(Conflicts_Number))
        self.Conflict_Decision_List.clear()
        self.Conflict_Decision_Keep_list.clear()
        self.conflict_list.clear()  
        self.conflict_list.setEnabled(True)
        conflict_map = {
            "CONFLICT_DELETE_ADD": (CONFLICT_DELETE_ADD, "Delete-Use-New Conflict"),
            "CONFLICT_DELETE_USE_OLD": (CONFLICT_DELETE_USE_OLD, "Delete-Use-Old Conflict"),
            "CONFLICT_DELETE_MOVE": (CONFLICT_DELETE_MOVE, "Delete-Move Conflict"),
            "CONFLICT_DELETE_UPDATE": (CONFLICT_DELETE_UPDATE, "Delete-Update Conflict"),
            "CONFLICT_UPDATE_UPDATE": (CONFLICT_UPDATE_UPDATE, "Update-Update Conflict"),
            "CONFLICT_MOVE_MOVE": (CONFLICT_MOVE_MOVE, "Move-Move Conflict"),
            "CONFLICT_INSERT_INSERT": (CONFLICT_INSERT_INSERT, "Insert-Insert Conflict"),
        }

        global_counter = 1
        for _, (conflict_list, display_text) in conflict_map.items():
            for conflict_item in conflict_list:
                numbered_text = f"Conflict {global_counter}: {display_text}"
                list_item = QListWidgetItem(numbered_text)
                list_item.setData(Qt.UserRole, conflict_item)
                self.conflict_list.addItem(list_item)
                global_counter += 1

        if Conflicts_Number == 0:
            self.merge_manu_btn.setEnabled(True)
        
    def perform_Auto_merge(self):
        self.myBloom_Object = myBloom(self.GitHub_Object.getMETAMODEL_PATH_FILE())
        self.myBloom_Object.load_left_right_versions(self.MetamodelPath, self.workSpacePath + "/" + "Left.xmi",
                                                     self.workSpacePath + "/" + "Right.xmi",
                                                     self.workSpacePath + "/" + "Base.xmi")
        self.myBloom_Object.compare_two_models_UUID(self.MetamodelPath,
                                                    self.workSpacePath + "/" + "Left.xmi",
                                                    self.workSpacePath + "/" + "Base.xmi",
                                                    self.workSpacePath + "/")
        with open(self.workSpacePath + "/" + 'Version_Info.json', 'r') as jfile:
            dataJson_LEFT_BASE = json.load(jfile)
        jfile.close()
        self.myBloom_Object.compare_two_models_UUID(self.MetamodelPath,
                                                    self.workSpacePath + "/" + "Right.xmi",
                                                    self.workSpacePath + "/" + "Base.xmi",
                                                    self.workSpacePath + "/")
        with open(self.workSpacePath + "/" + 'Version_Info.json', 'r') as jfile:
            dataJson_Right_BASE = json.load(jfile)
        jfile.close()
        numberOfChanges = sum(
            len(d.get(k, []))
            for base in (dataJson_LEFT_BASE, dataJson_Right_BASE)
            for d in base
            for k in ('UPDATE', 'DELETE', 'ADD')
        )
        detected_Conflicts = self.myBloom_Object.Conflict_Detection(dataJson_LEFT_BASE, dataJson_Right_BASE)
        CONFLICT_DELETE_UPDATE = self.myBloom_Object.CONFLICT_DELETE_UPDATE
        CONFLICT_DELETE_USE_OLD = self.myBloom_Object.CONFLICT_DELETE_USE_OLD
        CONFLICT_DELETE_MOVE = self.myBloom_Object.CONFLICT_DELETE_MOVE
        CONFLICT_DELETE_ADD = self.myBloom_Object.CONFLICT_DELETE_ADD
        CONFLICT_UPDATE_UPDATE = self.myBloom_Object.CONFLICT_UPDATE_UPDATE
        CONFLICT_MOVE_MOVE = self.myBloom_Object.CONFLICT_MOVE_MOVE
        CONFLICT_INSERT_INSERT = self.myBloom_Object.CONFLICT_INSERT_INSERT
        Conflicts_Number = len(CONFLICT_DELETE_UPDATE) + len(CONFLICT_DELETE_USE_OLD) + len(CONFLICT_DELETE_MOVE) + len(CONFLICT_DELETE_ADD) + len(CONFLICT_UPDATE_UPDATE) + len(CONFLICT_MOVE_MOVE) + len(CONFLICT_INSERT_INSERT)

        resolution = self.myBloom_Object.Prepered_List_of_Conflict_Detection_Resolution_Automatic_Merge(dataJson_LEFT_BASE, dataJson_Right_BASE)
        try:
            # reset progress and UI state
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0%")
            self.status_label.setText("Merging... Please wait")
            self.merge_auto_btn.setEnabled(False)

            def step_progress(step=0):
                if step <= 100:
                    self.progress_bar.setValue(min(step, 100))
                    self.progress_bar.setFormat(f"{min(step, 100)}%")
                    QTimer.singleShot(40, lambda: step_progress(step + 5))
                    if step == 50: 
                        self.GitHub_Object.GitHub_Merge_Models(self.workSpacePath + "/", self.MetamodelPath, resolution)
                        src= self.workSpacePath + "/" + 'Target.xmi'
                        dst= self.workSpacePath + "/" + self.newVersionID #+ ".xmi"
                        shutil.copy(src,dst)
                    if step == 80:
                        
                        ## uploading merged version on the parent branch 
                        self.GitHub_Object.uploadFile(self.workSpacePath + "/" + self.newVersionID, self.newVersionID , self.fileDirP, self.Selected_Repository_name)

                else:
                    # finalization
                    self.progress_bar.setValue(100)
                    self.progress_bar.setFormat("100%")
                    self.status_label.setText("✅ Operation Completed!")
                    self.merge_auto_btn.setEnabled(True)
                    self.final_report_manual = None
                    self.final_report_auto = { 
                        "mode": "automatic",
                        "summary": "Automatic operation completed successfully!",
                        "details": {
                            "All Changes": numberOfChanges,
                            "auto_resolved_conflicts": Conflicts_Number
                        },
                        "ignored changes": [
                            f"{i+1}. {item}" for i, item in enumerate(resolution)
                        ]
                    }

                    self.report_view.setText(json.dumps(self.final_report_auto, indent=4))
                    self.save_btn.setEnabled(True)
                    # update summary
                    self.update_summary(numberOfChanges, Conflicts_Number, Conflicts_Number, remaining=0)

            step_progress()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.merge_auto_btn.setEnabled(True)

    # ------------------- Save Report -------------------
    def save_report(self):
        try:
            current_report = None
            if self.header_label.text() == "Automatic Operation Report":
                current_report = self.final_report_auto
            else:
                current_report = self.final_report_manual

            if not current_report:
                QMessageBox.warning(self, "No Report", "No report to save.")
                return
            path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "JSON (*.json)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(current_report, f, indent=4)
                QMessageBox.information(self, "Saved", f"Report saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ------------------- Summary Update -------------------
    def update_summary(self, total=0, conflicts=0, resolved=0, remaining=0):
        try:
            self.cards["Changes"].setText(str(total))
            self.cards["Conflicts"].setText(str(conflicts))
            self.cards["Resolved"].setText(str(resolved))
            self.cards["Remaining"].setText(str(remaining))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ------------------- Sidebar Responsiveness -------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def update_sidebar_width(self):
        window_width = self.width()
        sidebar_width = max(280, min(int(window_width * 0.2), 400))
        self.sidebar.setMinimumWidth(sidebar_width)
        self.sidebar.setMaximumWidth(sidebar_width)

    # ------------------- Sidebar Links Placeholders -------------------
    def show_preferences(self):
        QMessageBox.critical(
            self,
            "Coming Soon 🚀",
            "preferences are almost here! Stay tuned — awesome new features are on the way!"
        )
        self.merge_auto_btn.setVisible(False)
        self.merge_manu_btn.setVisible(False)
        self.ConflictDetection_btn.setVisible(False)
        self.AskGemini_btn.setVisible(False)
        self.ElementViewer_btn.setVisible(False)


    def show_help(self):
        """Display an interactive Help page with internal links inside the main card layout."""

        # --- Update header ---
        self.header_label.setText("Help")

        # --- Clear previous content ---
        self.clear_card()

        # --- Create QTextBrowser for help content ---
        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setFont(QFont("Segoe UI Emoji, Noto Color Emoji, Apple Color Emoji, sans-serif", 11))
        help_text.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                padding: 10px;
                border: none;
            }
            a {
                color: #0078d7;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        """)

        # --- Set HTML Help Content with clickable Table of Contents ---
        help_text.setHtml("""
            <h2>Application Help</h2>

            <p>Welcome to <b>Braverge Merge/Update Tool</b> — a system for detecting and resolving
            model conflicts. This help page describes the key conflict types
            and how Braverge handles them.</p>

            <h3>📖 Table of Contents</h3>
            <ul>
                <li><a href="#delete-use">Delete-Use Conflict</a></li>
                <li><a href="#delete-update">Delete-Update Conflict</a></li>
                <li><a href="#update-update">Update-Update Conflict</a></li>
                <li><a href="#move-move">Move-Move Conflict</a></li>
                <li><a href="#insert-insert">Insert-Insert Conflict</a></li>
            </ul>

            <hr>
            <h3>⚙️ Conflict Types and Resolutions</h3>

            <h4 id="delete-use">✂ Delete-Use Conflict</h4>
            <p>
            A <b>Delete-Use Conflict</b> occurs when a reference is introduced to an element
            that has been concurrently deleted. This conflict combines two incompatible
            operations: deleting an element and referencing it from another element.
            Braverge distinguishes three subtypes:
            </p>
            <ul>
                <li><b>Delete-Use-Old Conflict:</b> An existing element references another element
                that has been deleted. Since the reference target no longer exists, the addition
                of this reference is either ignored automatically or flagged for user resolution.</li>

                <li><b>Delete-Use-New Conflict:</b> A newly created element references an element
                deleted by another client. To maintain consistency, the reference is ignored in
                automatic mode or presented to the client for decision.</li>

                <li><b>Delete-Move Conflict:</b> An element is deleted while its container is
                simultaneously changed (moved). Since a deleted element cannot be relocated,
                the move operation is discarded in automatic mode or flagged for user resolution.</li>
            </ul>

            <h4 id="delete-update">✂ Delete-Update Conflict</h4>
            <p>
            This conflict arises when one client deletes an element while another updates it
            (for example, by modifying its property values). In Braverge, deletions take precedence:
            updates to deleted elements are ignored automatically, or the conflict is presented
            to the client for semi-automatic resolution.
            </p>

            <h4 id="update-update">✏ Update-Update Conflict</h4>
            <p>
            When the same property of an element is modified concurrently in different versions,
            inconsistencies may occur. For single-valued properties, concurrent updates are
            irreconcilable; Braverge resolves them by prioritizing changes from the <b>right version</b>,
            while retaining historical versions for traceability.
            </p>
            <p>
            For multi-valued properties, resolution is more nuanced: common values are preserved,
            values deleted by either client are removed, and newly added values are retained.
            In user-driven mode, Braverge instead presents the alternatives for manual selection.
            </p>

            <h4 id="move-move">■ Move-Move Conflict</h4>
            <p>
            A special case of an update-update conflict occurs when an element is moved to
            different containers in parallel. Since EMF elements can belong to only one container,
            Braverge resolves this conflict by giving priority to the move from the <b>right version</b>,
            unless the client opts to override this decision.
            </p>

            <h4 id="insert-insert">▲ Insert-Insert Conflict</h4>
            <p>
            This conflict occurs when an element without a container is independently assigned
            to different containers in parallel versions. Since containment is exclusive, one
            insertion must be discarded. Braverge resolves this automatically by prioritizing
            the <b>right version</b>, or presents both alternatives to the client for resolution.
            </p>

            <hr>
            <p><i>For further details, please refer to the Braverge user documentation or contact support.</i></p>
        """)

        # --- Layout Assembly ---
        layout = QVBoxLayout()
        layout.addWidget(help_text)

        # Container widget for the card
        container = QWidget()
        container.setLayout(layout)
        self.card_layout.addWidget(container)

        # --- Hide unrelated buttons ---
        self.merge_auto_btn.setVisible(False)
        self.merge_manu_btn.setVisible(False)
        self.ConflictDetection_btn.setVisible(False)
        self.AskGemini_btn.setVisible(False)
        self.ElementViewer_btn.setVisible(False)

        # --- Disable save button if exists ---
        if hasattr(self, "save_btn"):
            self.save_btn.setEnabled(False)





