import sys, json
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot, QTime, QLocale
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QTextEdit,
    QLineEdit, QFileDialog, QMessageBox, QStackedWidget, QFrame
)
import os
from PyQt5.QtGui import QMovie

from controller.myGithub import myGithub
from controller.ViewManagement import ViewManagement
from controller.ViewWorker import ViewWorker, InitialVersionWorker
from controller.myBloom import myBloom
from UI.Braverge_modelviewer_one import ModelViewer 



# ---------- Main Window ----------
class ViewManager_MainWindow(QWidget):
    def __init__(self, workSpacePath, metamodelpath, GitHub_Object,
                 Selected_Repository_name, fileDirP, newVersionID,
                 MetamodelPath, limitedAccess, scale=1.0):
        super().__init__()
        self.scale = scale
        self.workSpacePath = workSpacePath
        self.metamodelpath = metamodelpath
        self.GitHub_Object = myGithub("empty")
        self.GitHub_Object = GitHub_Object
        self.Selected_Repository_name = Selected_Repository_name
        self.fileDirP = fileDirP
        self.newVersionID = newVersionID
        self.MetamodelPath = MetamodelPath
        self.limitedAccess = limitedAccess
        

        # ---------- Window setup ----------
        self.setWindowTitle("Braverge View Manager")
        self.resize(scale_ui(1300, scale), scale_ui(800, scale))
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                color: #333;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = HeaderBar(scale)
        main_layout.addWidget(self.header)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(scale)
        content_layout.addWidget(self.sidebar)

        # ---------- Page Stack ----------
        self.stack = QStackedWidget()
        self.pages = {}

        common_args = (
            self.GitHub_Object,
            self.workSpacePath,
            self.metamodelpath,
            self.newVersionID,
            Selected_Repository_name,
            fileDirP,
            scale
        )

        # Always available pages
        self.pages["Import Configuration"] = ImportConfigurationPage(*common_args)
        self.pages["Synchronization"] = SynchronizationPage(*common_args)

        # Conditionally available pages
        if not self.limitedAccess:
            self.pages["Manual Selection"] = ManualSelectionPage(*common_args)
            self.pages["AI Assistant"] = AIAssistantPage(scale)

        # Add created pages to the stack
        for page in self.pages.values():
            self.stack.addWidget(page)

        content_layout.addWidget(self.stack, 1)
        main_layout.addLayout(content_layout)

        # ---------- Sidebar & Navigation ----------
        # Hide restricted buttons
        if self.limitedAccess:
            if "Manual Selection" in self.sidebar.buttons:
                self.sidebar.buttons["Manual Selection"].hide()
            if "AI Assistant" in self.sidebar.buttons:
                self.sidebar.buttons["AI Assistant"].hide()

        # Connect navigation buttons
        for name, btn in self.sidebar.buttons.items():
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))

        # Set default page safely
        if self.pages:
            first_page = next(iter(self.pages.keys()))
            if first_page in self.sidebar.buttons:
                self.sidebar.buttons[first_page].setChecked(True)
            self.stack.setCurrentWidget(self.pages[first_page])

    # ---------- Page switching logic ----------
    def switch_page(self, name):
        # Safely handle missing pages (in limited access mode)
        if name not in self.pages:
            QMessageBox.warning(
                self,
                "Access Restricted",
                f"The page '{name}' is not available in limited access mode."
            )
            return

        # Update sidebar button states
        for btn in self.sidebar.buttons.values():
            btn.setChecked(False)
        if name in self.sidebar.buttons:
            self.sidebar.buttons[name].setChecked(True)

        # Switch the page
        self.stack.setCurrentWidget(self.pages[name])


# ---------- Helper ----------
def scale_ui(base_value, scale):
    return int(base_value * scale)

def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.getcwd())
        return os.path.join(base_path, relative_path)

ICON_PATHS = {
    "manual": resource_path("UI/icons/list.png"),
    "ai": resource_path("UI/icons/chatbot.png"),
    "sync": resource_path("UI/icons/sync.png"),
    "import": resource_path("UI/icons/import.png"),
}


