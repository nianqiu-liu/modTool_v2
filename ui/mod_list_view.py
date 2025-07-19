from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QCheckBox, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import functools

def create_name_widget(mod, display_name, parent_view=None):
    widget = QWidget()
    hbox = QHBoxLayout(widget)
    hbox.setContentsMargins(0,0,0,0)
    select_checkbox = QCheckBox()
    select_checkbox.setChecked(mod.is_selected)
    # 绑定事件，点击时更新mod.is_selected并刷新
    if parent_view is not None:
        def on_select_changed(state):
            mod.is_selected = (state == Qt.Checked)
            # 可选：刷新界面（如需立即反映选中状态）
            #parent_view.populate_mod_list()
        select_checkbox.stateChanged.connect(on_select_changed)
    hbox.addWidget(select_checkbox)
    hbox.addSpacing(8)
    name_label = QLabel(display_name)
    hbox.addWidget(name_label)
    hbox.addStretch()
    widget.setLayout(hbox)

        # 实例条目支持点击名称打开所在文件夹
    is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
    if is_instance:
        def open_folder(event):
            import os
            base_dir = parent_view.mod_manager.config.game_dir if mod.is_activated else parent_view.mod_manager.config.mod_dir
            folder_path = os.path.join(base_dir, mod.fullname)
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        name_label.setCursor(Qt.PointingHandCursor)
        name_label.mousePressEvent = open_folder

    return widget

class PreviewLabel(QLabel):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path

    def mousePressEvent(self, event):
        pixmap = QPixmap(self.img_path)
        if not pixmap.isNull():
            if max(pixmap.width(), pixmap.height()) > 800:
                pixmap = pixmap.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            dlg = QDialog()
            dlg.setWindowTitle("预览图")
            vbox = QVBoxLayout(dlg)
            label = QLabel()
            label.setPixmap(pixmap)
            vbox.addWidget(label)
            dlg.setFixedSize(pixmap.size())
            dlg.exec_()  # 使用模态对话框，窗口不会自动关闭

