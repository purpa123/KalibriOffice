# C:\Users\georg\Projects\CalibriOffice\res\pybash.py

import customtkinter as ctk
import sys
import os
import io
import subprocess
import re
import shlex

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PyBashShell(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyBash Interpreter (RU)")
        self.geometry("950x680")
        self.minsize(600, 450)

        self.variables = {}
        self.history = []
        self.history_index = -1
        self.prompt = "pybash> "

        self.create_widgets()
        self.print_header()

        print("🐍 PyBash (русскоязычный интерпретатор) запущен")

    def create_widgets(self):
        # Область вывода
        self.output_area = ctk.CTkTextbox(self, wrap="word", font=("Consolas", 13), state="normal")
        self.output_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.output_area.configure(state="disabled")

        # Строка ввода
        input_frame = ctk.CTkFrame(self, height=40)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.prompt_label = ctk.CTkLabel(input_frame, text=self.prompt, font=("Consolas", 14, "bold"), width=80)
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

        self.status_label = ctk.CTkLabel(status_frame, text="PyBash | Готов", font=("Consolas", 11), text_color="gray60")
        self.status_label.pack(side="left")

        ctk.CTkButton(status_frame, text="Очистить", command=self.clear_output, width=80, height=25, fg_color="gray30").pack(side="right", padx=5)

    def print_to_console(self, text, color=None):
        self.output_area.configure(state="normal")
        if color:
            self.output_area.insert("end", text + "\n", color)
        else:
            self.output_area.insert("end", text + "\n")
        self.output_area.configure(state="disabled")
        self.output_area.see("end")

    def print_header(self):
        self.print_to_console("╔═══════════════════════════════════════════════════════════════╗", "cyan")
        self.print_to_console("║                    PyBash (Русский язык)                     ║", "cyan")
        self.print_to_console("║          Гибрид Bash и Python                               ║", "cyan")
        self.print_to_console("╚═══════════════════════════════════════════════════════════════╝", "cyan")
        self.print_to_console("Введите help для справки", "green")

    def clear_output(self):
        self.output_area.configure(state="normal")
        self.output_area.delete("1.0", "end")
        self.output_area.configure(state="disabled")
        self.print_header()

    # ================== ОСНОВНАЯ ЛОГИКА ==================
    def evaluate(self, command):
        """Выполняет команду pybash и возвращает вывод"""
        command = command.strip()
        if not command:
            return ""

        # Переменные: $name = value
        if "=" in command and not command.startswith("#"):
            parts = command.split("=", 1)
            var_name = parts[0].strip()
            value = parts[1].strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            value = self.expand_subshell(value)
            self.variables[var_name] = value
            return f"✓ {var_name} = {value}"

        # Замена переменных и подстановок
        command = self.expand_variables(command)
        command = self.expand_subshell(command)

        # Перенаправление
        redirect_stdout = None
        redirect_append = False
        if ">>" in command:
            parts = command.split(">>", 1)
            command = parts[0].strip()
            redirect_stdout = parts[1].strip()
            redirect_append = True
        elif ">" in command:
            parts = command.split(">", 1)
            command = parts[0].strip()
            redirect_stdout = parts[1].strip()

        # Конвейеры (упрощённо)
        if "|" in command:
            cmds = command.split("|")
            if len(cmds) == 2:
                cmd1 = cmds[0].strip()
                cmd2 = cmds[1].strip()
                output1 = self.execute_command(cmd1)
                cmd2_with_args = cmd2 + " " + output1.strip()
                output2 = self.execute_command(cmd2_with_args)
                result = output2
                if redirect_stdout:
                    self.write_redirect(redirect_stdout, result, redirect_append)
                    return f"Вывод сохранён в {redirect_stdout}"
                return result

        # Обычное выполнение
        output = self.execute_command(command)
        if redirect_stdout:
            self.write_redirect(redirect_stdout, output, redirect_append)
            return f"Вывод сохранён в {redirect_stdout}"
        return output

    def expand_variables(self, text):
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        def replacer(match):
            var_name = match.group(1)
            return self.variables.get(var_name, "")
        return re.sub(pattern, replacer, text)

    def expand_subshell(self, text):
        pattern = r'\$\(([^)]+)\)'
        def replacer(match):
            cmd = match.group(1)
            old_vars = self.variables.copy()
            result = self.execute_command(cmd)
            self.variables = old_vars
            return result.strip()
        return re.sub(pattern, replacer, text)

    def execute_command(self, command):
        if command.startswith("python "):
            code = command[7:].strip()
            return self.execute_python(code)
        elif self.is_python_code(command):
            return self.execute_python(command)

        # Системные команды
        if command.startswith("cd "):
            path = command[3:].strip()
            try:
                os.chdir(path)
                return f"Перешли в {os.getcwd()}"
            except Exception as e:
                return f"Ошибка: {e}"
        elif command.startswith("echo "):
            return command[5:].strip()
        elif command == "help":
            return self.help_text()
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, env=os.environ)
                if result.stdout:
                    return result.stdout.strip()
                if result.stderr:
                    return f"Ошибка: {result.stderr.strip()}"
                return ""
            except Exception as e:
                return f"Ошибка выполнения: {e}"

    def is_python_code(self, command):
        python_keywords = ['if', 'for', 'while', 'def', 'class', 'import', 'from', 'try', 'except', 'with', 'lambda', 'yield', 'global', 'nonlocal', 'return', 'raise', 'assert', 'pass', 'break', 'continue']
        for kw in python_keywords:
            if re.match(rf'^{kw}\b', command.strip()):
                return True
        if re.search(r'\(.*\)', command) and not command.startswith('cd ') and not command.startswith('ls ') and not command.startswith('echo '):
            return True
        return False

    def execute_python(self, code):
        old_stdout = sys.stdout
        stdout_buffer = io.StringIO()
        sys.stdout = stdout_buffer
        try:
            exec(code, globals(), locals())
        except Exception as e:
            print(e)
        output = stdout_buffer.getvalue()
        sys.stdout = old_stdout
        return output.strip()

    def write_redirect(self, filename, content, append=False):
        mode = 'a' if append else 'w'
        with open(filename, mode, encoding='utf-8') as f:
            f.write(content)

    def help_text(self):
        return """
Доступные команды:
  help              - эта справка
  clear             - очистить экран
  exit, quit        - выход
  echo <текст>      - вывести текст
  cd <путь>         - сменить папку
  ls, dir           - список файлов
  python <код>      - выполнить Python-код
  $var = значение   - создать переменную
  $var              - использовать переменную
  $(команда)        - подстановка вывода команды
  > файл            - перенаправить вывод в файл
  >> файл           - дописать вывод в файл
  |                 - конвейер (упрощённо)
        """

    # ================== ОБРАБОТКА ВВОДА ==================
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
        self.print_to_console(f"{self.prompt}{cmd}", "lightblue")

        if cmd.strip() in ("exit", "quit"):
            self.destroy()
            return

        if cmd.strip() == "clear":
            self.clear_output()
            return

        result = self.evaluate(cmd)
        if result:
            self.print_to_console(result, "white")

    # ================== ИСТОРИЯ ==================
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
    app = PyBashShell()
    app.mainloop()
    