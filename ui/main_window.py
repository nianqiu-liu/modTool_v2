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

        # 文件菜单
        file_menu = menubar.addMenu('文件')
        save_action = QAction('保存清单', self)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        load_action = QAction('加载清单', self)
        load_action.triggered.connect(self.on_load)
        file_menu.addAction(load_action)

        # 条目菜单
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
        expand_all_action = QAction('展开所有层级', self, checkable=True)
        expand_all_action.setChecked(False)
        expand_all_action.toggled.connect(lambda checked: self.mod_list_view.toggle_expand_all(checked))
        item_menu.addAction(expand_all_action)

        # 标签显示子菜单
        tag_menu = item_menu.addMenu('标签显示')

        # 显示全部标签按钮
        display_all_tags_action = QAction('显示全部标签', self, checkable=True)
        display_all_tags_action.setChecked(self.mod_list_view._show_all_tags)
        display_all_tags_action.triggered.connect(self.mod_list_view.toggle_display_all_tags)
        tag_menu.addAction(display_all_tags_action)

        # 动态添加每个标签的切换按钮
        self.tag_actions = {}
        for tag, visible in self.config.tag_list.items():
            tag_action = QAction(tag, self, checkable=True)
            tag_action.setChecked(visible)
            # 绑定事件，切换标签显示状态
            def make_toggle(tag_name):
                def toggle_tag(checked):
                    self.config.tag_list[tag_name] = checked
                    self.mod_list_view.populate_mod_list()
                return toggle_tag
            tag_action.toggled.connect(make_toggle(tag))
            tag_menu.addAction(tag_action)
            self.tag_actions[tag] = tag_action

        # 标签设置子菜单
        set_tag_menu = item_menu.addMenu('标签设置')
        for tag in self.config.tag_list.keys():
            set_tag_action = QAction(tag, self)
            def make_set_tag(tag_name):
                def set_tag():
                    self.set_selected_mods_tag(tag_name)
                return set_tag
            set_tag_action.triggered.connect(make_set_tag(tag))
            set_tag_menu.addAction(set_tag_action)

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

    def set_selected_mods_tag(self, tag_name):
        import os
        # 递归查找所有选中的mod实例条目
        def set_tag_recursive(mod):
            is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
            if is_instance and getattr(mod, 'is_selected', False):
                # 构造新文件夹名
                base_name = mod.fullname.split('[')[0].rstrip()
                new_name = f"{base_name}[{tag_name}]"
                # 获取当前路径
                base_dir = self.mod_manager.config.game_dir if mod.is_activated else self.mod_manager.config.mod_dir
                old_path = os.path.join(base_dir, mod.fullname)
                new_path = os.path.join(base_dir, new_name)
                # 重命名文件夹
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                # 更新mod对象属性
                mod.fullname = new_name
                mod.tag = tag_name
            for child in getattr(mod, 'children', []):
                set_tag_recursive(child)
        for mod in self.mod_manager.mod_list:
            set_tag_recursive(mod)
        self.mod_list_view.populate_mod_list()
