# C:\Users\georg\Projects\CalibriOffice\launcher.py

import customtkinter as ctk
import subprocess
import os
import sys
import traceback

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ERROR_CODES = {
    "E005": "File not found",
    "E004": "Unknown error",
}

def handle_error(error_code, detail=None):
    msg = ERROR_CODES.get(error_code, "Error")
    if detail:
        msg += f"\n\n{detail}"
    error_window = ctk.CTkToplevel()
    error_window.title(f"Error {error_code}")
    error_window.geometry("450x250")
    error_window.resizable(False, False)
    ctk.CTkLabel(error_window, text="⚠️", font=("Arial", 48)).pack(pady=(20, 5))
    ctk.CTkLabel(error_window, text=f"Error code: {error_code}", font=("Arial", 14, "bold"), text_color="red").pack()
    ctk.CTkLabel(error_window, text=msg, wraplength=400).pack(pady=10)
    ctk.CTkButton(error_window, text="Close", command=error_window.destroy).pack(pady=10)
    error_window.grab_set()

class KalibriLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KalibriOffice Launcher")
        self.geometry("500x600")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="📁 KalibriOffice", font=("Arial", 30, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Your personal office suite", font=("Arial", 14), text_color="gray70").pack(pady=(0, 20))

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.btn_word = ctk.CTkButton(self.frame, text="📄 KalibriWord", command=self.open_word, height=45, font=("Arial", 16))
        self.btn_word.pack(pady=8, padx=20, fill="x")

        self.btn_excel = ctk.CTkButton(self.frame, text="📊 KalibriTable", command=self.open_excel, height=45, font=("Arial", 16))
        self.btn_excel.pack(pady=8, padx=20, fill="x")

        self.btn_show = ctk.CTkButton(self.frame, text="🎨 KalibriShow", command=self.open_show, height=45, font=("Arial", 16))
        self.btn_show.pack(pady=8, padx=20, fill="x")

        self.btn_console = ctk.CTkButton(self.frame, text="🖥️ KalibriConsole", command=self.open_console, height=45, font=("Arial", 16))
        self.btn_console.pack(pady=8, padx=20, fill="x")

        self.btn_pybash = ctk.CTkButton(
            self.frame,
            text="🐍 PyBash (RU)",
            command=self.open_pybash,
            height=45,
            font=("Arial", 16)
        )
        self.btn_pybash.pack(pady=8, padx=20, fill="x")

        ctk.CTkButton(self, text="Exit", command=self.destroy, fg_color="gray30", width=120, height=40).pack(pady=20)

        print("🚀 KalibriOffice Launcher started")
        print("📁 Path:", os.getcwd())

    def check_file(self, filename):
        if not os.path.exists(filename):
            handle_error("E005", f"File '{filename}' not found.\nPath: {os.getcwd()}")
            return False
        return True

    def open_word(self):
        target = os.path.join("res", "word.py")
        if self.check_file(target):
            subprocess.Popen([sys.executable, target])
            self.destroy()

    def open_excel(self):
        target = os.path.join("res", "excel.py")
        if self.check_file(target):
            subprocess.Popen([sys.executable, target])
            self.destroy()

    def open_show(self):
        target = os.path.join("res", "show.py")
        if self.check_file(target):
            subprocess.Popen([sys.executable, target])
            self.destroy()

    def open_console(self):
        target = os.path.join("res", "console.py")
        if self.check_file(target):
            subprocess.Popen([sys.executable, target])
            self.destroy()

    def open_pybash(self):
        warning = ctk.CTkToplevel(self)
        warning.title("Warning")
        warning.geometry("450x200")
        warning.resizable(False, False)
        warning.grab_set()

        ctk.CTkLabel(warning, text="⚠️", font=("Arial", 48)).pack(pady=(20, 5))
        ctk.CTkLabel(
            warning,
            text="PyBash is a Russian-language command interpreter.\n"
                 "All messages and commands will be in Russian.\n\n"
                 "Do you want to continue?",
            font=("Arial", 14),
            wraplength=400
        ).pack(pady=10)

        btn_frame = ctk.CTkFrame(warning, fg_color="transparent")
        btn_frame.pack(pady=10)

        def proceed():
            warning.destroy()
            target = os.path.join("res", "pybash.py")
            if self.check_file(target):
                subprocess.Popen([sys.executable, target])
                self.destroy()

        ctk.CTkButton(btn_frame, text="Yes, continue", command=proceed, width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=warning.destroy, width=120, fg_color="gray30").pack(side="left", padx=10)

if __name__ == "__main__":
    try:
        app = KalibriLauncher()
        app.mainloop()
    except Exception as e:
        handle_error("E004", str(e))