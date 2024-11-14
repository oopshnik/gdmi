import webview
import os
import sys
import threading
from flask import Flask, render_template, jsonify, request
import requests
import json
import zipfile
from pathlib import Path
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

window = None
JSON_URL = "https://raw.githubusercontent.com/oopshnik/gdmi/refs/heads/main/list.json"
versions_data = {}

def load_versions():
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        global versions_data
        versions_data = response.json()
        logger.info("Versions data loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load versions data: {str(e)}")
        versions_data = {}

def extract(url, version, install_path):
    try:
        current_dir = os.getcwd()
        download_dir = os.path.join(current_dir, "gd", version)
        os.makedirs(download_dir, exist_ok=True)

        zip_path = os.path.join(download_dir, f"{version}.zip")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                progress = int((downloaded / total_size) * 50)  
                window.evaluate_js(f'updateProgress({progress}, "Downloading...")')

        window.evaluate_js(f'updateProgress(50, "Extracting...")')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
        
    
        window.evaluate_js(f'updateProgress(100, "Installation complete!")')
        
        return True
    except Exception as e:
        logger.error(f"Error in extracting: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html', versions=versions_data)

@app.route('/select_directory')
def select_directory():
    try:
        directory = window.create_file_dialog(webview.FOLDER_DIALOG)
        if directory and len(directory) > 0:
            return jsonify({'path': directory[0]})
        return jsonify({'path': None})
    except Exception as e:
        logger.error(f"Error selecting directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/install', methods=['POST'])
def install():
    try:
        data = request.json
        version = data.get('version')
        directory = data.get('directory')
        options = data.get('options', [])

        if not version or not directory:
            return jsonify({'status': 'error', 'message': 'Missing required parameters'})

        if version not in versions_data:
            return jsonify({'status': 'error', 'message': 'Invalid version'})

        version_info = versions_data[version]
        install_path = Path(directory)
        install_path.mkdir(parents=True, exist_ok=True)

        if not extract(version_info['url'], version, str(install_path)):
            return jsonify({'status': 'error', 'message': 'Installation failed'})

        if 'megahack' in options:
            logger.info("MegaHack req")
        
        if 'geode' in options:
            logger.info("Geode req")

        return jsonify({
            'status': 'success',
            'message': 'Installation completed successfully'
        })

    except Exception as e:
        logger.error(f"Installation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Installation failed: {str(e)}'
        })

def start_server():
    app.run(port=0, threaded=True)

def main():
    global window
    
    load_versions()
    
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    window = webview.create_window(
        'Geometry Dash Modding Installer',
        app,
        width=600,
        height=800,
        resizable=True,
        min_size=(400, 600)
    )
    
    webview.start(debug=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1)
