import customtkinter as ctk
import requests
import json
import random
import time
import threading
from tkinter import filedialog, messagebox
import tkinter as tk
from customtkinter import ThemeManager
import os
import sys
from pystray import MenuItem as item
import pystray
from PIL import Image
from pybip39 import Mnemonic

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ErwinGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Erwin Submission GUI")
        self.geometry("800x600")

        self.icon = None  # Initialize icon as None
        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)

        icon_path = resource_path("erwin.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting icon: {e}")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.api_keys = []
        self.is_running = False
        self.stop_requested = False
        self.use_proxies = False
        self.wordlist = []
        self.proxies = []

        self.create_widgets()
        self.load_api_keys()
        self.load_proxies()

    def create_widgets(self):
        api_frame = ctk.CTkFrame(self)
        api_frame.pack(fill=ctk.X, padx=20, pady=10)

        ctk.CTkLabel(api_frame, text="API Keys").pack(side=ctk.LEFT, padx=5)
        self.api_key_entry = ctk.CTkEntry(api_frame, width=300)
        self.api_key_entry.pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(api_frame, text="Add Key", command=self.add_api_key).pack(side=ctk.LEFT, padx=5)

        bg_color = self.cget("bg")
        fg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
        select_color = ThemeManager.theme["CTkButton"]["fg_color"]
        
        self.api_keys_listbox = tk.Listbox(self, 
                                        height=5, 
                                        bg=bg_color, 
                                        fg=fg_color,
                                        selectbackground=select_color[1],
                                        selectforeground=fg_color,
                                        borderwidth=0,
                                        highlightthickness=0)
        self.api_keys_listbox.pack(fill=ctk.X, padx=20, pady=5)
        
        ctk.CTkButton(self, text="Remove Selected Key", command=self.remove_api_key).pack(pady=5)

        proxy_frame = ctk.CTkFrame(self)
        proxy_frame.pack(fill=ctk.X, padx=20, pady=10)

        ctk.CTkLabel(proxy_frame, text="Proxy Settings").pack(side=ctk.LEFT, padx=5)
        self.proxy_file_path = ctk.StringVar()
        ctk.CTkEntry(proxy_frame, textvariable=self.proxy_file_path, width=300).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(proxy_frame, text="Upload Proxies", command=self.upload_proxies).pack(side=ctk.LEFT, padx=5)

        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill=ctk.X, padx=20, pady=10)

        self.toggle_proxies_btn = ctk.CTkButton(control_frame, text="Enable Proxies", command=self.toggle_proxies)
        self.toggle_proxies_btn.pack(side=ctk.LEFT, padx=5)

        self.proxy_status = ctk.CTkLabel(control_frame, text="Proxies: Disabled", text_color="red")
        self.proxy_status.pack(side=ctk.LEFT, padx=5)

        self.start_stop_btn = ctk.CTkButton(control_frame, text="Start Submission", command=self.toggle_submission)
        self.start_stop_btn.pack(side=ctk.RIGHT, padx=5)

        ctk.CTkLabel(self, text="Logs").pack(pady=5)
        self.logs_text = ctk.CTkTextbox(self, height=200)
        self.logs_text.pack(fill=ctk.BOTH, expand=True, padx=20, pady=5)

        ctk.CTkButton(self, text="Download Logs", command=self.download_logs).pack(pady=10)

    def add_api_key(self):
        api_key = self.api_key_entry.get().strip()
        if api_key and api_key not in self.api_keys:
            self.api_keys.append(api_key)
            self.update_api_keys_list()
            self.api_key_entry.delete(0, ctk.END)
            self.save_api_keys()
            self.log_message(f"New API Key added: {api_key[:10]}...")
            if self.is_running:
                self.log_message('Restarting submission process to include new API key...')
                self.stop_submission()
                self.start_submission()
        else:
            self.log_message('This API key has already been added.')

    def remove_api_key(self):
        selection = self.api_keys_listbox.curselection()
        if selection:
            index = selection[0]
            removed_key = self.api_keys.pop(index)
            self.update_api_keys_list()
            self.save_api_keys()
            self.log_message(f"Removed API Key: {removed_key[:10]}...")
            if len(self.api_keys) > 0 and self.is_running:
                self.stop_submission()
                self.start_submission()
            elif self.is_running:
                self.log_message("No API keys left. Submission stopped.")
                self.stop_submission()

    def update_api_keys_list(self):
        self.api_keys_listbox.delete(0, tk.END)
        for key in self.api_keys:
            self.api_keys_listbox.insert(tk.END, f"{key[:10]}...")

    def upload_proxies(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.proxy_file_path.set(file_path)
            with open(file_path, 'r') as file:
                self.proxies = [line.strip() for line in file if line.strip()]
            self.save_proxies()
            self.log_message(f"Uploaded {len(self.proxies)} proxies.")

    def toggle_proxies(self):
        if not self.use_proxies and not self.proxies:
            messagebox.showwarning("No Proxies", "Please upload proxies before enabling.")
            return

        self.use_proxies = not self.use_proxies
        if self.use_proxies:
            self.toggle_proxies_btn.configure(text="Disable Proxies")
            self.proxy_status.configure(text="Proxies: Enabled", text_color="green")
        else:
            self.toggle_proxies_btn.configure(text="Enable Proxies")
            self.proxy_status.configure(text="Proxies: Disabled", text_color="red")
        
        self.log_message(f"Proxy usage {'enabled' if self.use_proxies else 'disabled'}.")
        if self.is_running:
            self.log_message(f"Restarting submission to update proxy settings...")
            self.stop_submission()
            self.start_submission()

    def toggle_submission(self):
        if not self.is_running:
            if not self.api_keys:
                messagebox.showwarning("No API Keys", "Please add at least one API key before starting.")
                return
            self.start_submission()
        else:
            self.stop_submission()

    def start_submission(self):
        self.is_running = True
        self.stop_requested = False
        self.start_stop_btn.configure(text="Stop Submission")
        self.log_message("Starting submission process...")
        
        for api_key in self.api_keys:
            threading.Thread(target=self.submit_guesses, args=(api_key, 60), daemon=True).start()

    def stop_submission(self):
        self.stop_requested = True
        self.is_running = False
        self.start_stop_btn.configure(text="Start Submission")
        self.log_message("Stopping submission. Please wait for the current cycle to complete.")

    def submit_guesses(self, api_key, sleep_time):
        attempt_count = 0
        while not self.stop_requested:
            attempt_count += 1
            passwords = [Mnemonic().phrase for _ in range(50)]
            proxy = random.choice(self.proxies) if self.use_proxies and self.proxies else None
            
            self.log_message(f"🔑 API Key: {api_key[:10]}... | Submission: {attempt_count} | Sleep: {sleep_time}s{' | Proxy: ' + proxy if proxy else ''}")
            self.log_message(f"➡ Submitting {len(passwords)} guesses to oracle")

            start_time = time.time()
            try:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                if self.use_proxies and proxy:
                    headers['X-Forwarded-For'] = proxy

                response = requests.post(
                    "https://api.erwin.lol/submit_guesses",
                    headers=headers,
                    json=passwords,
                    timeout=30
                )
                request_time = time.time() - start_time

                if response.status_code == 202:
                    self.log_message(f"✅ Guesses accepted | API Key: {api_key[:10]}... | Time: {request_time:.2f}s")
                    sleep_time = max(1, sleep_time - 1)
                else:
                    self.log_message(f"❌ Guesses rejected | API Key: {api_key[:10]}... | Status: {response.status_code} | Response: {response.text} | Time: {request_time:.2f}s")
                    sleep_time += 10
            except Exception as error:
                self.log_message(f"⚠️ Request error | API Key: {api_key[:10]}... | Error: {str(error)}")
                sleep_time += 10

            if self.stop_requested:
                break

            self.log_message(f"💤 Sleeping for {sleep_time}s | API Key: {api_key[:10]}...")
            time.sleep(sleep_time)

    def log_message(self, message):
        self.logs_text.insert(ctk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.logs_text.see(ctk.END)
        print(message)

    def download_logs(self):
        logs = self.logs_text.get("1.0", ctk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(logs)
                self.log_message(f"Logs downloaded to {file_path}")
            except Exception as e:
                self.log_message(f"Error saving logs: {str(e)}")
                messagebox.showerror("Error", f"Failed to save logs: {str(e)}")

    def save_api_keys(self):
        with open('api_keys.json', 'w') as file:
            json.dump(self.api_keys, file)

    def load_api_keys(self):
        try:
            with open('api_keys.json', 'r') as file:
                self.api_keys = json.load(file)
            self.update_api_keys_list()
            self.log_message(f"Loaded {len(self.api_keys)} API key(s) from storage.")
        except FileNotFoundError:
            pass

    def save_proxies(self):
        with open('proxies.json', 'w') as file:
            json.dump(self.proxies, file)

    def load_proxies(self):
        try:
            with open('proxies.json', 'r') as file:
                self.proxies = json.load(file)
            self.log_message(f"Loaded {len(self.proxies)} proxy(ies) from storage.")
        except FileNotFoundError:
            pass
    
    def setup_tray(self):
        if self.icon is None:
            try:
                icon_path = resource_path("erwin.ico")
                image = Image.open(icon_path)
                menu = (item('Show', self.show_window), item('Exit', self.quit_window))
                self.icon = pystray.Icon("name", image, "Erwin Submission GUI", menu)
                self.icon.run_detached()
            except Exception as e:
                print(f"Error setting up tray icon: {e}")

    def show_window(self):
        self.deiconify()
        if self.icon:
            self.icon.stop()
            self.icon = None

    def quit_window(self):
        if self.icon:
            self.icon.stop()
        self.quit()

    def withdraw_window(self):
        self.withdraw()
        self.setup_tray()

if __name__ == "__main__":
    app = ErwinGUI()
    app.mainloop()
    if hasattr(app, 'icon') and app.icon:
        app.icon.stop()
