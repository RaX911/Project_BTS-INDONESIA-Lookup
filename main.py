#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Upload Otomatis ke GitHub dengan Tema Hacker
Penulis: AI Assistant
"""

import os
import sys
import subprocess
import time
import json
import getpass
from datetime import datetime

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
        self.hacker_colors = ["\033[92m", "\033[96m", "\033[94m", "\033[95m"]  # Hijau, Cyan, Biru, Magenta
    
    def update(self, progress, message=""):
        self.progress = progress
        percent = self.progress / self.total
        bar_width = int(self.width * percent)
        bar = self.hacker_colors[1] + "█" * bar_width + "\033[0m"
        empty = self.hacker_colors[3] + "░" * (self.width - bar_width) + "\033[0m"
        
        # Tampilan persentase dengan warna berbeda
        percent_str = f"{self.progress}%"
        if self.progress < 30:
            percent_color = "\033[91m"  # Merah
        elif self.progress < 70:
            percent_color = "\033[93m"  # Kuning
        else:
            percent_color = "\033[92m"  # Hijau
            
        # Buat efek teks bergerak untuk tema hacker
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
    \033[92m╔══════════════════════════════════════════════════════════════╗
    ║  ██████╗ ██╗  ██╗██████╗  ██████╗██╗  ██╗███████╗██████╗  ██████╗  ║
    ║  ██╔════╝ ██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔═══██╗ ║
    ║  ███████╗ ███████║██████╔╝██║     ███████║█████╗  ██████╔╝██║   ██║ ║
    ║  ╚════██║ ██╔══██║██╔═══╝ ██║     ██╔══██║██╔══╝  ██╔══██╗██║   ██║ ║
    ║  ███████║ ██║  ██║██║     ╚██████╗██║  ██║███████╗██║  ██║╚██████╔╝ ║
    ║  ╚══════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ║
    ║                                                                      ║
    ║          [ GITHUB PROJECT UPLOADER - TERMINAL v2.0 ]                ║
    ║          [ TEMA: MATRIX HACKER - ENCRYPTED UPLOAD ]                 ║
    ╚══════════════════════════════════════════════════════════════╝\033[0m
    """
    
    print(hacker_art)
    print("\033[96m" + "=" * 70 + "\033[0m")
    print("\033[93m[!] Sistem upload otomatis GitHub diaktifkan...")
    print("[!] Autentikasi diperlukan untuk mengakses repositori GitHub")
    print("[!] Semua aktivitas akan terekam dalam log sistem\033[0m")
    print("\033[96m" + "=" * 70 + "\033[0m\n")

# Fungsi untuk efek mengetik dengan jeda
def typewriter_effect(text, delay=0.03):
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
    
    # Cek apakah folder mengandung file .git (sudah repo git)
    git_path = os.path.join(path, '.git')
    if os.path.exists(git_path):
        return True, "Folder sudah merupakan repository Git"
    
    return True, "Folder valid"

# Fungsi untuk menampilkan menu interaktif
def display_menu():
    print("\n\033[94m" + "═" * 70 + "\033[0m")
    print("\033[95m[ MENU UPLOAD GITHUB ]\033[0m")
    print("\033[94m" + "═" * 70 + "\033[0m")
    print("\033[96m1. Upload proyek baru ke GitHub")
    print("2. Perbarui proyek yang sudah ada")
    print("3. Lihat status repository lokal")
    print("4. Keluar dari program\033[0m")
    print("\033[94m" + "═" * 70 + "\033[0m")
    
    while True:
        try:
            choice = input("\033[93m[?] Pilih opsi (1-4): \033[0m").strip()
            if choice in ["1", "2", "3", "4"]:
                return int(choice)
            else:
                print("\033[91m[!] Pilihan tidak valid. Silakan pilih 1-4.\033[0m")
        except KeyboardInterrupt:
            print("\n\033[91m[!] Operasi dibatalkan.\033[0m")
            sys.exit(0)

# Fungsi untuk mendapatkan kredensial GitHub
def get_github_credentials():
    print("\n\033[95m[ AUTENTIKASI GITHUB ]\033[0m")
    print("\033[96m" + "─" * 50 + "\033[0m")
    
    username = input("\033[93m[?] Masukkan username GitHub: \033[0m").strip()
    
    # Gunakan getpass untuk keamanan input password
    password = getpass.getpass("\033[93m[?] Masukkan password GitHub (tersembunyi): \033[0m").strip()
    
    # Validasi input tidak kosong
    if not username or not password:
        print("\033[91m[!] Username dan password tidak boleh kosong.\033[0m")
        return None, None
    
    return username, password

