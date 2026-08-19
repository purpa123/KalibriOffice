import tkinter as tk

root = tk.Tk()
root.title("Тест ввода")
root.geometry("400x200")

label = tk.Label(root, text="Введите текст и нажмите Enter")
label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10)

def show_text(event=None):
    print("Вы ввели:", entry.get())

entry.bind("<Return>", show_text)

root.mainloop()