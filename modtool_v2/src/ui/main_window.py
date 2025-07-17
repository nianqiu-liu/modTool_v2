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
        self.mod_list_view = ModListView(self.mod_manager)
        self.setCentralWidget(self.mod_list_view)
        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()

        #文件菜单
        file_menu = menubar.addMenu('文件')

        save_action = QAction('保存清单', self)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)

        load_action = QAction('加载清单', self)
        load_action.triggered.connect(self.on_load)
        file_menu.addAction(load_action)

        #条目菜单
        item_menu = menubar.addMenu('条目')

        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.on_refresh)
        item_menu.addAction(refresh_action)

        unselect_all_action = QAction('取消选中', self)
        unselect_all_action.triggered.connect(self.mod_list_view.unselect_all_mods)
        item_menu.addAction(unselect_all_action)

        delete_selected_action = QAction('删除选中', self)
        delete_selected_action.triggered.connect(self.mod_list_view.delete_selected_mods)
        item_menu.addAction(delete_selected_action)

        display_activated_action = QAction('显示已激活', self, checkable=True)
        display_activated_action.setChecked(self.mod_list_view._show_activated_only)
        display_activated_action.triggered.connect(self.mod_list_view.toggle_display_activated)
        item_menu.addAction(display_activated_action)

        display_all_tags_action = QAction('显示全部标签', self, checkable=True)
        display_all_tags_action.setChecked(self.mod_list_view._show_all_tags)
        display_all_tags_action.triggered.connect(self.mod_list_view.toggle_display_all_tags)
        item_menu.addAction(display_all_tags_action)

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