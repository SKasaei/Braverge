import time
import json
import shutil
import os
from PyQt5.QtCore import QThread, pyqtSignal, QTime





# ==============================================================
# 🌱 Lightweight worker for initial version count
# ==============================================================
class InitialVersionWorker(QThread):
    """Runs the initial version check without blocking the UI."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)  # emits the number of versions found

    def __init__(self, GitHub_Object, repo_name, dir_item, branch_id):
        super().__init__()
        self.GitHub_Object = GitHub_Object
        self.repo_name = repo_name
        self.dir_item = dir_item
        self.branch_id = branch_id
        self.Selected_Version_ID = branch_id

    def run(self):
        try:
            self.progress.emit("🔎 Fetching initial branch info...")
            repo_contents = self.GitHub_Object.getRepos_contents(
                self.repo_name, self.dir_item
            )

            branch_info = None
            for item in repo_contents:
                if "Branch_Info" in item.name:
                    branch_info = json.loads(item.decoded_content)
                    if self.branch_id in branch_info.get("Versions_ID", []):
                        break
                    else:
                        branch_info = None

            if not branch_info:
                self.progress.emit("⚠️ No Branch_Info file found.")
                self.finished.emit(0)
                return

            version_count = len(branch_info.get("Versions_ID", []))
            self.progress.emit(f"✅ Found {version_count} existing versions.")
            self.finished.emit(version_count)

        except Exception as e:
            self.progress.emit(f"❌ Error reading branch info: {e}")
            self.finished.emit(0)


# ==============================================================
# ⚙️ ViewWorker — Handles synchronization & merging
# ==============================================================
class ViewWorker(QThread):
    """Background worker to synchronize and update views with a GitHub repository."""

    finished = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.GitHub_Object = None
        self.Selected_Repository_name = ""
        self.Selected_Dir_tree_view_selected_item = ""
        self.branch_id = ""
        self.Selected_Version_ID = ""
        self.numberOfVersion = 0
        self.workSpacePath = ""
        self.isUpdated = False

    # --- Getters / Setters ---
    def set_numberOfVersion(self, n: int):
        self.numberOfVersion = n

    def get_numberOfVersion(self) -> int:
        return self.numberOfVersion

    def get_isUpdated(self) -> bool:
        return self.isUpdated

    def set_arg_func(self, GitHub, Selected_Repo, Selected_Dir, Selected_Branch_ID, workSpace):
        self.GitHub_Object = GitHub
        self.Selected_Repository_name = Selected_Repo
        self.Selected_Dir_tree_view_selected_item = Selected_Dir
        self.Selected_Version_ID = Selected_Branch_ID
        self.branch_id = Selected_Branch_ID
        self.workSpacePath = workSpace

    # --- Main thread run method ---
    def run(self):
        try:
            self.progress.emit("Starting synchronization check...")
            time.sleep(1.0)

            repo_contents = self.GitHub_Object.getRepos_contents(
                self.Selected_Repository_name,
                self.Selected_Dir_tree_view_selected_item
            )

            branch_info = None
            for item in repo_contents:
                if "Branch_Info" in item.name:
                    branch_info = json.loads(item.decoded_content)
                    if self.branch_id in branch_info.get("Versions_ID", []):
                        self.branch_id = branch_info['branch_ID']
                        break
                    else:
                        branch_info = None

            if not branch_info:
                self.progress.emit("⚠️ No Branch_Info file found.")
                self.finished.emit("Synchronization failed — missing Branch_Info.")
                return

            self.versions = branch_info.get("Versions_ID", [])
            if len(self.versions) > self.numberOfVersion:
                self.progress.emit("🆕 New version detected! Press Update button to receive new changes...")
                self.isUpdated = True
                #self.branch_info_Json = branch_info
                #self.view_updating_func(branch_info)
            else:
                self.progress.emit("No new versions detected.")
                self.isUpdated = False

            now = QTime.currentTime().toString("HH:mm:ss")
            self.finished.emit(f"Task executed at {now}")

        except Exception as e:
            self.progress.emit(f"❌ Error during sync: {e}")
            self.finished.emit("Synchronization failed.")

    # --- Update logic ---
    def view_updating_func(self):#, branch_info: dict):
        try:
            #branch_info = self.branch_info_Json
            #self.isUpdated = True
            self.set_numberOfVersion(len(self.versions))

            file_name = f"{self.branch_id}.xmi"
            
            ### base version
            src= self.workSpacePath + "/" + file_name
            dst= str(self.workSpacePath + "/" + file_name).replace(file_name,'Base.xmi')
            #os.replace(src, dst)
            shutil.copy(src, dst)

            # Step 1: Download new model
            self.progress.emit("⬇️ Downloading latest model...")
            self.GitHub_Object.downloadFile_fromGitHub(
                self.workSpacePath + '/',
                '/' + file_name,
                self.Selected_Repository_name,
                self.Selected_Dir_tree_view_selected_item,
                'Right.xmi'
            )

            # Step 2: Replace files
            src = self.workSpacePath + "/viewSelectedItem.xmi"
            dst = self.workSpacePath + "/Left.xmi"
            if os.path.exists(src):
                os.replace(src, dst)
            else:
                self.progress.emit(f"⚠️ Source file missing: {src}")

            # Step 3: Merge models
            self.progress.emit("🔧 Merging models...")
            self.GitHub_Object.GitHub_Merge_Models(
                self.workSpacePath + "/",
                self.GitHub_Object.getMETAMODEL_PATH_FILE()
            )

            # Step 4: Copy result back
            src = os.path.join(self.workSpacePath, "Target.xmi")
            dst = os.path.join(self.workSpacePath, "viewSelectedItem.xmi")
            if os.path.exists(src):
                shutil.copy(src, dst)
                self.progress.emit("✅ View successfully updated.")
            else:
                self.progress.emit("⚠️ Merge output missing — update incomplete.")

            self.isUpdated = False

        except Exception as e:
            self.isUpdated = True
            self.progress.emit(f"❌ Update failed: {e}")