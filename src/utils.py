import requests
import zipfile
import os
import requests
from rich.console import Console
from rich.table import Table


def fetch_versions():
    response = requests.get("https://raw.githubusercontent.com/oopshnik/gdmi/refs/heads/main/list.json")
    data = response.json()
    return data


def display_versions(data):
    console = Console()
    table = Table(title="Versions Overview")
    table.add_column("Category", justify="center", style="bold cyan")
    table.add_column("Version/Name", justify="center", style="bold magenta")
    table.add_column("ID", justify="center", style="dim")
    table.add_column("URL", justify="left", style="dim")

    latest_version = list(data['latest'].keys())[0]
    latest_name = data['latest'][latest_version]['name']
    latest_id = data['latest'][latest_version]['id']
    latest_url = data['latest'][latest_version]['url']
    table.add_row("Latest Version", latest_name, latest_id, latest_url)

    gdps_name = list(data['gdps'].keys())[0]
    gdps_id = data['gdps'][gdps_name]['id']
    gdps_url = data['gdps'][gdps_name]['url']
    table.add_row("GDPS", gdps_name, gdps_id, gdps_url)

    for version, version_info in data['other'].items():
        table.add_row("Other", version_info['name'], version_info['id'], version_info['url'])
    return table


def download(url, output):
    if isinstance(url, str) and url.startswith("{") and url.endswith("}"):
        url = url.strip("{}").strip("'\"")
    
    os.makedirs(os.path.dirname(output), exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() 
        
        with open(output, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: 
                    f.write(chunk)
        return f"Downloaded {url} to {output}"
    except requests.exceptions.RequestException as e:
        return f"Failed to download {url}. Error: {e}"
def extract(zip_file, output):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output)
    return f"Extracted {zip_file} to {output}"


def json(type, version):
    response = requests.get("https://raw.githubusercontent.com/oopshnik/gdmi/refs/heads/main/list.json")
    if response.status_code == 200:
        json_data = response.json()
        if type in json_data:
            if version in json_data[type]:
                return json_data[type][version]
            else:
                return f"Version {version} not found in {type} section of JSON"
        else:
            return f"Section {type} not found in JSON"
    else:
        return f"Failed to fetch JSON. Status code: {response.status_code}"