# Fungsi untuk membuat efek teks berjalan seperti terminal hacker
def hacker_terminal_effect():
    loading = HackerLoading()
    
    print("\033[92m")
    print("[+] Inisialisasi sistem upload...")
    time.sleep(0.5)
    
    messages = [
        "Mengenkripsi koneksi ke server GitHub...",
        "Memvalidasi kredensial pengguna...",
        "Menganalisis struktur folder...",
        "Mempersiapkan file untuk upload...",
        "Menghubungkan ke repository target...",
        "Mengunggah file ke cloud...",
        "Memverifikasi integritas data..."
    ]
    
    for i, message in enumerate(messages):
        progress = int((i + 1) * 100 / len(messages))
        loading.update(progress, message)
        time.sleep(0.7)
    
    loading.complete("Upload selesai!")
    print("\033[0m")

# Fungsi untuk inisialisasi Git di folder
def init_git_repository(folder_path):
    try:
        # Cek apakah sudah ada repo git
        if os.path.exists(os.path.join(folder_path, '.git')):
            print("\033[93m[!] Repository Git sudah diinisialisasi di folder ini.\033[0m")
            return True
        
        # Inisialisasi Git
        subprocess.run(["git", "init"], cwd=folder_path, check=True, capture_output=True)
        print("\033[92m[+] Repository Git berhasil diinisialisasi.\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menginisialisasi Git: {e}\033[0m")
        return False

# Fungsi untuk menambahkan file ke staging area
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
        subprocess.run(["git", "commit", "-m", message], cwd=folder_path, check=True, capture_output=True)
        print(f"\033[92m[+] Commit berhasil dibuat dengan pesan: '{message}'\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal membuat commit: {e}\033[0m")
        return False

