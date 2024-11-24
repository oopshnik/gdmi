import os
import json
import win32com.client
from utils import fetch_data, save_file, load_config, save_config, organize_path, ensure_directory_exists, toggle_extension
import shutil
CONFIG_PATH = 'config.json'
DATA_URL = 'https://raw.githubusercontent.com/oopshnik/gdmi/refs/heads/main/list.json'

def display_categories(data):
    print("Categories:")
    categories = ['latest', 'gdps', 'other', 'stuffs']
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category.capitalize()}")

def display_versions(versions):
    print("Available Versions:")
    for version_id, version in versions.items():
        print(f"{version_id}. {version['name']}")

def display_extensions(config):
    print("Current Extensions:")
    for ext_id, enabled in config.items():
        print(f"[{'X' if enabled else ' '}] {ext_id}")

def get_category_choice():
    while True:
        choice = input("Select a category: ")
        if choice.isdigit():
            choice = int(choice)
            categories = ['latest', 'gdps', 'other', 'stuffs']
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
        print("Invalid choice, please try again.")

def get_version_choice(versions):
    while True:
        choice = input("Select a version by ID: ")
        if choice in versions:
            return versions[choice]
        print("Invalid version ID, please try again.")

def create_shortcut(target_path, shortcut_path, description=""):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.Description = description
    shortcut.save()

def main():
    data = fetch_data(DATA_URL)
    if not data:
        return

    config = load_config(CONFIG_PATH)
    base_dir = input("Enter the directory to save files: ")
    ensure_directory_exists(base_dir)

    while True:
        display_categories(data)
        category = get_category_choice()

        if category == 'stuffs':
            display_extensions(config)
            ext_id = input("Toggle an extension by typing its ID: ").strip().lower()
            config = toggle_extension(config, ext_id)
            save_config(CONFIG_PATH, config)
            print(f"Extension '{ext_id}' has been turned {'ON' if config[ext_id] else 'OFF'}.")
            continue

        versions = data.get(category, {})
        if not versions:
            print(f"No versions available for {category}.")
            continue

        display_versions(versions)
        version = get_version_choice(versions)

        save_path = organize_path(base_dir, category, version['name'])
        ensure_directory_exists(save_path)
        file_path = os.path.join(save_path, f"{version['name']}.zip")

        if save_file(version['url'], file_path):
            print(f"Downloaded {version['name']} to {file_path}")

            # Extract the zip file
            extract_path = os.path.join(save_path, version['name'])
            ensure_directory_exists(extract_path)
            shutil.unpack_archive(file_path, extract_path)

            # Find GeometryDash.exe in the extracted folder
            geometry_dash_exe_path = os.path.join(extract_path, "GeometryDash.exe")
            if not os.path.exists(geometry_dash_exe_path):
                print("GeometryDash.exe not found in the extracted files.")
            else:
                # Ask if the user wants to create a shortcut
                create_shortcut_choice = input("Do you want to create a shortcut to GeometryDash.exe? (y/n): ").strip().lower()
                if create_shortcut_choice == 'y':
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    shortcut_path = os.path.join(desktop, "GeometryDash.lnk")
                    create_shortcut(geometry_dash_exe_path, shortcut_path, "Shortcut to GeometryDash")
                    print(f"Shortcut created at {shortcut_path}")
        else:
            print(f"Failed to download {version['name']}")

        cont = input("Do you want to download another version? (y/n): ").strip().lower()
        if cont != 'y':
            break

if __name__ == "__main__":
    main()