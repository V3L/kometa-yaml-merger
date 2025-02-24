# Folder Creator and Config Merger

## Repository Overview

This repository contains two Python scripts that work together to manage and merge YAML configuration files for your project. The primary scripts are:

- **mergeFolderCreator.py** – Reads `config_core.yml` and creates the necessary folder structure required by `configMerger.py`.
- **configMerger.py** – Merges YAML configuration files and supporting directories into a single final configuration file. This is driven by the headings in a trimmed down Kometa configuration file (`config_core.yml`) 

These scripts use a specific folder structure to organize your configuration files and ensure consistency.

---

## Folder Structure

When you run the folder creator script (`mergeFolderCreator.py`), the following folder structure will be created under your base directory. For example, if your base directory is:

/home/v3l/docker/kometa/config_merge

The structure will be:

- **config_core.yml**  
  The core configuration file that defines the top-level keys and libraries.

- **libraries/**  
  - **global/**  
    - `metadata/`  
    - `collections/`  
    - `overlays/`  
    - `operations/`
  - **movies/**  
    - `metadata/`  
    - `collections/`  
    - `overlays/`  
    - `operations/`
  - **tv/**  
    - `metadata/`  
    - `collections/`  
    - `overlays/`  
    - `operations/`
  - **library_specific/**  
    - For each library defined in `config_core.yml` (e.g., "Movies", "Movies - Disney"), a folder will be created (e.g., `Movies`, `Movies-Disney`) containing:
      - `metadata/`  
      - `collections/`  
      - `overlays/`  
      - `operations/`

- Additional top-level directories (e.g., `settings`, `plex`, etc.) are also created based on the keys defined in `config_core.yml`.

- **_script_logs/**  
  Contains log files (e.g., `config_merge.log`).

- **_config_backups/**  
  Contains backups of the final configuration file.

---

## Prerequisites

- **Python 3.6+**
- **PyYAML** – Install it via pip:
  ```bash
  pip install pyyaml

Make sure your environment meets these requirements before running the scripts.

---

## Usage

### 1. Creating the Folder Structure

**Purpose:**  
`mergeFolderCreator.py` reads your `config_core.yml` and creates the necessary folder structure for configuration merging.

**How to Run:**
1. Place your `config_core.yml` file in the `/home/v3l/docker/kometa/config_merge` directory.
2. Run:
   ```bash
   python mergeFolderCreator.py

The script will create:
A libraries folder with subfolders global, movies, tv, and library_specific (with library-specific subfolders for each library defined in config_core.yml).
Folders for each additional top-level key from config_core.yml (e.g., settings, plex, etc.) in the base directory.
A _script_logs folder for log files.
A _config_backups folder for backups.
A summary of the folders created will be printed to the console.

---

## Customization

You can adjust the following configuration variables in both scripts:

- `CONFIG_BASE`: Base directory for your project.
- `BASE_DIR`: Directory containing your configuration files (including `config_core.yml`).
- `OUTPUT_PATH`: Final configuration file path.
- `LOG_DIR` and `LOG_PATH`: Directory and path for log files.
- `BACKUP_DIR`: Directory for backups.
- `library_subfolders`: List of subfolder names to create under each library folder (e.g., `metadata`, `collections`, `overlays`, `operations`).

Modify these variables as needed to suit your environment.

---

## Troubleshooting

- **config_core.yml:**  
  Ensure that this file exists in the `/home/vel/docker/kometa/config_merge` directory and is correctly formatted.

- **Folder Permissions:**  
  Make sure the scripts have permission to create directories and write files in the specified locations.

- **Log Files:**  
  Check the log file in `_script_logs/config_merge.log` for errors or warnings if something doesn't work as expected.

- **Backup Files:**  
  If a previous configuration exists, it will be backed up in the `_config_backups` folder. Verify that backups are being created correctly.

---

## Contributing

Contributions are welcome! If you have suggestions, improvements, or bug reports, please open an issue or submit a pull request.

---
