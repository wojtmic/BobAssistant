import customtkinter as tk
import json
import keyboard

# Initial Setup
with open("config.json", "r") as file:
    config = json.load(file)

# Functions
def set_topbar(text):
    topbar.config(text=text)

def ui_print(text):
    result_text.configure(state=tk.NORMAL)
    result_text.insert(tk.END, text + "\n")
    result_text.configure(state=tk.DISABLED)
    result_text.see(tk.END)

def button_press():
    text = entry.get()
    ui_print(text)
    entry.delete(0, tk.END)

def focus_entry():
    entry.focus_set()

# Keyboard Bindings
keyboard.add_hotkey("enter", button_press)
keyboard.add_hotkey("ctrl+space", focus_entry)

# UI Elements
root = tk.CTk()
root.title("Bob Assistant")
root.geometry("600x400")
root.resizable(False, False)

top_bar = tk.CTkFrame(root, width=600, height=30)
top_bar.place(x=0, y=0)

topbar = tk.CTkLabel(top_bar, text="Intialising Topbar...", font=("Helvetica", 12))
topbar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

result_text = tk.CTkTextbox(root, width=575, height=325, state=tk.DISABLED)
result_text.place(x=10, y=35)

entry = tk.CTkEntry(root, width=530)
entry.place(x=20, y=365)

button = tk.CTkButton(root, text=" > ", width=3, command=button_press)
button.place(x=560, y=365)

root.mainloop()
