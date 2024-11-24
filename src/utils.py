import os
import json
import requests
from tqdm import tqdm
import shutil

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

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
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
    return True

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    return {}

def save_config(config_path, config):
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

def organize_path(base_dir, category, version_name):
    return os.path.join(base_dir, category, version_name)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def toggle_extension(config, extension_id):
    if extension_id in config:
        config[extension_id] = not config[extension_id]
    else:
        config[extension_id] = True
    return config