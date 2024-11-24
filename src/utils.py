import os
import json
import requests
from tqdm import tqdm
import shutil
import win32com.client

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return f"Error fetching data: {e}"

def save_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        with open(save_path, 'wb') as file, tqdm(
            desc=save_path,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)
        return "Download successful"
    except requests.RequestException as e:
        return f"Error downloading file: {e}"

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    return {}

def save_config(config_path, config):
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
    return "Config saved"

def organize_path(base_dir, category, version_name):
    return os.path.join(base_dir, category, version_name)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def toggle_extension(config, extension_id):
    if extension_id in config:
        config[extension_id] = not config[extension_id]
    else:
        config[extension_id] = True
    return config

def create_shortcut(target_path, shortcut_path, description=""):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.Description = description
        shortcut.save()
        return "Shortcut created"
    except Exception as e:
        return f"Error creating shortcut: {e}"

def extract_zip(file_path, extract_path):
    try:
        shutil.unpack_archive(file_path, extract_path)
        return "Extraction successful"
    except Exception as e:
        return f"Error extracting file: {e}"

def download_and_extract_version(version, save_path):
    download_result = save_file(version['url'], save_path)
    if "successful" not in download_result:
        return download_result

    extract_result = extract_zip(save_path, os.path.dirname(save_path))
    if "successful" not in extract_result:
        return extract_result

    return "Download and extraction successful"

def find_geometry_dash_exe(extract_path):
    for root, dirs, files in os.walk(extract_path):
        if "GeometryDash.exe" in files:
            return os.path.join(root, "GeometryDash.exe")
    return None