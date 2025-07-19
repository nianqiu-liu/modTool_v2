# ModTool v2

## Overview
ModTool v2 is a graphical tool designed for managing mods for various games. It allows users to activate, deactivate, and organize mods easily through a user-friendly interface.

## Features
- Load and display mods from specified directories.
- Activate or deactivate mods with a simple click.
- Save and load mod activation lists.
- Sort mods by name or modification date.
- Preview mod images and open mod folders directly.

## Project Structure
```
modtool_v2
├── src
│   ├── main.py                # Entry point of the application
│   ├── config.py              # Configuration settings handler
│   ├── mod_manager.py         # Manages mod loading and activation
│   ├── ui
│   │   ├── main_window.py     # Main application window
│   │   ├── mod_list_view.py   # Displays the list of mods
│   │   └── dialogs.py         # Dialogs for file operations
│   ├── models
│   │   ├── mod_item.py        # Represents a mod entry
│   │   └── tag_item.py        # Represents a tag entry
│   └── utils
│       └── file_ops.py        # Utility functions for file operations
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
└── config.txt                 # Configuration file for game settings
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd modtool_v2
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Ensure the `config.txt` file is properly set up with the game name and mod directories.
2. Run the application:
   ```
   python src/main.py
   ```
3. Use the graphical interface to manage your mods.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.