class ModListView(QWidget):
    def __init__(self, mod_manager):
        super().__init__()
        self.mod_manager = mod_manager
        self._show_activated_only = False
        self._filtered_mod_list = []
        self._use_filtered = False
        self._show_all_tags = False  # 新增属性，控制是否显示全部标签
        self.init_ui()

    def get_expanded_items(self):
        expanded = set()
        def recurse(item, path):
            if item.isExpanded():
                expanded.add(tuple(path))
            for i in range(item.childCount()):
                recurse(item.child(i), path + [i])
        for i in range(self.tree_widget.topLevelItemCount()):
            recurse(self.tree_widget.topLevelItem(i), [i])
        return expanded

    def set_expanded_items(self, expanded):
        def recurse(item, path):
            if tuple(path) in expanded:
                item.setExpanded(True)
            for i in range(item.childCount()):
                recurse(item.child(i), path + [i])
        for i in range(self.tree_widget.topLevelItemCount()):
            recurse(self.tree_widget.topLevelItem(i), [i])

    def init_ui(self):
        layout = QVBoxLayout()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['Mod Name', 'Tag', 'enabled', 'Preview'])
        layout.addWidget(self.tree_widget)
        # self.info_label = QLabel("Select a mod to see details.")
        # layout.addWidget(self.info_label)
        self.setLayout(layout)
        self.populate_mod_list()
        #self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)

        # 设置列宽
        self.tree_widget.setColumnWidth(0, 300)  # Mod Name
        self.tree_widget.setColumnWidth(1, 36)   # Tag
        self.tree_widget.setColumnWidth(2, 36)   # Activated
        self.tree_widget.setColumnWidth(3, 200)  # Preview

        # 关键：连接展开/收缩信号
        self.tree_widget.itemExpanded.connect(self.on_item_expand_collapse)
        self.tree_widget.itemCollapsed.connect(self.on_item_expand_collapse)

    def populate_mod_list(self):
        expanded = self.get_expanded_items()
        vpos = self.tree_widget.verticalScrollBar().value()
        hpos = self.tree_widget.horizontalScrollBar().value()

        self.tree_widget.clear()
        self.mod_manager.sort_mods()  # 确保mod_list已排序

        def add_moditem_to_tree(mod, parent_item=None):
            # 判断tag是否可见（只对实例条目判断）
            is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
            if is_instance and mod.tag:
                if (not self.mod_manager.config.is_tag_visible(mod.tag)) and (not self._show_all_tags):
                    return  # 跳过不可见tag的mod

            item = QTreeWidgetItem(['', '', '', ''])
            name_widget = create_name_widget(mod, mod.name, self)
            if parent_item is None:
                self.tree_widget.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
            self.tree_widget.setItemWidget(item, 0, name_widget)

            if is_instance:
                item.setText(1, mod.tag)
                activated_checkbox = QCheckBox()
                activated_checkbox.setChecked(mod.is_activated)
                activated_checkbox.stateChanged.connect(
                    functools.partial(self.on_activated_changed, mod=mod)
                )
                self.tree_widget.setItemWidget(item, 2, activated_checkbox)
                preview_widget = QWidget()
                hbox = QHBoxLayout(preview_widget)
                hbox.setContentsMargins(0,0,0,0)
                preview_paths = self.mod_manager.get_preview_images(mod)
                for img_path in preview_paths[:3]:
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaledToHeight(128, Qt.SmoothTransformation)
                        label = PreviewLabel(img_path)
                        label.setPixmap(pixmap)
                        label.setFixedSize(pixmap.size())
                        hbox.addWidget(label)
                preview_widget.setLayout(hbox)
                self.tree_widget.setItemWidget(item, 3, preview_widget)
            else:
                # 分类条目（如一级分类），如果有激活的实例条目，且当前未展开，则显示其缩略图
                def find_activated_instances(node):
                    result = []
                    is_instance = bool(node.tag or getattr(node, 'fullname', None))
                    if is_instance and getattr(node, 'is_activated', False):
                        result.append(node)
                    for child in getattr(node, 'children', []):
                        result.extend(find_activated_instances(child))
                    return result

                activated_mods = find_activated_instances(mod)
                # 只在未展开时显示缩略图
                if activated_mods and not item.isExpanded():
                    preview_widget = QWidget()
                    hbox = QHBoxLayout(preview_widget)
                    hbox.setContentsMargins(0,0,0,0)
                    # 只显示前3个激活实例的缩略图
                    for activated_mod in activated_mods[:3]:
                        preview_paths = self.mod_manager.get_preview_images(activated_mod)
                        for img_path in preview_paths[:min(3,len(preview_paths))]:
                            pixmap = QPixmap(img_path)
                            if not pixmap.isNull():
                                pixmap = pixmap.scaledToHeight(128, Qt.SmoothTransformation)
                                label = PreviewLabel(img_path)
                                label.setPixmap(pixmap)
                                label.setFixedSize(pixmap.size())
                                hbox.addWidget(label)
                    preview_widget.setLayout(hbox)
                    self.tree_widget.setItemWidget(item, 3, preview_widget)

            for child in getattr(mod, 'children', []):
                add_moditem_to_tree(child, item)

        mod_list = self._filtered_mod_list if getattr(self, '_use_filtered', False) else self.mod_manager.mod_list

        for mod in mod_list:
            add_moditem_to_tree(mod)

        self.set_expanded_items(expanded)
        QTimer.singleShot(0, lambda: self.tree_widget.verticalScrollBar().setValue(vpos))
        QTimer.singleShot(0, lambda: self.tree_widget.horizontalScrollBar().setValue(hpos))

    # def on_selection_changed(self):
    #     items = self.tree_widget.selectedItems()
    #     if items:
    #         item = items[0]
    #         self.info_label.setText(f"Mod: {item.text(0)}, Tag: {item.text(1)}")
    #     else:
    #         self.info_label.setText("Select a mod to see details.")

    def clear_selection(self):
        self.tree_widget.clearSelection()

    def on_activated_changed(self, state, mod):
        if state == Qt.Checked:
            self.mod_manager.activate_mod(mod)  # 只移动文件夹和更新mod.is_activated
        else:
            self.mod_manager.deactivate_mod(mod)
        mod.is_activated = (state == Qt.Checked)

        # 直接更新当前条目的状态，而不刷新整个树形目录
        items = self.tree_widget.findItems(mod.name, Qt.MatchExactly | Qt.MatchRecursive, 0)
        for item in items:
            activated_checkbox = self.tree_widget.itemWidget(item, 2)
            if activated_checkbox:
                activated_checkbox.setChecked(mod.is_activated)

    def unselect_all_mods(self):
        def unselect_recursive(mod):
            mod.is_selected = False
            for child in getattr(mod, 'children', []):
                unselect_recursive(child)
        for mod in self.mod_manager.mod_list:
            unselect_recursive(mod)
        self.populate_mod_list()

    def delete_selected_mods(self):
        def delete_recursive(mod, parent_list):
            if getattr(mod, 'is_selected', False):
                # 删除文件夹
                import shutil, os
                mod_path = os.path.join(
                    self.mod_manager.config.mod_dir if not mod.is_activated else self.mod_manager.config.game_dir,
                    mod.fullname
                )
                if os.path.exists(mod_path):
                    shutil.rmtree(mod_path)
                parent_list.remove(mod)
                return
            for child in list(getattr(mod, 'children', [])):
                delete_recursive(child, mod.children)
        for mod in list(self.mod_manager.mod_list):
            delete_recursive(mod, self.mod_manager.mod_list)
        self.populate_mod_list()  # 不再调用 scan_mods

    def toggle_display_activated(self):
        # 切换只显示激活mod/全部mod
        if not hasattr(self, '_show_activated_only'):
            self._show_activated_only = False
        self._show_activated_only = not self._show_activated_only

        def filter_activated(mod):
            is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
            if is_instance:
                return mod.is_activated
            # 分类条目：只保留有激活子项的分类
            filtered_children = [child for child in getattr(mod, 'children', []) if filter_activated(child)]
            mod.children = filtered_children
            return bool(filtered_children)

        if self._show_activated_only:
            # 只显示激活
            filtered_list = []
            import copy
            for mod in copy.deepcopy(self.mod_manager.mod_list):
                if filter_activated(mod):
                    filtered_list.append(mod)
            self._filtered_mod_list = filtered_list
            self._use_filtered = True
        else:
            self._use_filtered = False

        self.populate_mod_list()

    def toggle_display_all_tags(self):
        # 切换显示全部标签/只显示可见标签
        self._show_all_tags = not self._show_all_tags

        # if self._show_all_tags:
        #     # 显示全部标签
        #     self._use_filtered = False
        # else:
        #     # 只显示可见标签
        #     self._use_filtered = True
        #     self._filtered_mod_list = [mod for mod in self.mod_manager.mod_list if mod.tag and self.mod_manager.config.is_tag_visible(mod.tag)]

        self.populate_mod_list()

    def toggle_expand_all(self, checked):
        if checked:
            # 展开所有
            def expand_all(item):
                item.setExpanded(True)
                for i in range(item.childCount()):
                    expand_all(item.child(i))
            for i in range(self.tree_widget.topLevelItemCount()):
                expand_all(self.tree_widget.topLevelItem(i))
        else:
            # 收缩所有
            def collapse_all(item):
                item.setExpanded(False)
                for i in range(item.childCount()):
                    collapse_all(item.child(i))
            for i in range(self.tree_widget.topLevelItemCount()):
                collapse_all(self.tree_widget.topLevelItem(i))

    def on_item_expand_collapse(self, item):
        # 判断是否为分类条目（没有tag和fullname）
        name_widget = self.tree_widget.itemWidget(item, 0)
        if not name_widget:
            return
        name_label = name_widget.findChild(QLabel)
        if not name_label:
            return
        mod_name = name_label.text()

        # 在mod_list中递归查找对应ModItem
        def find_mod_by_name(mods, name):
            for mod in mods:
                if mod.name == name and not (mod.tag or getattr(mod, 'fullname', None)):
                    return mod
                found = find_mod_by_name(getattr(mod, 'children', []), name)
                if found:
                    return found
            return None

        mod_list = self._filtered_mod_list if getattr(self, '_use_filtered', False) else self.mod_manager.mod_list
        mod = find_mod_by_name(mod_list, mod_name)
        if not mod:
            return

        # 清除原有预览
        self.tree_widget.setItemWidget(item, 3, QWidget())

        # 只有收缩时显示激活实例缩略图
        if not item.isExpanded():
            def find_activated_instances(node):
                result = []
                is_instance = bool(node.tag or getattr(node, 'fullname', None))
                if is_instance and getattr(node, 'is_activated', False):
                    result.append(node)
                for child in getattr(node, 'children', []):
                    result.extend(find_activated_instances(child))
                return result

            activated_mods = find_activated_instances(mod)
            if activated_mods:
                preview_widget = QWidget()
                hbox = QHBoxLayout(preview_widget)
                hbox.setContentsMargins(0,0,0,0)
                for activated_mod in activated_mods[:3]:
                    preview_paths = self.mod_manager.get_preview_images(activated_mod)
                    for img_path in preview_paths[:min(3,len(preview_paths))]:
                        pixmap = QPixmap(img_path)
                        if not pixmap.isNull():
                            pixmap = pixmap.scaledToHeight(128, Qt.SmoothTransformation)
                            label = PreviewLabel(img_path)
                            label.setPixmap(pixmap)
                            label.setFixedSize(pixmap.size())
                            hbox.addWidget(label)
                preview_widget.setLayout(hbox)
                self.tree_widget.setItemWidget(item, 3, preview_widget)