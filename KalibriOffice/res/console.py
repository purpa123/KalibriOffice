# C:\Users\georg\Projects\CalibriOffice\res\console.py

import customtkinter as ctk
import sys
import os
import io
import json
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Цвета радуги
RAINBOW_COLORS = [
    '#FF0000', '#FF7F00', '#FFFF00', '#00FF00',
    '#0000FF', '#4B0082', '#8B00FF'
]

class KalibriConsole(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KalibriConsole")
        self.geometry("950x680")
        self.minsize(600, 450)

        self.history = []
        self.history_index = -1
        self.aliases = {}
        self.history_file = os.path.join(os.getcwd(), "console_history.json")

        self.create_widgets()
        self.configure_tags()
        self.load_history()
        self.print_header()

        print("🖥️ KalibriConsole (customtkinter) запущен")

    def create_widgets(self):
        # Область вывода
        self.output_area = ctk.CTkTextbox(self, wrap="word", font=("Consolas", 13), state="normal")
        self.output_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.output_area.configure(state="disabled")

        # Строка ввода
        input_frame = ctk.CTkFrame(self, height=40)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.prompt_label = ctk.CTkLabel(input_frame, text=">>> ", font=("Consolas", 14, "bold"), width=40)
        self.prompt_label.pack(side="left", padx=(5, 0))

        self.input_entry = ctk.CTkEntry(input_frame, font=("Consolas", 14), height=35)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.input_entry.bind("<Return>", self.execute_command)
        self.input_entry.bind("<Up>", self.history_up)
        self.input_entry.bind("<Down>", self.history_down)
        self.input_entry.focus_set()

        self.send_button = ctk.CTkButton(input_frame, text="Выполнить", command=self.execute_command_from_button, width=80)
        self.send_button.pack(side="right", padx=5)

        # Статус-бар
        status_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.status_label = ctk.CTkLabel(status_frame, text="KalibriConsole | Готов", font=("Consolas", 11), text_color="gray60")
        self.status_label.pack(side="left")

        ctk.CTkButton(status_frame, text="Очистить", command=self.clear_output, width=80, height=25, fg_color="gray30").pack(side="right", padx=5)

    def configure_tags(self):
        """Настраивает цветовые теги для вывода"""
        text_widget = self.output_area._textbox
        colors = {
            'white': '#ffffff', 'red': '#ff4444', 'green': '#44ff44',
            'blue': '#4444ff', 'yellow': '#ffff44', 'orange': '#ff8800',
            'purple': '#aa44ff', 'cyan': '#44ffff', 'magenta': '#ff44ff',
            'gray': '#888888', 'lightblue': '#88ccff'
        }
        for name, hex_color in colors.items():
            text_widget.tag_config(name, foreground=hex_color)

        for i, hex_color in enumerate(RAINBOW_COLORS):
            text_widget.tag_config(f"rainbow_{i}", foreground=hex_color)

    # ================== ВЫВОД ==================
    def print_to_console(self, text, color="white"):
        self.output_area.configure(state="normal")
        self.output_area.insert("end", text + "\n", color)
        self.output_area.configure(state="disabled")
        self.output_area.see("end")

    def print_rainbow(self, text):
        self.output_area.configure(state="normal")
        if not text:
            text = "🌈"
        for i, char in enumerate(text):
            tag = f"rainbow_{i % len(RAINBOW_COLORS)}"
            self.output_area.insert("end", char, tag)
        self.output_area.insert("end", "\n")
        self.output_area.configure(state="disabled")
        self.output_area.see("end")

    def print_error(self, text):
        self.print_to_console(f"Ошибка: {text}", "red")

    def print_success(self, text):
        self.print_to_console(f"✓ {text}", "green")

    def print_info(self, text):
        self.print_to_console(f"ℹ {text}", "yellow")

    def clear_output(self):
        self.output_area.configure(state="normal")
        self.output_area.delete("1.0", "end")
        self.output_area.configure(state="disabled")
        self.print_header()

    def print_header(self):
        header = """
╔═══════════════════════════════════════════════════════════════╗
║                    KalibriConsole (customtkinter)            ║
║          Встроенный терминал + res// + перехват вывода       ║
╚═══════════════════════════════════════════════════════════════╝
"""
        self.print_to_console(header, "cyan")
        self.print_to_console("Введите help или res//help", "green")

    # ================== ИСТОРИЯ ==================
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.history_index = len(self.history)
            except:
                pass

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except:
            pass

    # ================== ВВОД КОМАНД ==================
    def execute_command_from_button(self):
        cmd = self.input_entry.get()
        self.input_entry.delete(0, "end")
        self.process_command(cmd)

    def execute_command(self, event=None):
        cmd = self.input_entry.get()
        self.input_entry.delete(0, "end")
        self.process_command(cmd)

    def process_command(self, cmd):
        if not cmd.strip():
            return
        self.history.append(cmd)
        self.history_index = len(self.history)
        self.save_history()
        self.print_to_console(f">>> {cmd}", "lightblue")

        # Алиасы
        parts = cmd.split()
        if parts and parts[0] in self.aliases:
            alias_cmd = self.aliases[parts[0]]
            cmd = alias_cmd + " " + " ".join(parts[1:]) if len(parts) > 1 else alias_cmd
            self.print_to_console(f"  -> {cmd}", "gray")

        # res//
        if cmd.strip().startswith("res//"):
            self.process_res_command(cmd)
            return

        # Встроенные команды
        if cmd == "help":
            self.cmd_help()
        elif cmd == "clear":
            self.clear_output()
        elif cmd.startswith("echo "):
            self.print_to_console(cmd[5:], "white")
        elif cmd in ("exit", "quit"):
            self.destroy()
        elif cmd.startswith("cd "):
            self.cmd_cd(cmd)
        elif cmd in ("ls", "dir"):
            self.cmd_ls()
        elif cmd.startswith("python "):
            self.cmd_python(cmd)
        elif cmd.startswith("run "):
            self.cmd_run(cmd)
        elif cmd.startswith("alias "):
            self.cmd_alias(cmd)
        elif cmd == "history":
            self.cmd_history()
        else:
            self.execute_python(cmd)

    # ================== ВЫПОЛНЕНИЕ PYTHON С ПЕРЕХВАТОМ ВЫВОДА ==================
    def execute_python(self, code):
        # Перенаправляем stdout/stderr в буферы
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer

        try:
            exec(code, globals(), locals())
        except Exception as e:
            stderr_buffer.write(str(e) + "\n")

        # Восстанавливаем stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        # Получаем вывод
        out = stdout_buffer.getvalue()
        err = stderr_buffer.getvalue()

        if out:
            self.print_to_console(out, "white")
        if err:
            self.print_error(err)
        if not out and not err:
            self.print_success("Код выполнен (без вывода)")

    # ================== КОМАНДЫ res// ==================
    def process_res_command(self, cmd):
        cmd = cmd[5:].strip()
        if not cmd:
            self.print_error("Команда не указана. Используйте res//help")
            return
        parts = cmd.split()
        main_cmd = parts[0].lower()
        args = parts[1:]

        if main_cmd == "help":
            self.cmd_res_help()
        elif main_cmd == "close":
            self.destroy()
        elif main_cmd == "clear":
            self.clear_output()
        elif main_cmd == "info":
            self.cmd_res_info()
        elif main_cmd == "exec":
            if args:
                self.execute_python(" ".join(args))
            else:
                self.print_error("Укажите код: res//exec print(2+2)")
        elif main_cmd == "run":
            if args:
                self.cmd_run("run " + args[0])
            else:
                self.print_error("Укажите файл: res//run script.py")
        elif main_cmd == "cd":
            if args:
                self.cmd_cd("cd " + args[0])
            else:
                self.cmd_cd("cd")
        elif main_cmd == "ls":
            self.cmd_ls()
        elif main_cmd == "history":
            self.cmd_history()
        elif main_cmd == "save":
            self.cmd_save_history()
        elif main_cmd == "load":
            self.cmd_load_history()
        elif main_cmd == "alias":
            if args:
                self.cmd_alias("alias " + " ".join(args))
            else:
                self.print_error("Укажите алиас: res//alias mycmd=print")
        elif main_cmd == "rainbow":
            self.print_rainbow(" ".join(args) if args else "🌈 Радуга!")
        else:
            self.print_error(f"Неизвестная res// команда: {main_cmd}")

    def cmd_res_help(self):
        help_text = """
Команды res//:
  res//help           - эта справка
  res//close          - закрыть консоль
  res//clear          - очистить экран
  res//info           - информация о системе
  res//exec <код>     - выполнить Python-код
  res//run <файл>     - запустить скрипт
  res//cd <путь>      - сменить папку
  res//ls             - список файлов
  res//history        - история команд
  res//save           - сохранить историю
  res//load           - загрузить историю
  res//alias <имя>=<код> - алиас
  res//rainbow <текст> - радужный вывод
        """
        self.print_to_console(help_text, "green")

    def cmd_res_info(self):
        info = f"""
Система:
  ОС: {sys.platform}
  Python: {sys.version}
  Папка: {os.getcwd()}
  История: {len(self.history)} записей
  Алиасы: {len(self.aliases)}
        """
        self.print_to_console(info, "cyan")

    # ================== ОСТАЛЬНЫЕ КОМАНДЫ ==================
    def cmd_help(self):
        help_text = """
Доступные команды:
  help                - справка
  clear               - очистить экран
  echo <текст>        - вывести текст
  exit, quit          - закрыть консоль
  cd <папка>          - сменить папку
  ls, dir             - список файлов
  python <код>        - выполнить Python-код
  run <файл.py>       - запустить скрипт
  alias <имя>=<код>   - создать алиас
  history             - история команд
  res//help           - справка по res//
        """
        self.print_to_console(help_text, "green")

    def cmd_cd(self, cmd):
        parts = cmd.split()
        if len(parts) < 2:
            try:
                os.chdir(os.path.expanduser("~"))
                self.print_success(f"Папка: {os.getcwd()}")
            except Exception as e:
                self.print_error(str(e))
        else:
            try:
                os.chdir(parts[1])
                self.print_success(f"Папка: {os.getcwd()}")
            except Exception as e:
                self.print_error(str(e))

    def cmd_ls(self):
        try:
            files = os.listdir(".")
            if not files:
                self.print_info("Папка пуста")
                return
            files.sort()
            for f in files:
                icon = "📁" if os.path.isdir(f) else "📄"
                self.print_to_console(f"  {icon} {f}", "white")
        except Exception as e:
            self.print_error(str(e))

    def cmd_python(self, cmd):
        code = cmd[7:].strip()
        if not code:
            self.print_error("Укажите код: python print(2+2)")
            return
        self.execute_python(code)

    def cmd_run(self, cmd):
        parts = cmd.split()
        if len(parts) < 2:
            self.print_error("Укажите файл: run script.py")
            return
        filename = parts[1]
        try:
            if not os.path.exists(filename):
                self.print_error(f"Файл '{filename}' не найден")
                return
            self.print_info(f"Запуск {filename}...")
            result = subprocess.run([sys.executable, filename], capture_output=True, text=True)
            if result.stdout:
                self.print_to_console(result.stdout, "white")
            if result.stderr:
                self.print_error(result.stderr)
            if result.returncode == 0:
                self.print_success("Выполнено успешно")
            else:
                self.print_error(f"Ошибка (код {result.returncode})")
        except Exception as e:
            self.print_error(str(e))

    def cmd_alias(self, cmd):
        parts = cmd.split("=", 1)
        if len(parts) < 2:
            self.print_error("Формат: alias имя=команда")
            return
        name = parts[0].strip()
        if name.startswith("alias "):
            name = name[6:].strip()
        alias_cmd = parts[1].strip()
        if not name or not alias_cmd:
            self.print_error("Имя и команда не могут быть пустыми")
            return
        self.aliases[name] = alias_cmd
        self.print_success(f"Алиас '{name}' -> '{alias_cmd}' создан")

    def cmd_history(self):
        if not self.history:
            self.print_info("История пуста")
            return
        self.print_to_console("История команд:", "yellow")
        for i, cmd in enumerate(self.history, 1):
            self.print_to_console(f"  {i}: {cmd}", "white")

    def cmd_save_history(self):
        self.save_history()
        self.print_success("История сохранена")

    def cmd_load_history(self):
        self.load_history()
        self.print_success("История загружена")

    # ================== ИСТОРИЯ (СТРЕЛКИ) ==================
    def history_up(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_index])

    def history_down(self, event):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.input_entry.delete(0, "end")

if __name__ == "__main__":
    app = KalibriConsole()
    app.mainloop()