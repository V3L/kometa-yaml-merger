import os
import re
import yaml
import logging
from datetime import datetime

# --- Configuration ---
CONFIG_BASE = '/home/vel/docker/kometa/'  # Base directory to be replaced with '/config/' in links.
BASE_DIR = os.path.join(CONFIG_BASE, 'config_merge')   # Directory containing config_core.yml, libraries, etc.
OUTPUT_PATH = '/home/vel/docker/kometa/config.yml'
LOG_DIR = os.path.join(BASE_DIR, '_script_logs')
LOG_PATH = os.path.join(LOG_DIR, 'config_merge.log')
BACKUP_DIR = os.path.join(BASE_DIR, '_config_backups')  # Configurable backup directory

# --- Setup Logging (overwrite log on each run) ---
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# --- Helper Functions ---

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                logging.warning(f"Empty data loaded from {file_path}")
                return {}
            return data
    except Exception as e:
        logging.error(f"Error loading YAML from {file_path}: {e}")
        return {}

def merge_yaml(base, update):
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            merge_yaml(base[key], value)
        else:
            base[key] = value

def process_directory(dir_path):
    """Merge all YAML files (non-recursively) in a directory."""
    result = {}
    if os.path.isdir(dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                file_path = os.path.join(dir_path, filename)
                data = load_yaml(file_path)
                merge_yaml(result, data)
                logging.info(f"Processed {file_path}")
    else:
        logging.info(f"Directory not found: {dir_path}")
    return result

def format_link(file_path):
    """
    Replace CONFIG_BASE with '/config/' (ensuring a trailing slash) and normalize the path.
    E.g., '/home/ben/docker/plex-meta-manager/config_merge/libraries/global/collections/MCU.yml'
    becomes '/config/config_merge/libraries/global/collections/MCU.yml'
    """
    replaced = file_path.replace(CONFIG_BASE, '/config/')
    return os.path.normpath(replaced).replace("\\", "/")

def process_link_directory(dir_path, expected_key=None):
    """
    For folder types (metadata, collections, overlays, playlists), scan all YAML files in dir_path.
    - If expected_key is provided and the file’s first top-level key equals expected_key (case-insensitive),
      then unwrap the raw data (i.e. include file_data[expected_key] rather than the entire dict).
    - Otherwise, create a file link (an object with a "file" key using format_link).
    Returns a list with file links grouped at the top followed by any raw data.
    """
    links = []
    raw_data = []
    if os.path.isdir(dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                file_path = os.path.join(dir_path, filename)
                file_data = load_yaml(file_path)
                if expected_key and isinstance(file_data, dict):
                    first_key = next(iter(file_data), None)
                    if first_key and first_key.lower() == expected_key.lower():
                        content = file_data[first_key]
                        if isinstance(content, list):
                            raw_data.extend(content)
                        else:
                            raw_data.append(content)
                        logging.info(f"Included raw data from {file_path} with key '{expected_key}' stripped")
                        continue
                link = {"file": format_link(file_path)}
                links.append(link)
                logging.info(f"Added link for {file_path}: {link}")
    else:
        logging.info(f"Link directory not found: {dir_path}")
    return links + raw_data

def library_key_to_folder(library_key):
    """Convert a library key from config_core.yml into the folder name used in library_specific.
       E.g., 'Movies - Disney' becomes 'Movies-Disney'."""
    return library_key.replace(" - ", "-").replace(" ", "-")

def process_library(library_key):
    """
    For a given library (as defined in config_core.yml under libraries),
    merge data from three sources: global, movies/tv, and library_specific.
    For folder types 'metadata', 'collections', 'overlays', and 'playlists':
      - If a file's top-level key matches the expected mapping key (e.g. "collection_files"),
        include the raw data (with the key stripped) instead of a file link.
      - Otherwise, add a file link.
    For 'operations', merge YAML content normally.
    Returns a dict with keys: metadata_files, collection_files, overlay_files, playlist_files, operations.
    """
    result = {}
    mapping = {
        "metadata": "metadata_files",
        "collections": "collection_files",
        "overlays": "overlay_files",
        "playlists": "playlist_files",
        "operations": "operations"
    }
    for folder_type, final_key in mapping.items():
        if folder_type in ["metadata", "collections", "overlays", "playlists"]:
            merged = []
            # Global source
            global_path = os.path.join(BASE_DIR, "libraries", "global", folder_type)
            merged.extend(process_link_directory(global_path, expected_key=final_key))
            # Movies or TV source based on library key
            if "movies" in library_key.lower():
                source = os.path.join(BASE_DIR, "libraries", "movies", folder_type)
                merged.extend(process_link_directory(source, expected_key=final_key))
            elif "tv" in library_key.lower():
                source = os.path.join(BASE_DIR, "libraries", "tv", folder_type)
                merged.extend(process_link_directory(source, expected_key=final_key))
            # Library-specific source
            folder_name = library_key_to_folder(library_key)
            libspec_path = os.path.join(BASE_DIR, "libraries", "library_specific", folder_name, folder_type)
            merged.extend(process_link_directory(libspec_path, expected_key=final_key))
        else:
            # For operations, merge YAML content normally.
            merged = {}
            global_path = os.path.join(BASE_DIR, "libraries", "global", folder_type)
            merge_yaml(merged, process_directory(global_path))
            if "movies" in library_key.lower():
                source = os.path.join(BASE_DIR, "libraries", "movies", folder_type)
                merge_yaml(merged, process_directory(source))
            elif "tv" in library_key.lower():
                source = os.path.join(BASE_DIR, "libraries", "tv", folder_type)
                merge_yaml(merged, process_directory(source))
            folder_name = library_key_to_folder(library_key)
            libspec_path = os.path.join(BASE_DIR, "libraries", "library_specific", folder_name, folder_type)
            merge_yaml(merged, process_directory(libspec_path))
        if merged not in ([], {}, None):
            result[final_key] = merged
            logging.info(f"For library '{library_key}', merged '{folder_type}' into {final_key}: {merged}")
        else:
            logging.info(f"For library '{library_key}', no data for folder type '{folder_type}'")
    return result

def process_category_from_core(category, original_value):
    """
    Process a non-library category (e.g., settings, plex, radarr, etc.)
    using only keys from the original configuration.
    """
    # If original_value is None, use empty dict.
    if original_value is None:
        original_value = {}
    dir_path = os.path.join(BASE_DIR, category)
    additional = {}
    if os.path.isdir(dir_path):
        additional = process_directory(dir_path)
        if isinstance(additional, dict) and len(additional) == 1:
            key = next(iter(additional))
            if key.lower() == category.lower():
                additional = additional[key]
    merged = {}
    merge_yaml(merged, original_value)
    merge_yaml(merged, additional)
    logging.info(f"Processed category '{category}' from {dir_path}: {merged}")
    return merged

def filter_by_keys(final, keys):
    """
    Recursively filter the dictionary 'final' to only include keys in the list 'keys'.
    If 'final' is a dictionary, only keep keys that are present in 'keys'.
    For nested dictionaries, 'keys' should be a dictionary specifying the allowed keys at each level.
    """
    if isinstance(final, dict) and isinstance(keys, dict):
        filtered = {}
        for k, subkeys in keys.items():
            if k in final:
                filtered[k] = filter_by_keys(final[k], subkeys)
        return filtered
    elif isinstance(final, dict) and isinstance(keys, list):
        return {k: final[k] for k in final if k in keys}
    else:
        return final

def backup_existing_file(file_path, backup_dir):
    """If file_path exists, rename it to {base_filename}.backup.{YYYYMMDD-HHMMSS}.yml in backup_dir."""
    if os.path.exists(file_path):
        if not os.path.isdir(backup_dir):
            os.makedirs(backup_dir)
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_filename = f"{base_filename}.backup.{timestamp}.yml"
        backup_path = os.path.join(backup_dir, backup_filename)
        os.rename(file_path, backup_path)
        logging.info(f"Existing file {file_path} backed up as {backup_path}")

# --- Main Script ---
def main():
    # Load the original core configuration.
    core_path = os.path.join(BASE_DIR, "config_core.yml")
    original_core = load_yaml(core_path)
    if not original_core:
        logging.error(f"config_core.yml not found or empty at {core_path}")
        return
    logging.info(f"Loaded core configuration from {core_path}")

    final_config = {}
    # Process only the keys from original_core.
    for key, original_value in original_core.items():
        if key.lower() == "libraries":
            final_config["libraries"] = {}
            for library_key, lib_original in original_value.items():
                processed = process_library(library_key)
                # Only select keys from processed that are in lib_original.
                filtered = {k: v for k, v in processed.items() if k in lib_original}
                final_config["libraries"][library_key] = filtered
        else:
            final_config[key] = process_category_from_core(key, original_value)
    
    # Backup existing output file, if any.
    backup_existing_file(OUTPUT_PATH, BACKUP_DIR)
    
    # Save the final configuration.
    try:
        dumped = yaml.safe_dump(final_config, default_flow_style=False, sort_keys=False)
        # Post-process: remove empty quotes for keys with null/empty values.
        dumped = dumped.replace(': ""', ':').replace(": ''", ':').replace(': null', ':')
        with open(OUTPUT_PATH, "w") as f:
            f.write(dumped)
        logging.info(f"Final configuration saved to {OUTPUT_PATH}")
    except Exception as e:
        logging.error(f"Error saving final configuration: {e}")

if __name__ == "__main__":
    main()