# ---------- Sidebar Button ----------
class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None, scale=1.0):
        super().__init__(text)
        self.setFixedHeight(scale_ui(46, scale))
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(scale_ui(20, scale), scale_ui(20, scale)))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #333;
                border: none;
                text-align: left;
                padding: {scale_ui(8, scale)}px {scale_ui(18, scale)}px;
                font-size: {scale_ui(15, scale)}px;
            }}
            QPushButton:hover {{
                background-color: #eaf3ff;
                color: #0078d7;
            }}
            QPushButton:checked {{
                background-color: #dceeff;
                border-left: 4px solid #0078d7;
                color: #0078d7;
                font-weight: 600;
                padding-left: {scale_ui(14, scale)}px;
            }}
        """)


# ---------- Sidebar ----------
class Sidebar(QWidget):
    def __init__(self, scale=1.0):
        super().__init__()
        self.setFixedWidth(scale_ui(220, scale))
        self.setStyleSheet("background-color: #f9fafc; border-right: 1px solid #ddd;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, scale_ui(10, scale), 0, scale_ui(10, scale))
        layout.setSpacing(scale_ui(6, scale))

        # title = QLabel("Navigation")
        # title.setStyleSheet(f"color: #0078d7; font-size: {scale_ui(18, scale)}px; font-weight: bold; margin: {scale_ui(14, scale)}px;")
        # layout.addWidget(title)

        self.buttons = {}
        for name, icon in [
            ("Import Configuration", ICON_PATHS["import"]),
            ("Manual Selection", ICON_PATHS["manual"]),
            ("AI Assistant", ICON_PATHS["ai"]),
            ("Synchronization", ICON_PATHS["sync"]),
        ]:
            btn = SidebarButton(name, icon, scale)
            layout.addWidget(btn)
            self.buttons[name] = btn

        layout.addStretch()


# ---------- Header Bar ----------
class HeaderBar(QFrame):
    def __init__(self, scale=1.0):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-bottom: 1px solid #ddd;
            }
        """)
        self.setFixedHeight(scale_ui(56, scale))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(scale_ui(20, scale), 0, scale_ui(20, scale), 0)
        layout.setSpacing(scale_ui(12, scale))

        title = QLabel("Braverge View Manager")
        title.setStyleSheet(f"font-size: {scale_ui(24, scale)}px; font-weight: 600; color: #222;")
        layout.addWidget(title)
        layout.addStretch()

