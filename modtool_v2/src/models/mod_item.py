class ModItem:
    def __init__(self, name, fullname='', tag='', is_activated=False, time_modified=None, is_selected=False, children=None, root=None):
        self.name = name
        self.fullname = fullname
        self.tag = tag
        self.is_activated = is_activated
        self.time_modified = time_modified
        self.is_selected = is_selected
        self.children = children if children else []
        self.root = root if root else None

    def activate(self):
        self.is_activated = True

    def deactivate(self):
        self.is_activated = False

    def toggle_selection(self):
        self.is_selected = not self.is_selected

    def __repr__(self):
        return f"ModItem(mod_name={self.name}, tag={self.tag}, is_activated={self.is_activated}, time_modified={self.time_modified})"