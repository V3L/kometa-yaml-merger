import os
import yaml

# --- Configuration Variables ---
CONFIG_BASE = '/home/vel/docker/kometa/'  # Base directory to be replaced with '/config/' in links.
BASE_DIR = os.path.join(CONFIG_BASE, 'config_merge')   # Directory containing config_core.yml, libraries, etc.
CONFIG_CORE_PATH = os.path.join(BASE_DIR, 'config_core.yml')

# Directories for additional files:
LOG_DIR = os.path.join(BASE_DIR, '_script_logs')
LOG_PATH = os.path.join(LOG_DIR, 'config_merge.log')
BACKUP_DIR = os.path.join(BASE_DIR, '_config_backups')  # Configurable backup directory

# Folders to create under each library folder.
library_subfolders = ['metadata', 'collections', 'overlays', 'operations']

# --- Load config_core.yml ---
if not os.path.exists(CONFIG_CORE_PATH):
    print(f"config_core.yml not found at {CONFIG_CORE_PATH}")
    exit(1)

with open(CONFIG_CORE_PATH, 'r') as f:
    core_config = yaml.safe_load(f) or {}

# --- Create Folder Structure ---

# Ensure base directories exist:
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# 1. Create the 'libraries' folder under BASE_DIR.
libraries_dir = os.path.join(BASE_DIR, 'libraries')
os.makedirs(libraries_dir, exist_ok=True)

# 2. Under 'libraries', create fixed folders: global, movies, tv, and library_specific.
for sub in ['global', 'movies', 'tv', 'library_specific']:
    os.makedirs(os.path.join(libraries_dir, sub), exist_ok=True)

# 3. Under each of global, movies, and tv, create the required subfolders.
for parent in ['global', 'movies', 'tv']:
    parent_dir = os.path.join(libraries_dir, parent)
    for folder in library_subfolders:
        os.makedirs(os.path.join(parent_dir, folder), exist_ok=True)

# 4. Under 'library_specific', create a folder for each library defined in config_core.yml.
def library_key_to_folder(library_key):
    # Convert library key to folder name: e.g., "Movies - Disney" becomes "Movies-Disney"
    return library_key.replace(" - ", "-").replace(" ", "-")

if "libraries" in core_config and isinstance(core_config["libraries"], dict):
    for library_key in core_config["libraries"]:
        folder_name = library_key_to_folder(library_key)
        lib_dir = os.path.join(libraries_dir, 'library_specific', folder_name)
        os.makedirs(lib_dir, exist_ok=True)
        for folder in library_subfolders:
            os.makedirs(os.path.join(lib_dir, folder), exist_ok=True)

# 5. For additional (non-library) top-level keys in config_core.yml, create folders in BASE_DIR.
additional_keys = [key for key in core_config if key.lower() != "libraries"]
for key in additional_keys:
    os.makedirs(os.path.join(BASE_DIR, key), exist_ok=True)

# --- Summary ---
print("Folder structure created successfully.\n")
print("Summary of folders created:")
print(f"Base Directory: {BASE_DIR}")
print("\nUnder 'libraries':")
print("  global:")
for folder in library_subfolders:
    print(f"    - {folder}")
print("  movies:")
for folder in library_subfolders:
    print(f"    - {folder}")
print("  tv:")
for folder in library_subfolders:
    print(f"    - {folder}")
print("  library_specific:")
if "libraries" in core_config and isinstance(core_config["libraries"], dict):
    for library_key in core_config["libraries"]:
        folder_name = library_key_to_folder(library_key)
        print(f"    - {folder_name}:")
        for folder in library_subfolders:
            print(f"        - {folder}")
print("\nAdditional top-level directories:")
for key in additional_keys:
    print(f"  - {key}")
print(f"\nLog Directory: {LOG_DIR}")
print(f"Backup Directory: {BACKUP_DIR}")
