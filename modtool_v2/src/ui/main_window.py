from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from ui.mod_list_view import ModListView

class MainWindow(QMainWindow):
    def __init__(self, config, mod_manager):
        super().__init__()
        self.config = config
        self.mod_manager = mod_manager
        self.setWindowTitle(f"{self.config.game_name} mod工具v2")
        self.resize(900, 600)
        self.init_menu()
        self.mod_list_view = ModListView(self.mod_manager)
        self.setCentralWidget(self.mod_list_view)

    def init_menu(self):
        menubar = self.menuBar()
        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.on_refresh)
        menubar.addAction(refresh_action)

        save_action = QAction('保存清单', self)
        save_action.triggered.connect(self.on_save)
        menubar.addAction(save_action)

        load_action = QAction('加载清单', self)
        load_action.triggered.connect(self.on_load)
        menubar.addAction(load_action)

    def on_refresh(self):
        self.mod_manager.scan_mods()
        self.mod_list_view.populate_mod_list()

    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存清单", ".", "Text Files (*.txt)")
        if path:
            self.mod_manager.save_active_mods(path)
            # with open(path, 'w', encoding='utf-8') as f:
            #     for mod in self.mod_manager.mod_list:
            #         if mod.is_activated:
            #             f.write(mod.name + '\n')
            QMessageBox.information(self, "保存成功", "激活mod清单已保存。")

    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(self, "加载清单", ".", "Text Files (*.txt)")
        if path:
            with open(path, encoding='utf-8') as f:
                active_mods = set(line.strip() for line in f if line.strip())

            def update_mods(mod):
                is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
                if is_instance:
                    if mod.fullname in active_mods and not mod.is_activated:
                        self.mod_manager.activate_mod(mod)
                    elif mod.fullname not in active_mods and mod.is_activated:
                        self.mod_manager.deactivate_mod(mod)
                for child in getattr(mod, 'children', []):
                    update_mods(child)

            for mod in self.mod_manager.mod_list:
                update_mods(mod)

            # 重新扫描和刷新界面
            self.mod_manager.scan_mods()
            self.mod_list_view.populate_mod_list()
            QMessageBox.information(self, "加载成功", "激活mod清单已加载。")