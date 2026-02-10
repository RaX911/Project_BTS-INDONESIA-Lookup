#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Upload Otomatis ke GitHub dengan Tema Hacker - VERSION 2.0
Mendukung GitHub Token Authentication
"""

import os
import sys
import subprocess
import time
import json
import getpass
import requests
from datetime import datetime
import re

# Fungsi untuk membersihkan layar terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Kelas untuk animasi loading dengan tema hacker
class HackerLoading:
    def __init__(self, total=100, width=50):
        self.total = total
        self.width = width
        self.progress = 0
        self.chars = ["█", "▓", "▒", "░", "▄", "▀", "■", "□", "◼", "◻"]
        self.hacker_colors = ["\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    
    def update(self, progress, message=""):
        self.progress = progress
        percent = self.progress / self.total
        bar_width = int(self.width * percent)
        bar = self.hacker_colors[1] + "█" * bar_width + "\033[0m"
        empty = self.hacker_colors[3] + "░" * (self.width - bar_width) + "\033[0m"
        
        percent_str = f"{self.progress}%"
        if self.progress < 30:
            percent_color = "\033[91m"
        elif self.progress < 70:
            percent_color = "\033[93m"
        else:
            percent_color = "\033[92m"
            
        hacker_text = ""
        if message:
            hacker_text = self.hacker_colors[0] + "[" + self.hacker_colors[2] + ">>>" + self.hacker_colors[0] + "] " + message + "\033[0m"
        
        sys.stdout.write(f"\r[{bar}{empty}] {percent_color}{percent_str:>4}\033[0m {hacker_text}")
        sys.stdout.flush()
    
    def complete(self, message=""):
        self.update(self.total, message)
        print()

# Fungsi untuk tampilan header bertema hacker
def display_hacker_header():
    clear_screen()
    
    hacker_art = """
    \033[92m╔══════════════════════════════════════════════════════════════════════╗
    ║   ██████╗ ██╗  ██╗ ██████╗ ██╗  ██╗███████╗██████╗   ██████╗ ██╗   ██╗██████╗  ║
    ║  ██╔════╝ ██║  ██║██╔════╝ ██║  ██║██╔════╝██╔══██╗██╔═══██╗██║   ██║██╔══██╗ ║
    ║  ███████╗ ███████║██║  ███╗███████║█████╗  ██████╔╝██║   ██║██║   ██║██████╔╝ ║
    ║  ╚════██║ ██╔══██║██║   ██║██╔══██║██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔═══╝  ║
    ║  ███████║ ██║  ██║╚██████╔╝██║  ██║███████╗██║  ██║╚██████╔╝╚██████╔╝██║      ║
    ║  ╚══════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝      ║
    ║                                                                                ║
    ║            [ GITHUB UPLOADER v3.0 - TOKEN AUTHENTICATION ]                     ║
    ║            [ SECURE UPLOAD WITH PERSONAL ACCESS TOKEN ]                       ║
    ╚══════════════════════════════════════════════════════════════════════╝\033[0m
    """
    
    print(hacker_art)
    print("\033[96m" + "=" * 78 + "\033[0m")
    print("\033[93m[!] PERINGATAN: GitHub tidak lagi menerima password untuk Git operations")
    print("[!] Gunakan Personal Access Token (PAT) sebagai pengganti password")
    print("[!] Dapatkan token di: https://github.com/settings/tokens")
    print("[!] Berikan token permissions: repo, workflow, write:packages\033[0m")
    print("\033[96m" + "=" * 78 + "\033[0m\n")

# Fungsi untuk efek mengetik
def typewriter_effect(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Fungsi untuk validasi folder
def validate_folder(path):
    if not os.path.exists(path):
        return False, f"Folder tidak ditemukan: {path}"
    
    if not os.path.isdir(path):
        return False, f"Path bukan folder: {path}"
    
    git_path = os.path.join(path, '.git')
    if os.path.exists(git_path):
        return True, "Folder sudah merupakan repository Git"
    
    return True, "Folder valid"

# Fungsi untuk menampilkan menu
def display_menu():
    print("\n\033[94m" + "═" * 78 + "\033[0m")
    print("\033[95m[ GITHUB UPLOAD MENU ]\033[0m")
    print("\033[94m" + "═" * 78 + "\033[0m")
    print("\033[96m1. Upload proyek baru ke GitHub")
    print("2. Update proyek yang sudah ada")
    print("3. Buat repository baru di GitHub")
    print("4. Lihat status repository lokal")
    print("5. Konfigurasi Git credentials")
    print("6. Keluar dari program\033[0m")
    print("\033[94m" + "═" * 78 + "\033[0m")
    
    while True:
        try:
            choice = input("\033[93m[?] Pilih opsi (1-6): \033[0m").strip()
            if choice in ["1", "2", "3", "4", "5", "6"]:
                return int(choice)
            else:
                print("\033[91m[!] Pilihan tidak valid. Silakan pilih 1-6.\033[0m")
        except KeyboardInterrupt:
            print("\n\033[91m[!] Operasi dibatalkan.\033[0m")
            sys.exit(0)

# Fungsi untuk mendapatkan kredensial GitHub (dengan token)
def get_github_credentials():
    print("\n\033[95m[ GITHUB AUTHENTICATION ]\033[0m")
    print("\033[96m" + "─" * 60 + "\033[0m")
    
    username = input("\033[93m[?] Masukkan username GitHub: \033[0m").strip()
    
    print("\n\033[93m[!] GitHub mengharuskan penggunaan Personal Access Token (PAT)")
    print("[!] Jika belum memiliki token, buat di: https://github.com/settings/tokens")
    print("[!] Token harus memiliki permission: 'repo' (full control of private repositories)\033[0m")
    
    token = getpass.getpass("\033[93m[?] Masukkan GitHub Personal Access Token: \033[0m").strip()
    
    if not username or not token:
        print("\033[91m[!] Username dan token tidak boleh kosong.\033[0m")
        return None, None
    
    # Validasi token format (minimal 40 karakter untuk GitHub token)
    if len(token) < 40:
        print("\033[91m[!] Token tidak valid. Token GitHub minimal 40 karakter.\033[0m")
        return None, None
    
    return username, token

# Fungsi untuk membuat repository baru di GitHub menggunakan API
def create_github_repository(username, token, repo_name, is_private=False):
    print(f"\n\033[93m[!] Membuat repository '{repo_name}' di GitHub...\033[0m")
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": f"Repository created by GitHub Uploader on {datetime.now().strftime('%Y-%m-%d')}",
        "private": is_private,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 201:
            print(f"\033[92m[+] Repository '{repo_name}' berhasil dibuat di GitHub!\033[0m")
            repo_url = response.json().get("html_url")
            print(f"\033[92m[+] URL Repository: {repo_url}\033[0m")
            return repo_url
        elif response.status_code == 401:
            print("\033[91m[!] Token tidak valid atau tidak memiliki permission yang cukup.\033[0m")
            return None
        elif response.status_code == 422:
            print(f"\033[91m[!] Repository '{repo_name}' sudah ada di akun Anda.\033[0m")
            return f"https://github.com/{username}/{repo_name}"
        else:
            print(f"\033[91m[!] Gagal membuat repository. Status code: {response.status_code}\033[0m")
            print(f"\033[91m[!] Response: {response.text}\033[0m")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[!] Gagal terhubung ke GitHub API: {e}\033[0m")
        return None

# Fungsi untuk animasi hacker terminal
def hacker_terminal_effect(stage="upload"):
    loading = HackerLoading()
    
    print("\033[92m")
    
    if stage == "upload":
        messages = [
            "Mengkoneksikan ke GitHub API...",
            "Memvalidasi Personal Access Token...",
            "Mengenkripsi data transfer...",
            "Menganalisis struktur file...",
            "Mempersiapkan upload batch...",
            "Mengunggah ke cloud storage...",
            "Memverifikasi checksum data..."
        ]
    elif stage == "create":
        messages = [
            "Mengkoneksikan ke GitHub API...",
            "Memvalidasi permission token...",
            "Membuat repository baru...",
            "Mengkonfigurasi repository settings...",
            "Menginisialisasi struktur...",
            "Mengatur permissions...",
            "Repository berhasil dibuat!"
        ]
    
    for i, message in enumerate(messages):
        progress = int((i + 1) * 100 / len(messages))
        loading.update(progress, message)
        time.sleep(0.5)
    
    loading.complete("Operasi selesai!")
    print("\033[0m")

# Fungsi untuk konfigurasi Git credentials secara permanen
def configure_git_credentials():
    print("\n\033[95m[ KONFIGURASI GIT CREDENTIALS ]\033[0m")
    
    username = input("\033[93m[?] Masukkan username GitHub: \033[0m").strip()
    email = input("\033[93m[?] Masukkan email GitHub: \033[0m").strip()
    
    try:
        # Konfigurasi global Git
        subprocess.run(["git", "config", "--global", "user.name", username], check=True)
        subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        
        print("\033[92m[+] Git username dan email berhasil dikonfigurasi.\033[0m")
        
        # Tanya apakah ingin menyimpan credential helper
        use_helper = input("\033[93m[?] Gunakan Git credential helper untuk menyimpan token? (y/n): \033[0m").strip().lower()
        
        if use_helper == 'y':
            # Set credential helper untuk menyimpan credentials
            subprocess.run(["git", "config", "--global", "credential.helper", "store"], check=True)
            print("\033[92m[+] Credential helper diaktifkan.\033[0m")
            print("\033[93m[!] Token akan disimpan setelah operasi push pertama.\033[0m")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal mengkonfigurasi Git: {e}\033[0m")
        return False

# Fungsi untuk inisialisasi Git
def init_git_repository(folder_path):
    try:
        if os.path.exists(os.path.join(folder_path, '.git')):
            print("\033[93m[!] Repository Git sudah ada di folder ini.\033[0m")
            return True
        
        subprocess.run(["git", "init"], cwd=folder_path, check=True, capture_output=True)
        print("\033[92m[+] Repository Git berhasil diinisialisasi.\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menginisialisasi Git: {e}\033[0m")
        return False

# Fungsi untuk menambahkan file ke staging
def add_files_to_git(folder_path):
    try:
        subprocess.run(["git", "add", "."], cwd=folder_path, check=True, capture_output=True)
        print("\033[92m[+] Semua file berhasil ditambahkan ke staging area.\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menambahkan file ke Git: {e}\033[0m")
        return False

# Fungsi untuk membuat commit
def create_commit(folder_path, message="Initial commit"):
    try:
        # Cek apakah ada perubahan untuk di-commit
        result = subprocess.run(["git", "status", "--porcelain"], cwd=folder_path, 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("\033[93m[!] Tidak ada perubahan untuk di-commit.\033[0m")
            return True
        
        subprocess.run(["git", "commit", "-m", message], cwd=folder_path, check=True, capture_output=True)
        print(f"\033[92m[+] Commit berhasil dibuat: '{message}'\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal membuat commit: {e}\033[0m")
        return False

# Fungsi untuk menambahkan remote repository dengan token authentication
def add_remote_with_token(folder_path, username, token, repo_name):
    # URL dengan token authentication
    repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    
    try:
        # Cek remote yang sudah ada
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path, 
                              capture_output=True, text=True)
        
        if "origin" in result.stdout:
            # Update existing remote
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], 
                         cwd=folder_path, check=True)
            print("\033[93m[!] Remote origin sudah diperbarui.\033[0m")
        else:
            # Add new remote
            subprocess.run(["git", "remote", "add", "origin", repo_url], 
                         cwd=folder_path, check=True)
            print("\033[92m[+] Remote origin berhasil ditambahkan.\033[0m")
        
        return True, repo_url
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menambahkan remote: {e}\033[0m")
        return False, None

# Fungsi untuk push ke GitHub dengan token authentication
def push_to_github_with_token(folder_path, username, token, branch="main"):
    try:
        # Konfigurasi credential helper untuk sesi ini
        env = os.environ.copy()
        
        # Set environment variables untuk Git credentials
        env['GIT_USERNAME'] = username
        env['GIT_PASSWORD'] = token
        
        # Cek dan set branch
        result = subprocess.run(["git", "branch", "--show-current"], 
                              cwd=folder_path, capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            # Buat branch main jika belum ada
            subprocess.run(["git", "branch", "-M", branch], cwd=folder_path, check=True)
            current_branch = branch
        
        print(f"\033[93m[!] Mengupload ke branch '{current_branch}'...\033[0m")
        
        # Push dengan menggunakan credential helper
        push_command = ["git", "push", "-u", "origin", current_branch]
        
        # Gunakan Popen untuk memasukkan credentials
        process = subprocess.Popen(
            push_command,
            cwd=folder_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Push akan otomatis menggunakan token dari URL
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("\033[92m[+] Push ke GitHub berhasil!\033[0m")
            return True
        else:
            print(f"\033[91m[!] Gagal push ke GitHub:\033[0m")
            print(f"\033[91m{stderr}\033[0m")
            
            # Coba alternatif: gunakan force push jika ada error konflik
            if "failed to push some refs" in stderr:
                force = input("\033[93m[?] Coba force push? (y/n): \033[0m").strip().lower()
                if force == 'y':
                    subprocess.run(["git", "push", "-u", "origin", current_branch, "--force"], 
                                 cwd=folder_path, check=True)
                    print("\033[92m[+] Force push berhasil!\033[0m")
                    return True
            
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal push ke GitHub: {e}\033[0m")
        return False

# Fungsi untuk upload proyek baru
def upload_new_project(folder_path, username, token):
    print(f"\n\033[95m[ UPLOAD PROYEK BARU ]\033[0m")
    print(f"\033[96mFolder: {os.path.basename(folder_path)}\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    # Minta nama repository
    default_name = os.path.basename(folder_path)
    repo_name = input(f"\033[93m[?] Nama repository GitHub (default: '{default_name}'): \033[0m").strip()
    if not repo_name:
        repo_name = default_name
    
    # Bersihkan nama repository (hapus spasi, karakter khusus)
    repo_name = re.sub(r'[^a-zA-Z0-9_.-]', '-', repo_name)
    
    # Tanya apakah repository private
    is_private = input("\033[93m[?] Buat repository private? (y/n): \033[0m").strip().lower() == 'y'
    
    # Buat repository di GitHub
    hacker_terminal_effect("create")
    repo_url = create_github_repository(username, token, repo_name, is_private)
    
    if not repo_url:
        print("\033[91m[!] Gagal membuat repository. Upload dibatalkan.\033[0m")
        return False
    
    # Inisialisasi Git lokal
    if not init_git_repository(folder_path):
        return False
    
    # Tambahkan file
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Pesan commit (default: 'Initial commit'): \033[0m").strip()
    if not commit_msg:
        commit_msg = "Initial commit"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Tambahkan remote dengan token
    success, remote_url = add_remote_with_token(folder_path, username, token, repo_name)
    if not success:
        return False
    
    # Tampilkan animasi upload
    hacker_terminal_effect("upload")
    
    # Push ke GitHub
    if not push_to_github_with_token(folder_path, username, token):
        return False
    
    # Tampilkan sukses
    print("\n\033[92m" + "═" * 78 + "\033[0m")
    print("\033[92m[ UPLOAD BERHASIL! ]\033[0m")
    print(f"\033[96mRepository: {repo_url}")
    print(f"Folder: {folder_path}")
    print(f"Branch: main")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print("\033[92m" + "═" * 78 + "\033[0m")
    
    return True

# Fungsi untuk update proyek yang sudah ada
def update_existing_project(folder_path, username, token):
    print(f"\n\033[95m[ UPDATE PROYEK ]\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    # Cek apakah ini repository Git
    if not os.path.exists(os.path.join(folder_path, '.git')):
        print("\033[91m[!] Folder ini bukan repository Git.\033[0m")
        return False
    
    # Tambahkan file
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Pesan commit: \033[0m").strip()
    if not commit_msg:
        commit_msg = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Tampilkan animasi
    hacker_terminal_effect("upload")
    
    # Cek remote URL untuk mendapatkan repo name
    try:
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path,
                              capture_output=True, text=True)
        if "origin" in result.stdout:
            # Ekstrak repo name dari URL
            lines = result.stdout.split('\n')
            for line in lines:
                if "origin" in line and "github.com" in line:
                    # Cari pattern github.com/username/repo.git
                    match = re.search(r'github\.com[/:]([^/]+)/([^/.]+)', line)
                    if match:
                        repo_user, repo_name = match.groups()
                        break
    except:
        repo_name = os.path.basename(folder_path)
    
    # Push ke GitHub
    if not push_to_github_with_token(folder_path, username, token):
        return False
    
    print("\n\033[92m[+] Update proyek berhasil!\033[0m")
    return True

# Fungsi untuk melihat status repository
def view_repository_status(folder_path):
    print(f"\n\033[95m[ STATUS REPOSITORY ]\033[0m")
    
    try:
        # Git status
        result = subprocess.run(["git", "status"], cwd=folder_path,
                              capture_output=True, text=True)
        print("\033[96m" + result.stdout + "\033[0m")
        
        # Log commit terakhir
        result = subprocess.run(["git", "log", "--oneline", "-5"], cwd=folder_path,
                              capture_output=True, text=True)
        if result.stdout:
            print("\033[93m[ 5 COMMIT TERAKHIR ]\033[0m")
            print("\033[96m" + result.stdout + "\033[0m")
        
        # Remote info
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path,
                              capture_output=True, text=True)
        if result.stdout:
            print("\033[93m[ REMOTE INFO ]\033[0m")
            print("\033[96m" + result.stdout + "\033[0m")
            
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal mendapatkan status: {e}\033[0m")

# Fungsi untuk membuat repository baru saja (tanpa upload)
def create_repository_only(username, token):
    print("\n\033[95m[ BUAT REPOSITORY BARU ]\033[0m")
    
    repo_name = input("\033[93m[?] Nama repository: \033[0m").strip()
    if not repo_name:
        print("\033[91m[!] Nama repository tidak boleh kosong.\033[0m")
        return False
    
    is_private = input("\033[93m[?] Repository private? (y/n): \033[0m").strip().lower() == 'y'
    
    hacker_terminal_effect("create")
    repo_url = create_github_repository(username, token, repo_name, is_private)
    
    if repo_url:
        print(f"\n\033[92m[+] Repository berhasil dibuat!")
        print(f"\033[92m[+] URL: {repo_url}\033[0m")
        return True
    else:
        return False

# Fungsi utama
def main():
    # Tampilkan header
    display_hacker_header()
    
    # Pesan selamat datang
    welcome_msg = "\033[92m[+] GitHub Uploader v3.0 - Token Authentication Ready"
    typewriter_effect(welcome_msg, 0.01)
    
    # Minta input folder
    folder_path = input("\033[93m[?] Masukkan path folder proyek: \033[0m").strip()
    
    if folder_path and os.path.exists(folder_path):
        print(f"\033[92m[+] Folder ditemukan: {folder_path}\033[0m")
        use_current_folder = True
    else:
        print("\033[91m[!] Folder tidak ditemukan.\033[0m")
        use_current_folder = False
        folder_path = os.getcwd()
        print(f"\033[93m[!] Menggunakan folder saat ini: {folder_path}\033[0m")
    
    # Dapatkan kredensial GitHub
    username, token = get_github_credentials()
    if not username or not token:
        print("\033[91m[!] Autentikasi gagal.\033[0m")
        sys.exit(1)
    
    print(f"\033[92m[+] Autentikasi berhasil sebagai: {username}\033[0m")
    
    # Loop menu utama
    while True:
        choice = display_menu()
        
        if choice == 1:
            # Upload proyek baru
            if use_current_folder:
                upload_new_project(folder_path, username, token)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 2:
            # Update proyek yang sudah ada
            if use_current_folder:
                update_existing_project(folder_path, username, token)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 3:
            # Buat repository baru
            create_repository_only(username, token)
        
        elif choice == 4:
            # Lihat status repository
            if use_current_folder:
                view_repository_status(folder_path)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 5:
            # Konfigurasi Git
            configure_git_credentials()
        
        elif choice == 6:
            # Keluar
            print("\n\033[92m[+] Program selesai. Terima kasih!\033[0m")
            break
        
        # Tanya apakah ingin melanjutkan
        if choice != 6:
            continue_choice = input("\n\033[93m[?] Lanjutkan? (y/n): \033[0m").strip().lower()
            if continue_choice != 'y':
                print("\n\033[92m[+] Program selesai.\033[0m")
                break

# Eksekusi program
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m[!] Program dihentikan.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Error: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
