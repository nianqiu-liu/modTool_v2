import os

class Config:
    def __init__(self, config_file='config.txt'):
        self.config_file = config_file
        self.game_name = ""
        self.mod_dir = ""
        self.game_dir = ""
        self.tag_list = {}

        self.load_config()

    def load_config(self):
        fdir = os.path.join(os.getcwd(),self.config_file)  # Ensure the current working directory is set correctly
        if not os.path.exists(fdir):
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")

        with open(self.config_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if len(lines) < 3:
                raise ValueError("Configuration file must contain at least four lines.")

            self.game_name = lines[0].strip()
            self.mod_dir = lines[1].strip()
            self.game_dir = lines[2].strip()

            if len(lines) >= 4:
                for line in lines[3:]:
                    is_show, tag = line.strip().split(',')
                    self.tag_list[tag] = is_show.lower() == 'true'

    def get_game_name(self):
        return self.game_name

    def get_mod_dir(self):
        return self.mod_dir

    def get_game_dir(self):
        return self.game_dir

    def get_tag_list(self):
        return self.tag_list

    def is_tag_visible(self, tag):
        return self.tag_list.get(tag, False)