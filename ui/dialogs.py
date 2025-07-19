from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QPushButton, QLabel

class SaveDialog(QDialog):
    def __init__(self, parent=None):
        super(SaveDialog, self).__init__(parent)
        self.setWindowTitle("Save Mod List")
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Choose a location to save the mod list:")
        self.layout.addWidget(self.label)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            # Logic to save the mod list goes here
            pass

class LoadDialog(QDialog):
    def __init__(self, parent=None):
        super(LoadDialog, self).__init__(parent)
        self.setWindowTitle("Load Mod List")
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Choose a mod list to load:")
        self.layout.addWidget(self.label)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.setLayout(self.layout)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            # Logic to load the mod list goes here
            pass