import argparse
import json
import os
import requests

def load_versions(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def download_file(url, directory, name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, name)
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print(f"Downloaded {name} to {file_path}")

def list_versions(versions):
    print("Available versions:")
    for category, items in versions.items():
        print(f"\n{category.upper()}:")
        for id, info in items.items():
            print(f"  {id}: {info['name']}")

def main():
    parser = argparse.ArgumentParser(description="Download a specific version of Geometry Dash.")
    parser.add_argument('version_id', type=str, help="The ID of the version to download")
    parser.add_argument('--directory', type=str, default='.', help="The directory to save the downloaded file")
    parser.add_argument('--list', action='store_true', help="List available versions and exit")

    args = parser.parse_args()

    versions = load_versions('list.json')

    if args.list:
        list_versions(versions)
        return

    version_info = None
    for category in versions.values():
        if args.version_id in category:
            version_info = category[args.version_id]
            break

    if not version_info:
        print(f"Version with ID '{args.version_id}' not found.")
        list_versions(versions)
        return

    download_file(version_info['url'], args.directory, f"{version_info['id']}.zip")

if __name__ == "__main__":
    main()