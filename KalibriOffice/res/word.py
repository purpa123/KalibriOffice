# C:\Users\georg\Projects\CalibriOffice\res\word.py

import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import os
import sys

# ================== ПОДДЕРЖКА ИЗОБРАЖЕНИЙ ==================
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Для изображений установи: pip install Pillow")

# ================== НАСТРОЙКА ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONTS = ["Arial", "Consolas", "Courier New", "Georgia", "Helvetica", "Impact", "Roboto", "Segoe UI", "Times New Roman", "Verdana"]
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]

class TabData:
    def __init__(self, text_widget, file_path=None):
        self.text_widget = text_widget
        self.file_path = file_path
        self.image_refs = []

class KalibriWord(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KalibriOffice — KalibriWord")
        self.geometry("1100x750")
        self.minsize(800, 500)

        self.current_font = "Consolas"
        self.current_size = 14
        self.tabs_data = {}
        self.active_tab = None

        self.create_menu()
        self.create_tab_view()
        self.create_status_bar()

        self.add_new_tab()

        # ===== ГОРЯЧИЕ КЛАВИШИ =====
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-Shift-S>", lambda e: self.save_as_file())
        self.bind_all("<Control-w>", lambda e: self.close_current_tab())
        self.bind_all("<Control-f>", lambda e: self.open_search_dialog())

        # ===== ФОРМАТИРОВАНИЕ: Жирный, Курсив, Подчёркнутый =====
        self.bind_all("<Control-b>", lambda e: self.apply_bold())
        self.bind_all("<Control-i>", lambda e: self.apply_italic())
        self.bind_all("<Control-u>", lambda e: self.apply_underline())

        # ===== КОМАНДЫ: Ctrl+U+N =====
        self.bind_all("<Control-u><Control-n>", self.execute_command)
        self.bind_all("<Control-Shift-n>", self.execute_command)

        # ===== СИСТЕМА КОМАНД =====
        self.commands = {
            "res//close": self.cmd_close_app,
            "res//save": self.cmd_save_all,
            "res//new": self.cmd_new_tab,
            "res//dark": self.cmd_dark_theme,
            "res//light": self.cmd_light_theme,
            "res//info": self.cmd_show_info,
            "res//clear": self.cmd_clear_all,
            "res//font": self.cmd_change_font,
            "res//size": self.cmd_change_size,
            "res//exit": self.cmd_force_exit,
            "res//wordcount": self.cmd_show_wordcount,
            "res//closeall": self.cmd_close_all_tabs,
        }

        print("📄 KalibriWord с форматированием запущен")
        print("🔧 Ctrl+B — жирный, Ctrl+I — курсив, Ctrl+U — подчёркнутый")

    # ================== МЕНЮ ==================
    def create_menu(self):
        menu_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        menu_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Кнопки файлов
        ctk.CTkButton(menu_frame, text="📄 Новая вкладка", command=self.add_new_tab, width=130).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="📂 Открыть", command=self.open_file, width=80).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="💾 Сохранить", command=self.save_file, width=80).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="📁 Сохранить как", command=self.save_as_file, width=110).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="🖼️ Вставить изображение", command=self.insert_image, width=160).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="❌ Закрыть вкладку", command=self.close_current_tab, width=120).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="🔍 Поиск", command=self.open_search_dialog, width=80).pack(side="left", padx=2)

        # Разделитель
        ctk.CTkLabel(menu_frame, text="|", font=("Arial", 18)).pack(side="left", padx=5)

        # Кнопки форматирования
        ctk.CTkButton(menu_frame, text="B", command=self.apply_bold, width=30, font=("Arial", 14, "bold")).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="I", command=self.apply_italic, width=30, font=("Arial", 14, "italic")).pack(side="left", padx=2)
        ctk.CTkButton(menu_frame, text="U", command=self.apply_underline, width=30, font=("Arial", 14, "underline")).pack(side="left", padx=2)

        # Шрифт и размер
        self.font_var = ctk.StringVar(value=self.current_font)
        self.font_menu = ctk.CTkOptionMenu(menu_frame, values=FONTS, variable=self.font_var, command=self.change_font, width=130)
        self.font_menu.pack(side="left", padx=2)

        self.size_var = ctk.StringVar(value=str(self.current_size))
        self.size_menu = ctk.CTkOptionMenu(menu_frame, values=[str(s) for s in FONT_SIZES], variable=self.size_var, command=self.change_size, width=70)
        self.size_menu.pack(side="left", padx=2)

        self.label_info = ctk.CTkLabel(menu_frame, text="Вкладок: 1")
        self.label_info.pack(side="right", padx=10)

    # ================== ВКЛАДКИ ==================
    def create_tab_view(self):
        self.tab_view = ctk.CTkTabview(self, width=900, height=500)
        self.tab_view.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        self.tab_view._segmented_button.configure(command=self.on_tab_changed)

    def on_tab_changed(self, tab_id=None):
        self.active_tab = tab_id
        if tab_id and tab_id in self.tabs_data:
            self.update_word_count()
            data = self.tabs_data[tab_id]
            if data.file_path:
                name = os.path.basename(data.file_path)
                self.label_info.configure(text=f"{name} (вкладок: {len(self.tabs_data)})")
            else:
                self.label_info.configure(text=f"Без названия (вкладок: {len(self.tabs_data)})")
            self.apply_font()

    def get_active_text(self):
        if self.active_tab and self.active_tab in self.tabs_data:
            return self.tabs_data[self.active_tab].text_widget
        return None

    def get_active_file(self):
        if self.active_tab and self.active_tab in self.tabs_data:
            return self.tabs_data[self.active_tab].file_path
        return None

    def set_active_file(self, path):
        if self.active_tab and self.active_tab in self.tabs_data:
            self.tabs_data[self.active_tab].file_path = path
            self.on_tab_changed(self.active_tab)

    def add_new_tab(self, file_path=None, content=""):
        tab_name = f"Документ {len(self.tabs_data) + 1}"
        self.tab_view.add(tab_name)
        text_widget = ctk.CTkTextbox(
            self.tab_view.tab(tab_name),
            wrap="word",
            font=(self.current_font, self.current_size),
            height=500
        )
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        text_widget.insert("1.0", content if content else f"Новый документ {len(self.tabs_data) + 1}")
        text_widget.bind("<KeyRelease>", lambda e: self.update_word_count())
        text_widget.bind("<ButtonRelease-1>", lambda e: self.update_word_count())

        # Привязываем ПКМ для удаления изображения
        text_widget._textbox.bind("<Button-3>", self.show_image_context_menu)

        self.tabs_data[tab_name] = TabData(text_widget, file_path)
        self.tab_view.set(tab_name)
        self.active_tab = tab_name

        self.update_word_count()
        self.label_info.configure(text=f"Вкладок: {len(self.tabs_data)}")
        print(f"📄 Создана новая вкладка: {tab_name}")
        return tab_name

    def close_current_tab(self):
        if len(self.tabs_data) <= 1:
            messagebox.showinfo("KalibriWord", "Нельзя закрыть последнюю вкладку.")
            return
        if not self.active_tab:
            return

        text_widget = self.get_active_text()
        if text_widget and text_widget.get("1.0", "end-1c").strip():
            if not messagebox.askyesno("KalibriWord", "Сохранить изменения перед закрытием?"):
                pass

        self.tab_view.delete(self.active_tab)
        del self.tabs_data[self.active_tab]
        self.active_tab = None

        if self.tabs_data:
            first_tab = list(self.tabs_data.keys())[0]
            self.tab_view.set(first_tab)
            self.active_tab = first_tab
            self.on_tab_changed(first_tab)

        self.label_info.configure(text=f"Вкладок: {len(self.tabs_data)}")
        print("❌ Закрыта вкладка")

    def cmd_close_all_tabs(self):
        if len(self.tabs_data) <= 1:
            messagebox.showinfo("KalibriWord", "Уже только одна вкладка.")
            return

        if messagebox.askyesno("KalibriWord", f"Закрыть все {len(self.tabs_data)-1} вкладки?"):
            while len(self.tabs_data) > 1:
                for tab in list(self.tabs_data.keys()):
                    if tab != self.active_tab:
                        self.tab_view.delete(tab)
                        del self.tabs_data[tab]
                        break
            self.label_info.configure(text=f"Вкладок: {len(self.tabs_data)}")
            print("🔧 Команда: закрыты все вкладки")

    # ================== СТАТУС-БАР ==================
    def create_status_bar(self):
        status_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.word_count_label = ctk.CTkLabel(status_frame, text="Слов: 0 | Символов: 0", font=("Consolas", 12), text_color="gray60")
        self.word_count_label.pack(side="left")

        ctk.CTkLabel(status_frame, text="KalibriWord v0.7", font=("Consolas", 12), text_color="gray40").pack(side="right")

    def update_word_count(self):
        text_widget = self.get_active_text()
        if text_widget:
            content = text_widget.get("1.0", "end-1c")
            words = len(content.split()) if content.strip() else 0
            chars = len(content)
            self.word_count_label.configure(text=f"Слов: {words} | Символов: {chars}")

    def cmd_show_wordcount(self):
        text_widget = self.get_active_text()
        if text_widget:
            content = text_widget.get("1.0", "end-1c")
            words = len(content.split()) if content.strip() else 0
            chars = len(content)
            lines = len(content.split("\n"))
            messagebox.showinfo("Статистика", f"Слов: {words}\nСимволов: {chars}\nСтрок: {lines}")

    # ================== ФОРМАТИРОВАНИЕ ==================
    def apply_bold(self):
        """Применяет/убирает жирный стиль к выделенному тексту"""
        self._apply_tag("bold", ("Arial", self.current_size, "bold"))

    def apply_italic(self):
        """Применяет/убирает курсив к выделенному тексту"""
        self._apply_tag("italic", ("Arial", self.current_size, "italic"))

    def apply_underline(self):
        """Применяет/убирает подчёркивание к выделенному тексту"""
        self._apply_tag("underline", ("Arial", self.current_size, "underline"))

    def _apply_tag(self, tag_name, font_spec):
        """Общая функция для применения тега к выделенному тексту"""
        text_widget = self.get_active_text()
        if not text_widget:
            return

        try:
            # Получаем выделение
            sel_start = text_widget._textbox.index("sel.first")
            sel_end = text_widget._textbox.index("sel.last")
        except:
            # Нет выделения – ничего не делаем
            return

        # Проверяем, есть ли уже такой тег у выделения
        tags = text_widget._textbox.tag_names(sel_start)
        if tag_name in tags:
            # Если есть – убираем
            text_widget._textbox.tag_remove(tag_name, sel_start, sel_end)
        else:
            # Если нет – добавляем
            text_widget._textbox.tag_add(tag_name, sel_start, sel_end)
            # Настраиваем внешний вид тега
            text_widget._textbox.tag_config(tag_name, font=font_spec)

        # Обновляем счётчик (для перерисовки)
        self.update_word_count()

    # ================== ШРИФТЫ ==================
    def change_font(self, choice):
        self.current_font = choice
        self.apply_font()

    def change_size(self, choice):
        self.current_size = int(choice)
        self.apply_font()

    def apply_font(self):
        text_widget = self.get_active_text()
        if text_widget:
            text_widget.configure(font=(self.current_font, self.current_size))
            # Устанавливаем базовый тег "default"
            text_widget.tag_configure("default", font=(self.current_font, self.current_size))
            text_widget.tag_add("default", "1.0", "end")
            self.size_var.set(str(self.current_size))
            self.font_var.set(self.current_font)

    # ================== ОТКРЫТИЕ / СОХРАНЕНИЕ ==================
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Документы Word", "*.docx"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.add_new_tab(file_path=file_path, content=content)
            self.apply_font()
            self.update_word_count()
            print(f"📂 Открыт: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        file_path = self.get_active_file()
        if file_path:
            self._save_to_file(file_path)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Документы Word", "*.docx"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return
        self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        text_widget = self.get_active_text()
        if not text_widget:
            return

        try:
            content = text_widget.get("1.0", "end-1c")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.set_active_file(file_path)
            self.on_tab_changed(self.active_tab)
            print(f"💾 Сохранён: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")

    # ================== ИЗОБРАЖЕНИЯ ==================
    def insert_image(self):
        if not PIL_AVAILABLE:
            messagebox.showerror("Ошибка", "Pillow не установлена.\nУстанови: pip install Pillow")
            return

        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if not file_path:
            return

        text_widget = self.get_active_text()
        if not text_widget:
            return

        try:
            image = Image.open(file_path)
            max_width = 400
            if image.width > max_width:
                ratio = max_width / image.width
                new_size = (max_width, int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            text_widget._textbox.image_create("insert", image=photo)
            text_widget._textbox.insert("insert", "\n")

            data = self.tabs_data.get(self.active_tab)
            if data:
                data.image_refs.append(photo)

            self.update_word_count()
            print(f"🖼️ Вставлено: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить изображение:\n{str(e)}")

    # ================== ПКМ УДАЛИТЬ ИЗОБРАЖЕНИЕ ==================
    def show_image_context_menu(self, event):
        text_widget = self.get_active_text()
        if not text_widget:
            return

        try:
            index = text_widget._textbox.index(f"@{event.x},{event.y}")
            image_obj = text_widget._textbox.image_cget(index, "image")
            if not image_obj:
                return

            menu = Menu(self, tearoff=0)
            menu.add_command(
                label="🗑️ Удалить изображение",
                command=lambda: self.delete_image_at_index(index)
            )
            menu.add_separator()
            menu.add_command(label="Отмена", command=lambda: None)
            menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"⚠️ Ошибка ПКМ: {e}")

    def delete_image_at_index(self, index):
        text_widget = self.get_active_text()
        if text_widget:
            try:
                text_widget._textbox.delete(index)
                self.update_word_count()
                print(f"🗑️ Изображение удалено в позиции {index}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить изображение:\n{str(e)}")

    # ================== ПОИСК ==================
    def open_search_dialog(self):
        text_widget = self.get_active_text()
        if not text_widget:
            return

        search_window = ctk.CTkToplevel(self)
        search_window.title("Поиск")
        search_window.geometry("300x120")
        search_window.resizable(False, False)
        search_window.grab_set()

        ctk.CTkLabel(search_window, text="Найти:").pack(pady=(10, 0))
        entry = ctk.CTkEntry(search_window, width=250)
        entry.pack(pady=5)
        entry.focus_set()

        button_frame = ctk.CTkFrame(search_window, fg_color="transparent")
        button_frame.pack(pady=5)

        def do_search():
            query = entry.get()
            if query:
                self.find_text(query)
                search_window.destroy()

        ctk.CTkButton(button_frame, text="Найти", command=do_search, width=80).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Отмена", command=search_window.destroy, width=80).pack(side="left", padx=5)

        entry.bind("<Return>", lambda e: do_search())

    def find_text(self, query):
        text_widget = self.get_active_text()
        if not text_widget:
            return

        text_widget.tag_remove("search", "1.0", "end")

        if not query:
            return

        start = "1.0"
        self.search_results = []
        while True:
            pos = text_widget._textbox.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.search_results.append((pos, end))
            start = end

        for pos, end in self.search_results:
            text_widget.tag_add("search", pos, end)

        text_widget.tag_config("search", background="yellow", foreground="black")

        if self.search_results:
            self.search_index = 0
            pos, end = self.search_results[0]
            text_widget._textbox.mark_set("insert", pos)
            text_widget._textbox.see(pos)
            messagebox.showinfo("Поиск", f"Найдено {len(self.search_results)} совпадений")
        else:
            messagebox.showinfo("Поиск", "Текст не найден")

    # ================== СИСТЕМА КОМАНД ==================
    def execute_command(self, event=None):
        text_widget = self.get_active_text()
        if not text_widget:
            return

        content = text_widget.get("1.0", "end-1c")
        lines = content.split("\n")
        last_line = lines[-1] if lines else ""

        for command, action in self.commands.items():
            if command in last_line:
                start_idx = content.rfind(command)
                if start_idx != -1:
                    end_idx = start_idx + len(command)
                    text_widget.delete(f"1.0+{start_idx}c", f"1.0+{end_idx}c")
                    if start_idx > 0:
                        text_widget.delete(f"1.0+{start_idx-1}c", f"1.0+{start_idx}c")
                action()
                self.update_word_count()
                return

        if last_line.strip().startswith("res//"):
            messagebox.showinfo("KalibriWord", f"Неизвестная команда: {last_line.strip()}\n\nДоступные команды:\n" + "\n".join(self.commands.keys()))

    # ================== ДЕЙСТВИЯ КОМАНД ==================
    def cmd_close_app(self):
        if messagebox.askyesno("KalibriWord", "Закрыть всё приложение?"):
            self.destroy()
        print("🔧 Команда: закрыть приложение")

    def cmd_save_all(self):
        saved = 0
        for tab_name, data in self.tabs_data.items():
            if data.file_path:
                self._save_to_file(data.file_path)
                saved += 1
        messagebox.showinfo("KalibriWord", f"Сохранено вкладок: {saved}")
        print(f"🔧 Команда: сохранено {saved} вкладок")

    def cmd_new_tab(self):
        self.add_new_tab()
        print("🔧 Команда: новая вкладка")

    def cmd_dark_theme(self):
        ctk.set_appearance_mode("dark")
        messagebox.showinfo("KalibriWord", "Тёмная тема активирована")
        print("🔧 Команда: тёмная тема")

    def cmd_light_theme(self):
        ctk.set_appearance_mode("light")
        messagebox.showinfo("KalibriWord", "Светлая тема активирована")
        print("🔧 Команда: светлая тема")

    def cmd_show_info(self):
        info = f"""
📁 KalibriOffice
📄 KalibriWord v0.7
🐍 Python + CustomTkinter
📂 Вкладок: {len(self.tabs_data)}
💾 Активный файл: {self.get_active_file() or 'Не сохранён'}
📝 Символов: {len(self.get_active_text().get("1.0", "end-1c")) if self.get_active_text() else 0}
        """
        messagebox.showinfo("О KalibriWord", info)
        print("🔧 Команда: информация о проекте")

    def cmd_clear_all(self):
        text_widget = self.get_active_text()
        if text_widget and messagebox.askyesno("KalibriWord", "Очистить весь текст?"):
            text_widget.delete("1.0", "end")
            self.update_word_count()
            print("🔧 Команда: очистка текста")

    def cmd_change_font(self):
        font = ctk.CTkInputDialog(text="Введите название шрифта:", title="Сменить шрифт")
        if font.get().strip():
            self.change_font(font.get())
        print(f"🔧 Команда: шрифт изменён на {font.get()}")

    def cmd_change_size(self):
        size = ctk.CTkInputDialog(text="Введите размер шрифта (8-72):", title="Сменить размер")
        try:
            new_size = int(size.get())
            if 8 <= new_size <= 72:
                self.change_size(str(new_size))
                print(f"🔧 Команда: размер изменён на {new_size}")
            else:
                messagebox.showerror("Ошибка", "Размер должен быть от 8 до 72")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число")

    def cmd_force_exit(self):
        if messagebox.askyesno("KalibriWord", "Точно закрыть без сохранения?"):
            self.destroy()
        print("🔧 Команда: экстренное закрытие")

# ================== ЗАПУСК ==================
if __name__ == "__main__":
    app = KalibriWord()
    app.mainloop()