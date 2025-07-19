def read_mod_list(file_path):
    """Reads the mod list from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            mod_list = [line.strip() for line in file if line.strip()]
        return mod_list
    except Exception as e:
        print(f"Error reading mod list from {file_path}: {e}")
        return []

def write_mod_list(file_path, mod_list):
    """Writes the mod list to a specified file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for mod in mod_list:
                file.write(f"{mod}\n")
    except Exception as e:
        print(f"Error writing mod list to {file_path}: {e}")

def move_mod_folder(source, destination):
    """Moves a mod folder from source to destination."""
    import shutil
    try:
        shutil.move(source, destination)
    except Exception as e:
        print(f"Error moving folder from {source} to {destination}: {e}")

def get_mod_directory_structure(mod_dir):
    """Returns the structure of the mod directory."""
    import os
    structure = {}
    try:
        for root, dirs, files in os.walk(mod_dir):
            for dir_name in dirs:
                structure[dir_name] = os.path.join(root, dir_name)
    except Exception as e:
        print(f"Error accessing mod directory {mod_dir}: {e}")
    return structure