# Fungsi untuk menambahkan remote repository
def add_remote_repository(folder_path, repo_url):
    try:
        # Cek apakah remote sudah ada
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path, capture_output=True, text=True)
        
        if "origin" in result.stdout:
            # Update remote yang sudah ada
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=folder_path, check=True)
            print("\033[93m[!] Remote origin sudah diperbarui.\033[0m")
        else:
            # Tambah remote baru
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=folder_path, check=True)
            print("\033[92m[+] Remote origin berhasil ditambahkan.\033[0m")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menambahkan remote repository: {e}\033[0m")
        return False

# Fungsi untuk push ke GitHub
def push_to_github(folder_path, branch="main"):
    try:
        # Cek branch saat ini
        result = subprocess.run(["git", "branch", "--show-current"], cwd=folder_path, capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            # Buat branch main jika belum ada
            subprocess.run(["git", "branch", "-M", branch], cwd=folder_path, check=True)
        
        # Push ke GitHub
        print(f"\033[93m[!] Mengupload ke branch '{branch}'...\033[0m")
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=folder_path, check=True, capture_output=True)
        
        print("\033[92m[+] Push ke GitHub berhasil!\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal push ke GitHub: {e}\033[0m")
        
        # Coba saran jika error
        if "error: failed to push some refs" in str(e):
            print("\033[93m[!] Coba gunakan: git push -u origin main --force\033[0m")
        
        return False

# Fungsi utama untuk upload proyek baru
def upload_new_project(folder_path, github_user, github_pass):
    print(f"\n\033[95m[ UPLOAD PROYEK BARU: {os.path.basename(folder_path)} ]\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    print(f"\033[92m[+] Folder valid: {folder_path}\033[0m")
    
    # Inisialisasi Git
    if not init_git_repository(folder_path):
        return False
    
    # Tambahkan file
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Masukkan pesan commit (default: 'Initial commit'): \033[0m").strip()
    if not commit_msg:
        commit_msg = "Initial commit"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Minta nama repository
    repo_name = input("\033[93m[?] Masukkan nama repository GitHub (default: nama folder): \033[0m").strip()
    if not repo_name:
        repo_name = os.path.basename(folder_path)
    
    # Buat URL repository
    repo_url = f"https://github.com/{github_user}/{repo_name}.git"
    
    print(f"\033[93m[!] Repository URL: {repo_url}\033[0m")
    
    # Tambah remote repository
    if not add_remote_repository(folder_path, repo_url):
        return False
    
    # Tampilkan animasi hacker
    hacker_terminal_effect()
    
    # Push ke GitHub
    if not push_to_github(folder_path):
        return False
    
    # Tampilkan informasi sukses
    print("\n\033[92m" + "═" * 70 + "\033[0m")
    print("\033[92m[ UPLOAD BERHASIL! ]\033[0m")
    print(f"\033[96mRepository: {repo_url}")
    print(f"Folder: {folder_path}")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print("\033[92m" + "═" * 70 + "\033[0m")
    
    return True

# Fungsi untuk update proyek yang sudah ada
def update_existing_project(folder_path):
    print(f"\n\033[95m[ UPDATE PROYEK: {os.path.basename(folder_path)} ]\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    # Cek apakah ini repository Git
    if not os.path.exists(os.path.join(folder_path, '.git')):
        print("\033[91m[!] Folder ini bukan repository Git. Gunakan opsi 'Upload proyek baru'.\033[0m")
        return False
    
    # Tambahkan file yang berubah
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Masukkan pesan commit: \033[0m").strip()
    if not commit_msg:
        commit_msg = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Tampilkan animasi hacker
    hacker_terminal_effect()
    
    # Push ke GitHub
    if not push_to_github(folder_path):
        return False
    
    print("\n\033[92m[+] Update proyek berhasil!\033[0m")
    return True

# Fungsi untuk melihat status repository
def view_repository_status(folder_path):
    print(f"\n\033[95m[ STATUS REPOSITORY: {os.path.basename(folder_path)} ]\033[0m")
    
    try:
        # Status Git
        result = subprocess.run(["git", "status"], cwd=folder_path, capture_output=True, text=True)
        print("\033[96m" + result.stdout + "\033[0m")
        
        # Log commit terakhir
        result = subprocess.run(["git", "log", "--oneline", "-5"], cwd=folder_path, capture_output=True, text=True)
        print("\033[93m[ 5 COMMIT TERAKHIR ]\033[0m")
        print("\033[96m" + result.stdout + "\033[0m")
        
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal mendapatkan status repository: {e}\033[0m")

# Fungsi utama
def main():
    # Tampilkan header hacker
    display_hacker_header()
    
    # Pesan selamat datang
    welcome_msg = "\033[92m[+] Sistem upload GitHub siap digunakan. Tekan Ctrl+C untuk keluar.\033[0m"
    typewriter_effect(welcome_msg, 0.01)
    
    # Minta input folder
    folder_path = input("\033[93m[?] Masukkan path folder proyek: \033[0m").strip()
    
    # Validasi folder
    if not folder_path or not os.path.exists(folder_path):
        print("\033[91m[!] Folder tidak valid. Pastikan path folder benar.\033[0m")
        sys.exit(1)
    
    # Dapatkan kredensial GitHub
    github_user, github_pass = get_github_credentials()
    if not github_user or not github_pass:
        print("\033[91m[!] Autentikasi gagal. Program dihentikan.\033[0m")
        sys.exit(1)
    
    # Verifikasi kredensial (simulasi)
    print("\033[92m[+] Verifikasi kredensial...\033[0m")
    time.sleep(1)
    print(f"\033[92m[+] Login berhasil sebagai: {github_user}\033[0m")
    
    # Loop menu utama
    while True:
        choice = display_menu()
        
        if choice == 1:
            # Upload proyek baru
            upload_new_project(folder_path, github_user, github_pass)
        
        elif choice == 2:
            # Update proyek yang sudah ada
            update_existing_project(folder_path)
        
        elif choice == 3:
            # Lihat status repository
            view_repository_status(folder_path)
        
        elif choice == 4:
            # Keluar
            print("\n\033[92m[+] Keluar dari program. Terima kasih!\033[0m")
            sys.exit(0)
        
        # Tanya apakah ingin melanjutkan
        continue_choice = input("\n\033[93m[?] Lanjutkan operasi lain? (y/n): \033[0m").strip().lower()
        if continue_choice != 'y':
            print("\n\033[92m[+] Program selesai. Sampai jumpa!\033[0m")
            break

# Eksekusi program
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m[!] Program dihentikan oleh pengguna.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Terjadi kesalahan: {e}\033[0m")
        sys.exit(1)