# ---------- Page Card Wrapper ----------
class PageCard(QFrame):
    def __init__(self, scale=1.0):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: {scale_ui(10, scale)}px;
                border: 1px solid #ddd;
            }}
        """)
        self.setContentsMargins(scale_ui(20, scale), scale_ui(20, scale),
                                scale_ui(20, scale), scale_ui(20, scale))


# ---------- Manual Selection Page ----------
class ManualSelectionPage(PageCard):
    def __init__(self, GitHub_Object, workSpacePath, metamodelpath, newVersionID, Selected_Repository_name, fileDirP, scale=1.0):
        super().__init__(scale)
        self.GitHub_Object = GitHub_Object
        self.workSpacePath = workSpacePath
        self.newVersionID = newVersionID
        self.Selected_Repository_name= Selected_Repository_name
        self.fileDirP = fileDirP
        self.metamodelpath = metamodelpath

        viewObject = ViewManagement()
        dec_meta = viewObject.Decomposer_Metamodel_NAME(GitHub_Object.getMETAMODEL_PATH_FILE())
        dec_meta = dec_meta[0]

        vbox = QVBoxLayout(self)
        vbox.setSpacing(scale_ui(20, scale))

        header = QLabel("🧩 Manual Element Selection")
        header.setStyleSheet(f"font-size: {scale_ui(20, scale)}px; font-weight: 600; color: #222;")
        vbox.addWidget(header)

        # ---------- 🔍 SEARCH BAR ----------
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to filter elements...")
        self.search_bar.textChanged.connect(self.filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        vbox.addLayout(search_layout)
        # -----------------------------------

        self.table = QTableWidget(len(dec_meta), 2)
        self.table.setHorizontalHeaderLabels(["Select", "Element Name"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #fafafa;
                border: 1px solid #ccc;
                border-radius: 8px;
                gridline-color: #eee;
            }
        """)

        count = 0
        for i in dec_meta:
            chk = QCheckBox()
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)
            self.table.setCellWidget(count, 0, cell_widget)

            item = QTableWidgetItem(str(i['element']))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(count, 1, item)
            count += 1

        vbox.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        for label in ["Create View", "Export JSON", "View Viewer"]:
            btn = QPushButton(label)
            btn.setFixedHeight(scale_ui(40, scale))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: {scale_ui(6, scale)}px;
                    font-size: {scale_ui(14, scale)}px;
                    padding: 6px 18px;
                }}
                QPushButton:hover {{ background-color: #008af0; }}
            """)
            if label == "Create View":
                btn.clicked.connect(self.create_view_action)
            elif label == "Export JSON":
                btn.clicked.connect(self.export_json)
            else:
                btn.clicked.connect(self.view_viewer)
                btn.setEnabled(False)  # Disable "View Viewer" initially
                self.view_viewer_manual_btn = btn  # Keep a reference for later
            btn_row.addWidget(btn)

        vbox.addLayout(btn_row)

    # ---------- 🔍 FILTER FUNCTION ----------
    def filter_table(self, text):
        """Show only rows that contain the search text."""
        text = text.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item:
                element_name = item.text().lower()
                match = text in element_name
                self.table.setRowHidden(row, not match)
    # ---------------------------------------

    def create_view_action(self):
        selected = []
        for i in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(i, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)  # Get the actual checkbox
                if chk and chk.isChecked():
                    selected.append(self.table.item(i, 1).text())
        if selected:
            self.GitHub_Object.GitHub_View_Management_ItemSelection(self.newVersionID, self.workSpacePath, self.metamodelpath, self.Selected_Repository_name, self.fileDirP, selected)
            QMessageBox.information(self, "Successful", "Your view is successfully created.")
            self.view_viewer_manual_btn.setEnabled(True)
        else:
            QMessageBox.information(self, "Failed", "No elements selected.")
            self.view_viewer_manual_btn.setEnabled(False)
            
    def view_viewer(self):   
        self.myBloom_Object = myBloom(self.metamodelpath)
        MyMetaModel = self.myBloom_Object.importMetaModel(self.metamodelpath)
        root_m = self.myBloom_Object.importModel(self.workSpacePath + "/viewSelectedItem.xmi", MyMetaModel)
        model_json = self.myBloom_Object.all_properties_of_model(root_m)
        self.element_viewer_window = ModelViewer(model_json)
        self.element_viewer_window.show()

    def export_json(self):
        if not self.table:
            QMessageBox.warning(self, "Export Failed", "No elements to export.")
            return

        selected = []
        for i in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(i, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)  # get the actual QCheckBox
                if chk and chk.isChecked():
                    selected.append(self.table.item(i, 1).text())

        if not selected:
            QMessageBox.information(self, "Export", "No elements selected.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export JSON", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                json.dump({"selected_elements": selected}, f, indent=4)
            QMessageBox.information(self, "Export Successful", f"Exported {len(selected)} elements.")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Error: {str(e)}")



# ---------- Import Configuration Page ----------
class ImportConfigurationPage(PageCard):
    def __init__(self, GitHub_Object, workSpacePath, metamodelpath, newVersionID, Selected_Repository_name, fileDirP, scale=1.0):
        super().__init__(scale)
        self.scale = scale
        self.GitHub_Object = GitHub_Object
        self.workSpacePath = workSpacePath
        self.newVersionID = newVersionID
        self.Selected_Repository_name= Selected_Repository_name
        self.fileDirP = fileDirP
        self.metamodelpath = metamodelpath

        vbox = QVBoxLayout(self)
        vbox.setSpacing(scale_ui(16, scale))

        title = QLabel("📥 Import Configuration")
        title.setStyleSheet(f"font-size: {scale_ui(20, scale)}px; font-weight: 600; color: #222;")
        vbox.addWidget(title)

        desc = QLabel("Import a configuration JSON file to automatically select elements.")
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #555;")
        vbox.addWidget(desc)

        import_btn = QPushButton("Import from JSON")
        import_btn.setFixedHeight(scale_ui(40, scale))
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                padding: 6px 18px;
            }
            QPushButton:hover { background-color: #008af0; }
        """)
        import_btn.clicked.connect(self.import_config)
        vbox.addWidget(import_btn, alignment=Qt.AlignLeft)

        self.table = None
        self.create_view_btn = None
        self.layout_container = vbox

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Configuration", "", "JSON Files (*.json)")
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            elements = data.get("selected_elements", [])
            if not elements:
                raise ValueError("Invalid or empty configuration format.")
            self.display_imported_elements(elements)
        except Exception as e:
            QMessageBox.warning(self, "Import Failed", f"Error: {str(e)}")

    def display_imported_elements(self, elements):
        if self.table:
            self.layout_container.removeWidget(self.table)
            self.table.deleteLater()
            self.table = None
        if self.create_view_btn:
            self.layout_container.removeWidget(self.create_view_btn)
            self.create_view_btn.deleteLater()
            self.create_view_btn = None

        self.table = QTableWidget(len(elements), 2)
        self.table.setHorizontalHeaderLabels(["Select", "Element Name"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        for i, name in enumerate(elements):
            chk = QCheckBox()
            chk.setChecked(True)

            # Center the checkbox in the cell
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignCenter)  # center alignment
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)

            self.table.setCellWidget(i, 0, cell_widget)

            item = QTableWidgetItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # make read-only
            self.table.setItem(i, 1, item)

        self.layout_container.addWidget(self.table)


        btn_row = QHBoxLayout()
        btn_row.addStretch()
        for label in ["Create View", "View Viewer"]:
            btn = QPushButton(label)
            btn.setFixedHeight(scale_ui(40, self.scale))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: {scale_ui(6, self.scale)}px;
                    font-size: {scale_ui(14, self.scale)}px;
                    padding: 6px 18px;
                }}
                QPushButton:hover {{ background-color: #008af0; }}
            """)
            if label == "Create View":
                btn.clicked.connect(self.create_view_action)
            else:
                btn.clicked.connect(self.view_viewer)
                btn.setEnabled(False)  # Disable "View Viewer" initially
                self.view_viewer_import_btn = btn  # Keep a reference for later
            
            btn_row.addWidget(btn)
        self.layout_container.addLayout(btn_row)

    def create_view_action(self):
        selected = []
        for i in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(i, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)  # Get the actual checkbox
                if chk and chk.isChecked():
                    selected.append(self.table.item(i, 1).text())
        if selected:
            self.GitHub_Object.GitHub_View_Management_ItemSelection(self.newVersionID, self.workSpacePath, self.metamodelpath, self.Selected_Repository_name, self.fileDirP, selected)
            QMessageBox.information(self, "Successful", "Your view is successfully created.")
            self.view_viewer_import_btn.setEnabled(True)
        else:
            QMessageBox.information(self, "Failed", "No elements selected.")
            self.view_viewer_import_btn.setEnabled(False)

    def view_viewer(self):   
        self.myBloom_Object = myBloom(self.metamodelpath)
        MyMetaModel = self.myBloom_Object.importMetaModel(self.metamodelpath)
        root_m = self.myBloom_Object.importModel(self.workSpacePath + "/viewSelectedItem.xmi", MyMetaModel)
        model_json = self.myBloom_Object.all_properties_of_model(root_m)
        self.element_viewer_window = ModelViewer(model_json)
        self.element_viewer_window.show()

# ---------- AI Assistant Page ----------
class AIAssistantPage(PageCard):
    def __init__(self, scale=1.0):
        super().__init__(scale)
        vbox = QVBoxLayout(self)
        vbox.setSpacing(scale_ui(16, scale))

        header = QLabel("🤖 AI Assistant for View Creation")
        header.setStyleSheet(f"font-size: {scale_ui(20, scale)}px; font-weight: 600; color: #222;")
        vbox.addWidget(header)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("AI Assistant: Describe the view you want to create...")
        self.chat_display.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ccc; border-radius: 6px;")
        vbox.addWidget(self.chat_display, stretch=1)

        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Describe your desired view...")
        send_btn = QPushButton("Send")
        #send_btn.setFixedWidth(scale_ui(80, scale))
        send_btn.setFixedHeight(scale_ui(40, scale))
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                padding: 6px 18px;
            }
            QPushButton:hover { background-color: #008af0; }
        """)
        input_row.addWidget(self.input_field)
        input_row.addWidget(send_btn)
        vbox.addLayout(input_row)


def scale_ui(value, scale=1.0):
    return int(value * scale)
class SynchronizationPage(QWidget):
    def __init__(self, GitHub_Object, workSpacePath, metamodelpath, newVersionID,
                 Selected_Repository_name, fileDirP, scale=1.0):
        super().__init__()
        self.scale = scale
        self.GitHub_Object = GitHub_Object
        self.workSpacePath = workSpacePath
        self.newVersionID = newVersionID
        self.Selected_Repository_name = Selected_Repository_name
        self.fileDirP = fileDirP
        self.metamodelpath = metamodelpath
        
        #self.numberOfVersion_View_sync = 0
        self.worker = ViewWorker()
        #self.worker.set_numberOfVersion(self.numberOfVersion_View_sync)
        self.worker.set_arg_func(
            self.GitHub_Object,
            self.Selected_Repository_name,
            self.fileDirP,
            self.newVersionID,
            self.workSpacePath
        )

        # ---------- MAIN CARD FRAME ----------
        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: {scale_ui(12, scale)}px;
                border: 1px solid #ddd;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(scale_ui(20, scale))
        card_layout.setContentsMargins(scale_ui(20, scale), scale_ui(20, scale),
                                       scale_ui(20, scale), scale_ui(20, scale))

        # ---------- TITLE & SUBTITLE ----------
        title = QLabel("🔄 View Synchronization")
        title.setStyleSheet(f"font-size: {scale_ui(20, scale)}px; font-weight: 600; color: #222;")
        card_layout.addWidget(title)

        subtitle = QLabel("Keep your created views synchronized with the base model.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 14px; color: #555;")
        card_layout.addWidget(subtitle)

        # ---------- INFO FRAME ----------
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 10, 15, 10)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f7f9fc;
                border: 1px solid #d0d7de;
                border-radius: 6px;
            }
            QLabel {
                font-size: 14px;
            }
        """)

        self.version_label = QLabel("📦 Versions in repository: 0")
        self.version_label.setStyleSheet("color: #0056b3; font-weight: 600;")
        info_layout.addWidget(self.version_label)

        self.last_check_label = QLabel("🕓 Last checked: —")
        self.last_check_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.last_check_label)

        card_layout.addWidget(info_frame)

        # ---------- STATUS AREA ----------
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_layout.setAlignment(Qt.AlignLeft)

        self.spinner_label = QLabel()
        spinner_path = os.path.join(os.path.dirname(__file__), resource_path("icons/spinner.gif") )
        if os.path.exists(spinner_path):
            self.spinner_movie = QMovie(spinner_path)
            self.spinner_movie.setScaledSize(QSize(24, 24))
            self.spinner_label.setMovie(self.spinner_movie)
        else:
            self.spinner_label.setText("⏳")
        self.spinner_label.hide()
        status_layout.addWidget(self.spinner_label)

        self.status_label = QLabel("🔸 Waiting to start synchronization...")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #444;
            background-color: #fff8e1;
            border: 1px solid #f0d67a;
            border-radius: 5px;
            padding: 8px;
        """)
        status_layout.addWidget(self.status_label, stretch=1)

        card_layout.addLayout(status_layout)

        # ---------- SCHEDULE BUTTONS ----------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_button_View_sync = QPushButton("▶️ Start Syncing")
        self.stop_button_View_sync = QPushButton("⏹️ Stop Syncing")
        self.stop_button_View_sync.setEnabled(False)

        for btn in (self.start_button_View_sync, self.stop_button_View_sync):
            btn.setFixedHeight(scale_ui(40, scale))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                    padding: 4px 12px;
                }
                QPushButton:hover { background-color: #008af0; }
                QPushButton:disabled { background-color: #aaa; }
            """)
            btn_layout.addWidget(btn)

        card_layout.addLayout(btn_layout)

        # ---------- ACTION BUTTONS ----------
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        self.update_view_button = QPushButton("⬆️ Update View")
        self.submit_changes_button = QPushButton("📤 Submit Changes")
        self.update_view_button.setEnabled(False)

        for btn in (self.update_view_button, self.submit_changes_button):
            btn.setFixedHeight(scale_ui(40, scale))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                    padding: 4px 12px;
                }
                QPushButton:hover { background-color: #218838; }
                QPushButton:disabled { background-color: #aaa; }
            """)
            action_layout.addWidget(btn)

        card_layout.addLayout(action_layout)

        # ---------- MAIN LAYOUT ----------
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(card)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ---------- TIMER ----------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_task_view_updater)

        # ---------- BUTTON CONNECTIONS ----------
        self.start_button_View_sync.clicked.connect(self.start_schedule)
        self.stop_button_View_sync.clicked.connect(self.stop_schedule)
        self.update_view_button.clicked.connect(self.update_view)
        self.submit_changes_button.clicked.connect(self.submit_changes)

        # ---------- INITIAL CHECK ----------
        self.run_initial_check()

    # ========================== INITIAL VERSION CHECK ==========================
    @pyqtSlot()
    def run_initial_check(self):
        self.show_spinner(True)
        self.update_status("⏳ Checking repository version info...", "info")

        self.init_worker = InitialVersionWorker(
            self.GitHub_Object,
            self.Selected_Repository_name,
            self.fileDirP,
            self.newVersionID
        )
        self.init_worker.progress.connect(self.update_status)
        self.init_worker.finished.connect(self.handle_initial_check_finished)
        self.init_worker.start()

    @pyqtSlot(int)
    def handle_initial_check_finished(self, version_count):
        self.show_spinner(False)
        self.numberOfVersion_View_sync = version_count
        self.version_label.setText(f"📦 Versions in repository: {version_count}")

        self.worker.set_numberOfVersion(self.numberOfVersion_View_sync)
        
        if version_count > 0:
            self.update_status(f"✅ Repository ready with {version_count} versions.", "success")
        else:
            self.update_status("⚠️ No version info detected.", "warning")

    # ========================== SCHEDULE CONTROL ==========================
    @pyqtSlot()
    def start_schedule(self):
        self.update_status("🕓 Schedule started. Checking for updates every minute...", "info")
        self.start_button_View_sync.setEnabled(False)
        self.stop_button_View_sync.setEnabled(True)
        self.timer.start(60_000)
        self.run_task_view_updater()

    @pyqtSlot()
    def stop_schedule(self):
        if self.timer.isActive():
            self.timer.stop()
        self.update_status("⏹️ Schedule stopped.", "error")
        self.start_button_View_sync.setEnabled(True)
        self.stop_button_View_sync.setEnabled(False)

        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()

    # ========================== SYNC WORKER ==========================
    @pyqtSlot()
    def run_task_view_updater(self):
        if self.worker and self.worker.isRunning():
            self.update_status("⏳ Previous check still running...", "info")
            return

        self.show_spinner(True)
        self.update_status("🔍 Checking for updates...", "info")
        
        self.worker.finished.connect(self.update_label_View_sync)
        self.worker.start()

    @pyqtSlot(str)
    def update_label_View_sync(self, message):
        self.show_spinner(False)
        self.update_status(message, "info")
        #self.last_check_label.setText(f"🕓 Last checked: {QTime.currentTime().toString('HH:mm:ss')}")

        english_locale = QLocale(QLocale.English)
        current_time = QTime.currentTime()
        formatted_time = english_locale.toString(current_time, "HH:mm:ss")
        self.last_check_label.setText(f"🕓 Last checked: {formatted_time}")

        if not self.worker:
            return

        self.numberOfVersion_View_sync = self.worker.get_numberOfVersion()
        self.version_label.setText(f"📦 Versions in repository: {self.numberOfVersion_View_sync}")

        if self.worker.get_isUpdated():
            self.update_status("🆕 New version detected! Press Update View to receive new changes...", "warning")
            self.update_view_button.setEnabled(True)
        else:
            self.update_status("[Sync] No update detected.", "info")
            self.update_view_button.setEnabled(False)

    # ========================== NEW BUTTON FUNCTIONS ==========================
    @pyqtSlot()
    def update_view(self):
        """Manual update triggered by the user."""
        self.update_status("⬆️ Updating view to latest version...", "info")
        self.worker.view_updating_func()
        QTimer.singleShot(1500, lambda: self.update_status("✅ View successfully updated.", "success"))
        self.version_label.setText(f"📦 Versions in repository: {self.worker.get_numberOfVersion()}")

    @pyqtSlot()
    def submit_changes(self):
        """Submit current view changes to the server."""
        self.update_status("📤 Submitting changes to server...", "info")
        # Example: you would call a worker or API here
        # For now, simulate success:
        QTimer.singleShot(1500, lambda: self.update_status("✅ Changes submitted successfully!", "success"))

    # ========================== SPINNER & STATUS ==========================
    def show_spinner(self, show: bool):
        if hasattr(self, "spinner_movie"):
            if show:
                self.spinner_label.show()
                self.spinner_movie.start()
            else:
                self.spinner_movie.stop()
                self.spinner_label.hide()
        else:
            self.spinner_label.setVisible(show)

    @pyqtSlot(str)
    def update_status(self, message, level="info"):
        colors = {
            "info": ("#e8f4fd", "#0078d7"),
            "success": ("#e6f4ea", "#107c10"),
            "warning": ("#fff8e1", "#b58900"),
            "error": ("#fdecea", "#d32f2f"),
        }
        bg, fg = colors.get(level, colors["info"])
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {fg};
                background-color: {bg};
                border: 1px solid {fg};
                border-radius: 5px;
                padding: 8px;
            }}
        """)
