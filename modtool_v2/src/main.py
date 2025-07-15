import sys
from PyQt5.QtWidgets import QApplication
from config import Config
from mod_manager import ModManager
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    config = Config('config.txt')
    mod_manager = ModManager(config)
    window = MainWindow(config, mod_manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()