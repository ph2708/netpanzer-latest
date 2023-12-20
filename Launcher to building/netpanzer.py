import requests
import os
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk
import win32com.client

def get_current_version(install_dir):
    current_version = "1.0.0"  # Default version if the file does not exist
    try:
        with open(os.path.join(install_dir, "current_version.txt"), "r") as file:
            current_version = file.read().strip()
    except FileNotFoundError:
        pass
    return current_version

def set_current_version(install_dir, version):
    with open(os.path.join(install_dir, "current_version.txt"), "w") as file:
        file.write(version)

def get_latest_version_from_json(json_url):
    try:
        response = requests.get(json_url)
        data = response.json()
        latest_version = data.get("version")
        if latest_version:
            return latest_version
        else:
            raise ValueError("Could not retrieve the latest version from the JSON file.")
    except Exception as e:
        print(f"Error in obtaining the latest version: {e}")
        return None

def create_desktop_shortcut(install_dir, target_path):
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    shortcut_path = os.path.join(desktop, "Netpanzer.lnk")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.WorkingDirectory = install_dir
    shortcut.save()

def download_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def get_download_url_from_json(json_url):
    response = requests.get(json_url)
    data = response.json()
    download_url = data.get("download_url")
    return download_url

def install_game(install_dir, progress_label, json_url):
    try:
        progress_label.config(text="Downloading and installing the game...")
        progress_label.update()

        os.makedirs(install_dir, exist_ok=True)

        download_url = get_download_url_from_json(json_url)
        zip_path = os.path.join(install_dir, os.path.basename(download_url))
        download_file(download_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        os.remove(zip_path)

        latest_version = get_latest_version_from_json(json_url)
        if latest_version:
            set_current_version(install_dir, latest_version)
        else:
            raise Exception("Could not retrieve the latest version of the game.")

        progress_label.config(text="Installation complete.")
        progress_label.update()

        launch_game(install_dir)

    except Exception as e:
        progress_label.config(text=f"An error occurred during installation: {str(e)}")
        progress_label.update()
    finally:
        close_window()



def check_version(install_dir, progress_label, json_url):
    try:
        progress_label.config(text="Checking the game version...")
        progress_label.update()

        current_version = get_current_version(install_dir)
        latest_version = get_latest_version_from_json(json_url)

        game_exe_path = os.path.join(install_dir, "netpanzer.exe")

        if not os.path.exists(game_exe_path) or current_version != latest_version:
            progress_label.config(text="Game not found or outdated. Performing installation...")
            progress_label.update()
            install_game(install_dir, progress_label, json_url)
        else:
            progress_label.config(text="Your game is installed and up to date.")
            progress_label.update()
            launch_game(install_dir)

    except Exception as e:
        progress_label.config(text=f"An unexpected error occurred: {str(e)}")
    finally:
        close_window()

def launch_game(install_dir):
    game_exe_path = os.path.join(install_dir, "netpanzer.exe")
    if os.path.exists(game_exe_path):
        subprocess.Popen([game_exe_path], cwd=install_dir)
    else:
        print("Game executable not found.")

def close_window():
    root.after(1000, root.destroy)  # Wait for 1 second before closing the window

if __name__ == "__main__":
    install_dir = 'C:\\Netpanzer'
    json_url = 'https://github.com/ph2708/netpanzer-latest/raw/main/version.json'

    root = tk.Tk()
    root.title("Checking Updates")
    root.geometry("300x100")

    progress_label = ttk.Label(root, text="Checking updates...")
    progress_label.pack(pady=20)

    check_version(install_dir, progress_label, json_url)

    root.mainloop()
