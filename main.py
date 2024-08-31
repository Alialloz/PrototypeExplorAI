import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QVBoxLayout, QWidget, 
                             QMessageBox, QCheckBox, QSpinBox, QProgressBar, 
                             QMenuBar, QAction, QStatusBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QIcon

class FileSearchThread(QThread):
    file_found_signal = pyqtSignal(str)
    search_complete_signal = pyqtSignal(bool)

    def __init__(self, rootDir, fileName, fileFormat, minSize, maxSize, looseMatch):
        super().__init__()
        self.rootDir = rootDir
        self.fileName = fileName
        self.fileFormat = fileFormat
        self.minSize = minSize
        self.maxSize = maxSize
        self.looseMatch = looseMatch
        self._is_running = True

    def run(self):
        files_found = False
        for root, dirs, files in os.walk(self.rootDir):
            if not self._is_running:
                break
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    continue  # Skip inaccessible files

                # Check if the file name matches the criteria
                if self.fileFormat:
                    # If a format is specified, the file name must end with that format
                    if not file.lower().endswith(self.fileFormat.lower()):
                        continue

                file_name_without_extension = os.path.splitext(file)[0]
                if ((self.looseMatch and self.fileName.lower() in file_name_without_extension.lower()) or 
                    (file_name_without_extension.lower() == self.fileName.lower())) and \
                    (self.minSize <= file_size <= self.maxSize):
                    self.file_found_signal.emit(file_path)
                    files_found = True

        self.search_complete_signal.emit(files_found)

    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExplorAI - Votre assistant de recherche intelligent")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('path/to/icon.png'))  # Assurez-vous que le chemin est correct
        self.current_theme = 'light'
        self.initUI()
        self.found_files = []

    def initUI(self):
        self.setStyleSheet(self.light_theme_stylesheet())

        self.createMenuBar()
        self.createStatusBar()

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.labelTitle = QLabel("Trouvez vos fichiers rapidement avec ExplorAI")
        self.labelTitle.setAlignment(Qt.AlignCenter)
        self.labelTitle.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(self.labelTitle)

        self.addSeparator()

        self.lineEditFileName = QLineEdit(self)
        self.layout.addWidget(QLabel("Nom du fichier :", self.centralWidget))
        self.layout.addWidget(self.lineEditFileName)

        self.checkBoxLooseMatch = QCheckBox("Recherche non stricte du nom", self)
        self.layout.addWidget(self.checkBoxLooseMatch)

        self.addSeparator()

        self.comboBoxFileFormat = QComboBox(self)
        self.comboBoxFileFormat.addItem("")  # Item vide pour format optionnel
        self.comboBoxFileFormat.addItems(['.png', '.jpg', '.txt', '.pdf'])
        self.layout.addWidget(QLabel("Format du fichier (optionnel) :", self.centralWidget))
        self.layout.addWidget(self.comboBoxFileFormat)

        self.addSeparator()

        self.spinBoxMinSize = QSpinBox(self)
        self.spinBoxMinSize.setMaximum(1000000)
        self.layout.addWidget(QLabel("Taille minimale du fichier (Ko) :", self.centralWidget))
        self.layout.addWidget(self.spinBoxMinSize)

        self.spinBoxMaxSize = QSpinBox(self)
        self.spinBoxMaxSize.setMaximum(1000000)
        self.spinBoxMaxSize.setValue(1000000)
        self.layout.addWidget(QLabel("Taille maximale du fichier (Ko) :", self.centralWidget))
        self.layout.addWidget(self.spinBoxMaxSize)

        self.addSeparator()

        self.pushButtonSearch = QPushButton("Chercher", self)
        self.pushButtonSearch.setStyleSheet("margin-top: 15px; padding: 10px; font-size: 16px;")
        self.pushButtonSearch.clicked.connect(self.startSearch)
        self.layout.addWidget(self.pushButtonSearch)

        self.progressBar = QProgressBar(self)
        self.progressBar.setStyleSheet("margin-top: 20px; height: 20px;")
        self.layout.addWidget(self.progressBar)
        self.progressBar.setVisible(False)

        self.addSeparator()

        self.resultTable = QTableWidget(self)
        self.resultTable.setColumnCount(1)
        self.resultTable.setHorizontalHeaderLabels(["Chemin des fichiers"])
        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.resultTable)

        self.layout.addStretch()  # Add stretch to push everything up and leave some space at the bottom

        self.animateWidgets()

    def createMenuBar(self):
        menuBar = QMenuBar(self)
        menuBar.setStyleSheet("""
            QMenuBar {
                background-color: #34495e;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: #34495e;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #2980b9;
            }
            QMenu {
                background-color: #34495e;
                color: white;
            }
            QMenu::item:selected {
                background-color: #2980b9;
            }
        """)
        self.setMenuBar(menuBar)

        themeMenu = menuBar.addMenu("Thème")

        self.switchThemeAction = QAction("Basculer vers le thème sombre", self)
        self.switchThemeAction.triggered.connect(self.switchTheme)
        themeMenu.addAction(self.switchThemeAction)

    def createStatusBar(self):
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt")

    def light_theme_stylesheet(self):
        return """
            QWidget {
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                background-color: #f0f2f5;
            }
            QLabel {
                color: #34495e;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLineEdit, QComboBox, QCheckBox, QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                font-size: 15px;
            }
            QLineEdit:focus, QComboBox:focus, QCheckBox:focus, QSpinBox:focus {
                border: 1px solid #3498db;
                outline: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5f8a;
            }
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-size: 15px;
                color: white;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                font-size: 15px;
            }
        """

    def dark_theme_stylesheet(self):
        return """
            QWidget {
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLineEdit, QComboBox, QCheckBox, QSpinBox {
                border: 1px solid #95a5a6;
                border-radius: 8px;
                padding: 10px;
                background-color: #34495e;
                color: #ecf0f1;
                font-size: 15px;
            }
            QLineEdit:focus, QComboBox:focus, QCheckBox:focus, QSpinBox:focus {
                border: 1px solid #1abc9c;
                outline: none;
            }
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #12876f;
            }
            QProgressBar {
                border: 1px solid #95a5a6;
                border-radius: 8px;
                text-align: center;
                font-size: 15px;
                color: white;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #1abc9c;
                width: 20px;
            }
            QTableWidget {
                background-color: #34495e;
                border: 1px solid #95a5a6;
                border-radius: 8px;
                font-size: 15px;
                color: #ecf0f1;
            }
        """

    def addSeparator(self):
        separator = QFrame(self)
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

    def animateWidgets(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget:
                animation = QPropertyAnimation(widget, b"geometry")
                animation.setDuration(500)
                animation.setStartValue(QRect(widget.x(), widget.y() - 50, widget.width(), widget.height()))
                animation.setEndValue(QRect(widget.x(), widget.y(), widget.width(), widget.height()))
                animation.setEasingCurve(QEasingCurve.OutBounce)
                animation.start(QPropertyAnimation.DeleteWhenStopped)

    def startSearch(self):
        self.disableInputs(True)
        self.statusBar.showMessage("Recherche en cours...")
        self.found_files.clear()
        self.resultTable.setRowCount(0)  # Clear the table
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)  # Indeterminate state
        self.lineEditFileName.setStyleSheet("")  # Reset border color

        fileName = self.lineEditFileName.text()
        fileFormat = self.comboBoxFileFormat.currentText() if self.comboBoxFileFormat.currentText() != "" else None
        minSize = self.spinBoxMinSize.value() * 1024
        maxSize = self.spinBoxMaxSize.value() * 1024
        looseMatch = self.checkBoxLooseMatch.isChecked()
        rootDir = '/'  # Adjust this to your system if needed

        self.search_thread = FileSearchThread(rootDir, fileName, fileFormat, minSize, maxSize, looseMatch)
        self.search_thread.file_found_signal.connect(self.fileFound)
        self.search_thread.search_complete_signal.connect(self.searchComplete)
        self.search_thread.start()

    def disableInputs(self, disable):
        self.lineEditFileName.setDisabled(disable)
        self.comboBoxFileFormat.setDisabled(disable)
        self.spinBoxMinSize.setDisabled(disable)
        self.spinBoxMaxSize.setDisabled(disable)
        self.checkBoxLooseMatch.setDisabled(disable)
        self.pushButtonSearch.setDisabled(disable)

    def fileFound(self, filePath):
        self.found_files.append(filePath)
        row_position = self.resultTable.rowCount()
        self.resultTable.insertRow(row_position)
        self.resultTable.setItem(row_position, 0, QTableWidgetItem(filePath))

    def searchComplete(self, files_found):
        self.progressBar.setVisible(False)
        self.disableInputs(False)
        if not self.found_files:
            self.lineEditFileName.setStyleSheet("border: 2px solid red;")
            QMessageBox.warning(self, "Aucun Résultat", "Fichier non trouvé. Veuillez vérifier le nom et réessayer.")
            self.statusBar.showMessage("Recherche terminée : aucun fichier trouvé")
        else:
            self.statusBar.showMessage("Recherche terminée : fichiers trouvés")

    def switchTheme(self):
        if self.current_theme == 'light':
            self.setStyleSheet(self.dark_theme_stylesheet())
            self.switchThemeAction.setText("Basculer vers le thème clair")
            self.current_theme = 'dark'
        else:
            self.setStyleSheet(self.light_theme_stylesheet())
            self.switchThemeAction.setText("Basculer vers le thème sombre")
            self.current_theme = 'light'

    def closeEvent(self, event):
        if hasattr(self, 'search_thread') and self.search_thread.isRunning():
            self.search_thread.stop()
            self.search_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
