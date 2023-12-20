import requests
import os
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import win32com.client
import json

def get_current_version(install_dir):
    current_version = "1.0.0"  # Versão padrão se o arquivo não existir
    try:
        with open(os.path.join(install_dir, "current_version.txt"), "r") as file:
            current_version = file.read().strip()
    except FileNotFoundError:
        pass
    return current_version

def set_current_version(install_dir, version):
    with open(os.path.join(install_dir, "current_version.txt"), "w") as file:
        file.write(version)

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
        progress_label.config(text="Baixando e instalando o jogo...")
        progress_label.update()

        # Certifique-se de ter permissões administrativas para escrever na pasta de instalação
        os.makedirs(install_dir, exist_ok=True)

        # Obter o link de download do JSON
        download_url = get_download_url_from_json(json_url)

        # Baixar o arquivo ZIP da versão mais recente
        zip_path = os.path.join(install_dir, os.path.basename(download_url))
        download_file(download_url, zip_path)

        # Extrair o conteúdo do arquivo ZIP para a pasta de instalação
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        # Remover o arquivo ZIP após a instalação
        os.remove(zip_path)

        # Atualizar a versão atual após a instalação
        latest_version = get_current_version(install_dir)
        set_current_version(install_dir, latest_version)

        progress_label.config(text="Instalação concluída.")
        progress_label.update()

    except Exception as e:
        progress_label.config(text=f"Ocorreu um erro durante a instalação: {str(e)}")
        progress_label.update()

def check_version(install_dir, progress_label, json_url):
    try:
        progress_label.config(text="Verificando a versão do jogo...")
        progress_label.update()

        # Obter a versão atual do jogo
        current_version = get_current_version(install_dir)

        # Verificar se o arquivo executável do jogo existe
        game_exe_path = os.path.join(install_dir, "netpanzer.exe")

        if not os.path.exists(game_exe_path):
            progress_label.config(text="Jogo não encontrado. Realizando a instalação...")
            progress_label.update()

            # Executar a instalação completa
            install_game(install_dir, progress_label, json_url)
        else:
            progress_label.config(text="Seu jogo está instalado e atualizado.")

        # Criar o atalho para o launcher.exe com o nome "netpanzer"
        launcher_path = os.path.join(install_dir, "launcher.exe")

        # Criar o atalho na área de trabalho
        create_desktop_shortcut(install_dir, launcher_path)

        # Executar o jogo após a verificação e instalação
        subprocess.Popen([game_exe_path], cwd=install_dir)

        # Fechar a janela do tkinter após a execução do jogo
        root.destroy()

    except Exception as e:
        progress_label.config(text=f"Ocorreu um erro inesperado: {str(e)}")

if __name__ == "__main__":
    install_dir = 'C:\\Netpanzer'  # Defina a pasta de instalação
    json_url = 'https://github.com/ph2708/netpanzer-latest/raw/main/version.json'  # URL do arquivo JSON com o link de download

    root = tk.Tk()
    root.title("Verificando Atualizações")
    root.geometry("300x100")

    progress_label = ttk.Label(root, text="Verificando atualizações...")
    progress_label.pack(pady=20)

    check_version(install_dir, progress_label, json_url)

    root.mainloop()
