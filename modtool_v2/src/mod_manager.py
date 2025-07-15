import os
import time
import shutil
from models.mod_item import ModItem


class ModManager:
    def __init__(self, config):
        self.config = config
        self.mod_list = []
        self.scan_mods()

    def scan_mods(self):
        self.mod_list = []
        mod_dirs = [(self.config.mod_dir, False), (self.config.game_dir, True)]
        mods = {}

        # 收集所有mod信息，构建多级树结构
        for dir_path, activated in mod_dirs:
            if not os.path.exists(dir_path):
                continue
            for name in os.listdir(dir_path):
                if not os.path.isdir(os.path.join(dir_path, name)):
                    continue
                tag = ''
                full_name = name
                if '[' in name and ']' in name:
                    tag = name.split('[')[-1].split(']')[0]
                base_name = name.split('[')[0].rstrip()
                levels = [x.strip() for x in base_name.split('-') if x.strip()]
                time_modified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(os.path.join(dir_path, name))))
                # 构建树结构，每层都是ModItem
                current = mods
                for i, level in enumerate(levels):
                    if level not in current:
                        # 分类条目
                        current[level] = {
                            '_moditem': ModItem(
                                name=level,
                                tag='',
                                is_activated=False,
                                time_modified='',
                            ),
                            '_children': {}
                        }
                    if i == 0:
                        # 一级分类条目，设置根条目为自身
                        current[level]['_moditem'].root = current[level]['_moditem']
                        #print(current[level]['_moditem'].root.name)
                    else:
                        # 二级及以上分类条目，设置根条目为上一级分类条目
                        current[level]['_moditem'].root = parent.root
                        #print(current[level]['_moditem'].root.name)
                    if i == len(levels) - 1:
                        # 实例条目，覆盖分类条目的属性
                        current[level]['_moditem'].fullname = full_name
                        current[level]['_moditem'].tag = tag
                        current[level]['_moditem'].is_activated = activated
                        current[level]['_moditem'].time_modified = time_modified
                    parent = current[level]['_moditem']
                    current = current[level]['_children']

        def build_tree(node):
            result = []
            for key, value in node.items():
                moditem = value['_moditem']
                # 递归构建children
                moditem.children = build_tree(value['_children'])
                result.append(moditem)
            return result

        self.mod_list = build_tree(mods)

    def get_mod_item(self, index):
        if 0 <= index.row() < len(self.mod_list):
            return self.mod_list[index.row()]
        return None

    def get_preview_images(self, mod):
        # 假设预览图在mod文件夹下的 'preview' 子文件夹
        mod_path = os.path.join(self.config.mod_dir if not mod.is_activated else self.config.game_dir, mod.fullname)
        preview_dir = mod_path
        if not os.path.exists(preview_dir):
            return []
        images = []
        for fname in os.listdir(preview_dir):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif','.webp')):
                images.append(os.path.join(preview_dir, fname))
        return images[:3]  # 最多三张

    def activate_mod(self, mod):
        # 互斥：取消同一级分类下其它已激活的mod
        root = mod.root if mod.root else mod  # 一级分类
        def deactivate_others(node):
            for child in getattr(node, 'children', []):
                # 只处理实例条目
                if (child is not mod) and getattr(child, 'is_activated', False):
                    self.deactivate_mod(child)
                deactivate_others(child)
        deactivate_others(root)

        # 激活当前mod
        src = os.path.join(self.config.mod_dir, mod.fullname)
        dst = os.path.join(self.config.game_dir, mod.fullname)
        if os.path.exists(src):
            shutil.move(src, dst)
        mod.is_activated = True

    def deactivate_mod(self, mod):
        src = os.path.join(self.config.game_dir, mod.fullname)
        dst = os.path.join(self.config.mod_dir, mod.fullname)
        if os.path.exists(src):
            shutil.move(src, dst)
        mod.is_activated = False
    
    def save_active_mods(self, filename):
        active_mods = []

        def collect_active(mod):
            # 只收集实例条目
            is_instance = bool(mod.tag or getattr(mod, 'fullname', None))
            if is_instance and getattr(mod, 'is_activated', False):
                active_mods.append(mod.fullname)
            for child in getattr(mod, 'children', []):
                collect_active(child)

        for mod in self.mod_list:
            collect_active(mod)

        with open(filename, 'w', encoding='utf-8') as f:
            for name in active_mods:
                f.write(name + '\n')