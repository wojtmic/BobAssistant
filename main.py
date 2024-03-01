import customtkinter as tk
import json
import keyboard
from openai import OpenAI
import tkinter.messagebox as messagebox
import sys
import time
import os

# Initial Setup
with open("config.json", "r") as file:
    config = json.load(file)

messages = []

with open("rules.txt", "r") as file:
    setupMessage = [line.strip() for line in file]

initPrompt = ""

for i in setupMessage:
    initPrompt += i + " "

initPrompt = {"role": "system", "content": f"{initPrompt}"}
messages.append(initPrompt)

# Functions
def set_topbar(text):
    topbar.configure(text=text)

def ui_print(text):
    result_text.configure(state=tk.NORMAL)
    result_text.insert(tk.END, text + "\n")
    result_text.configure(state=tk.DISABLED)
    result_text.see(tk.END)

def button_press():
    text = entry.get()
    entry.delete(0, tk.END)
    send_to_ai(text)

def focus_entry():
    entry.focus_set()

def confirm_run_code(code):
        title = "Confirmation"
        message = f"Do you want to run the following code?\n\n{code}"
        result = messagebox.askyesno(title, message)
        return result

def send_to_ai(text):
    global client
    global messages

    set_topbar("Bob is thinking...")
    entry.configure(state=tk.DISABLED)
    button.configure(state=tk.DISABLED)

    messages.append({"role": "user", "content": text})
    completion = client.chat.completions.create(model=config["model"], messages=messages)
    print(completion)
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})

    generated_text = completion.choices[0].message.content
    splitText = generated_text.split("[CODE]")

    if len(splitText) > 1:
        set_topbar("Executing code...")

        if config["enable-confirmation"] == False or confirm_run_code(splitText[1]):
            set_topbar("Executing code...")
            for c in splitText[1].split("\n"):
                if c != "":
                    try:
                        exec(c)
                    except Exception as e:
                        ui_print(f"Error: {e}")
        else:
            set_topbar("Code execution cancelled.")
    else:
        set_topbar("No code to execute.")

    ui_print(splitText[0])

    set_topbar("")
    entry.configure(state=tk.NORMAL)
    button.configure(state=tk.NORMAL)

# UI Elements
root = tk.CTk()
root.title("Bob Assistant")
root.geometry("600x400")
root.resizable(False, False)

top_bar = tk.CTkFrame(root, width=600, height=30)
top_bar.place(x=0, y=0)

topbar = tk.CTkLabel(top_bar, text="Send a message to begin.", font=("Helvetica", 12))
topbar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

result_text = tk.CTkTextbox(root, width=575, height=325, state=tk.DISABLED)
result_text.place(x=10, y=35)

entry = tk.CTkEntry(root, width=530)
entry.place(x=20, y=365)

button = tk.CTkButton(root, text=" > ", width=3, command=button_press)
button.place(x=560, y=365)

# Post-setup
client = OpenAI(api_key=config["api-key"])

root.mainloop()
