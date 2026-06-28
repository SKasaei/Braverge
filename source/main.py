##
#
#Braverge Toolkit
#Version: 0.1.4
#Author: @smskasaei
#
##
from PyQt5.QtCore import Qt
import sys , os
from  PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
from UI.Braverge_Login_ui import MainWindow

def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', os.getcwd())
        return os.path.join(base_path, relative_path)

def main():
    # Enable automatic high-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path('UI/icons/app.ico')))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    # Detect screen DPI for scaling
    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    scale_factor = dpi / 144  # 96 DPI is default baseline

    window = MainWindow(scale_factor)
    window.setWindowTitle("Braverge - Login Page")
    window.resize(int(400 * scale_factor), int(300 * scale_factor))
    window.center_on_screen()  # <-- Center the window
    window.show()
    sys.exit(app.exec_())
    
if __name__=='__main__':
    main()