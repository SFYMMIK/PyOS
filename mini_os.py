import os
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QVBoxLayout, QLabel, QPushButton, 
    QWidget, QLineEdit, QInputDialog, QMessageBox, QGridLayout, QTabWidget, QAction, QFileDialog, QTextEdit,
    QTreeView, QFileSystemModel, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QPixmap

import mimetypes

class MiniOS(QMdiArea):
    icon_double_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Add application icons
        self.icons = {
            'calculator': QLabel(self),
            'file_manager': QLabel(self),
            'notepad': QLabel(self),
            'settings': QLabel(self)
            # Add more icons here as needed
        }

        # Position and set icons
        positions = [(50, 50), (100, 50), (150, 50), (200, 50)]  # Add positions for other icons
        icons_files = ['calculator.ico', 'file_manager.ico', 'notepad.ico', 'settings.ico']  # Add filenames for other icons

        for icon, position, icon_file in zip(self.icons.values(), positions, icons_files):
            icon.setPixmap(QIcon(icon_file).pixmap(16, 16))
            icon.setGeometry(position[0], position[1], 16, 16)
            icon.mouseDoubleClickEvent = self.create_icon_double_click_event(icon_file.split('.')[0])

    def create_icon_double_click_event(self, app_name):
        def icon_double_click_event(event):
            if event.button() == Qt.LeftButton:
                self.icon_double_clicked.emit(app_name)
        return icon_double_click_event

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.result_display = QLineEdit(self)
        layout.addWidget(self.result_display)
        
        # Add buttons for the calculator
        grid_layout = QGridLayout()
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        positions = [(i, j) for i in range(4) for j in range(4)]
        
        for position, button in zip(positions, buttons):
            btn = QPushButton(button)
            btn.clicked.connect(self.on_click)
            grid_layout.addWidget(btn, *position)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def on_click(self):
        sender = self.sender()
        text = sender.text()
        if text == '=':
            try:
                result = str(eval(self.result_display.text()))
                self.result_display.setText(result)
            except Exception as e:
                self.result_display.setText("Error")
        else:
            self.result_display.setText(self.result_display.text() + text)

class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(os.getcwd())
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(os.getcwd()))
        layout.addWidget(self.tree_view)

        self.go_to_button = QPushButton("Go to directory")
        self.go_to_button.clicked.connect(self.go_to_directory)
        layout.addWidget(self.go_to_button)

        self.setLayout(layout)

    def go_to_directory(self):
        directory = QInputDialog.getText(self, "Go to directory", "Enter directory path:")
        if directory[1]:
            self.file_system_model.setRootPath(directory[0])
            self.tree_view.setRootIndex(self.file_system_model.index(directory[0]))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction("Open in Notepad", self)
        open_action.triggered.connect(self.open_in_notepad)
        menu.addAction(open_action)
        menu.exec_(event.globalPos())

    def open_in_notepad(self):
        index = self.tree_view.currentIndex()
        file_path = self.file_system_model.filePath(index)
        file_type, _ = mimetypes.guess_type(file_path)
        if file_type is None or file_type.startswith('text/'):
            notepad = Notepad()
            notepad.load_file(file_path)
            sub_window = QMdiSubWindow()
            sub_window.setWidget(notepad)
            sub_window.setWindowTitle("Notepad - " + os.path.basename(file_path))
            sub_window.setGeometry(100, 100, 800, 600)
            sub_window.show()
        else:
            QMessageBox.critical(self, "Error", "Cannot open file: not a text file")

class Notepad(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notepad")
        self.init_ui()
        self.file_path = None

    def init_ui(self):
        layout = QVBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        layout.addWidget(self.save_button)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file)
        layout.addWidget(self.open_button)

        self.text_editor = QTextEdit()
        layout.addWidget(self.text_editor)

        self.setLayout(layout)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_editor.setPlainText(file.read())
            self.file_path = file_path
        except UnicodeDecodeError:
            QMessageBox.critical(self, "Error", "Cannot open file: invalid UTF-8 encoding")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, 'w') as file:
                file.write(self.text_editor.toPlainText())
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text files (*.txt);;All files (*.*)")
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(self.text_editor.toPlainText())
                self.file_path = file_path

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text files (*.txt);;All files (*.*)")
        if file_path:
            self.load_file(file_path)

class SystemSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Settings")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.desktop_tab = QWidget()
        self.sysinfo_tab = QWidget()

        # Desktop Tab
        self.desktop_tab.layout = QVBoxLayout()
        desktop_label = QLabel("Desktop Settings")
        desktop_label.setAlignment(Qt.AlignCenter)
        self.desktop_tab.layout.addWidget(desktop_label)
        self.desktop_tab.setLayout(self.desktop_tab.layout)

        # SysInfo Tab
        self.sysinfo_tab.layout = QVBoxLayout()
        sysinfo_label = QLabel("SysInfo Settings")
        sysinfo_label.setAlignment(Qt.AlignCenter)
        self.sysinfo_tab.layout.addWidget(sysinfo_label)
        sysinfo_logo = QLabel()
        sysinfo_logo.setAlignment(Qt.AlignCenter)
        sysinfo_logo.setPixmap(QPixmap('system_logo.png'))
        self.sysinfo_tab.layout.addWidget(sysinfo_logo)
        sysinfo_text = QLabel("PyOS Ver. (add version here)")
        sysinfo_text.setAlignment(Qt.AlignCenter)
        self.sysinfo_tab.layout.addWidget(sysinfo_text)
        self.sysinfo_tab.setLayout(self.sysinfo_tab.layout)

        # Add tabs to tab widget
        self.tabs.addTab(self.desktop_tab, "Desktop")
        self.tabs.addTab(self.sysinfo_tab, "SysInfo")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

class MiniOSWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Mini OS Simulation')
        self.setGeometry(100, 100, 800, 600)

        self.mdi_area = MiniOS()
        self.setCentralWidget(self.mdi_area)

        self.create_actions()
        self.create_menus()

        self.mdi_area.icon_double_clicked.connect(self.open_application)

    def create_actions(self):
        self.exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(self.close)

    def create_menus(self):
        self.file_menu = self.menuBar().addMenu('&File')
        self.file_menu.addAction(self.exit_action)

    def open_application(self, app_name):
        if app_name == 'calculator':
            self.open_calculator()
        elif app_name == 'file_manager':
            self.open_file_manager()
        elif app_name == 'notepad':
            self.open_notepad()
        elif app_name == 'settings':
            self.open_system_settings()

    def open_calculator(self):
        sub_window = QMdiSubWindow()
        calculator = Calculator()
        sub_window.setWidget(calculator)
        sub_window.setWindowTitle("Calculator")
        sub_window.setGeometry(100, 100, 175, 250)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def open_file_manager(self):
        sub_window = QMdiSubWindow()
        file_manager = FileManager()
        sub_window.setWidget(file_manager)
        sub_window.setWindowTitle("File Manager")
        sub_window.setGeometry(100, 100, 400, 400)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def open_notepad(self):
        sub_window = QMdiSubWindow()
        notepad = Notepad()
        sub_window.setWidget(notepad)
        sub_window.setWindowTitle("Notepad")
        sub_window.setGeometry(100, 100, 150, 300)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def open_system_settings(self):
        sub_window = QMdiSubWindow()
        system_settings = SystemSettings()
        sub_window.setWidget(system_settings)
        sub_window.setWindowTitle("System Settings")
        sub_window.setGeometry(100, 100, 300, 225)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    main_window = MiniOSWindow()
    main_window.show()

    sys.exit(app.exec_())