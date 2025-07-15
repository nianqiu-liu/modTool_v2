from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QCheckBox, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import functools

def create_name_widget(mod, display_name):
    widget = QWidget()
    hbox = QHBoxLayout(widget)
    hbox.setContentsMargins(0,0,0,0)
    select_checkbox = QCheckBox()
    select_checkbox.setChecked(mod.is_selected)
    hbox.addWidget(select_checkbox)
    hbox.addSpacing(8)
    name_label = QLabel(display_name)
    hbox.addWidget(name_label)
    hbox.addStretch()
    widget.setLayout(hbox)
    return widget

class PreviewLabel(QLabel):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path

    def mousePressEvent(self, event):
        pixmap = QPixmap(self.img_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(640, Qt.SmoothTransformation)
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
        self.tree_widget.setHeaderLabels(['Mod Name', 'Tag', 'Activated', 'Preview'])
        layout.addWidget(self.tree_widget)
        self.info_label = QLabel("Select a mod to see details.")
        layout.addWidget(self.info_label)
        self.setLayout(layout)
        self.populate_mod_list()
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)

    def populate_mod_list(self):
        expanded = self.get_expanded_items()
        vpos = self.tree_widget.verticalScrollBar().value()
        hpos = self.tree_widget.horizontalScrollBar().value()

        self.tree_widget.clear()
        self.mod_manager.mod_list.sort(key=lambda m: m.name)

        def add_moditem_to_tree(mod, parent_item=None):
            # 判断tag是否可见（只对实例条目判断）
            is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
            if is_instance and mod.tag:
                if not self.mod_manager.config.is_tag_visible(mod.tag):
                    return  # 跳过不可见tag的mod

            item = QTreeWidgetItem(['', '', '', ''])
            name_widget = create_name_widget(mod, mod.name)
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

            for child in getattr(mod, 'children', []):
                add_moditem_to_tree(child, item)

        for mod in self.mod_manager.mod_list:
            add_moditem_to_tree(mod)

        self.set_expanded_items(expanded)
        QTimer.singleShot(0, lambda: self.tree_widget.verticalScrollBar().setValue(vpos))
        QTimer.singleShot(0, lambda: self.tree_widget.horizontalScrollBar().setValue(hpos))

    def on_selection_changed(self):
        items = self.tree_widget.selectedItems()
        if items:
            item = items[0]
            self.info_label.setText(f"Mod: {item.text(0)}, Tag: {item.text(1)}")
        else:
            self.info_label.setText("Select a mod to see details.")

    def clear_selection(self):
        self.tree_widget.clearSelection()

    def on_activated_changed(self, state, mod):
        if state == Qt.Checked:
            self.mod_manager.activate_mod(mod)
        else:
            self.mod_manager.deactivate_mod(mod)
        mod.is_activated = (state == Qt.Checked)
        # 刷新树，恢复展开状态
        self.populate_mod_list()