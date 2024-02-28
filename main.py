import customtkinter as tk
import json
import keyboard
from openai import OpenAI
import sys
import time
import tkinter.messagebox as messagebox
import os

# Initial Setup
# os.system(remove system32) frfrfrfrfrfr
with open("config.json", "r") as file:
    config = json.load(file)

messages = []

setupMessage = ["You are a helpful assistant, your name is Bob.",
                "You are installed on the user's machine.",
                "You are a chatbot and your job is to help the user.",
                "You can run python code by separating your normal message with [CODE]. Do not use markdown, or any other formatting, nor [/CODE]. Use of codeblocks, like ``` is forbidden. You will have to import libraries inside your code, they are not preimported, except for sys, time, json and keyboard.",
                "You can use os.system() to run terminal commands, like pip (without ! before it) if the user agrees to it.",
                "Do not respond to the user's messages twice.",
                "You are free to use winget if the user asks you to install or uninstall something.",
                "Since all the code you are running is executed directly on the user's machine, you should not run any code that could be harmful to the user or their machine and if they ask you to do something, and its not malicious, do it. Do not tell them you cant, you can.",
                "You can use the os module to interact with the user's file system if they agree.",
                "Beacuse of a bug in the interpreter, you cannot use if, for, while, def, class or with statements. If you absolutly need to do it, save the file (without with) and run it using os.system(), but only if the user agrees.",
                "The user cant see the code you write, but their antivirus can.",
                "You are allowed to open and close apps, using os.system(), if the user wants you to.",
                "You always have to provide a message to the user (before [CODE]), providing just code is forbidden. You do have to type [CODE] before typing any code, as it will not run otherwise.",
                "Dont be british, be polite, but not too polite.",
                "You are not allowed to respond to the same message twice, except for the initial setup message."]

initPrompt = ""

for i in setupMessage:
    initPrompt += i + " "

print(initPrompt)
initPrompt = {"role": "system", "content": f"{initPrompt}"}
print(initPrompt)
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
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
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

topbar = tk.CTkLabel(top_bar, text="Send a message to begin.", font=("Helvetica", 12))
topbar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

result_text = tk.CTkTextbox(root, width=575, height=325, state=tk.DISABLED)
result_text.place(x=10, y=35)

entry = tk.CTkEntry(root, width=530)
entry.place(x=20, y=365)

button = tk.CTkButton(root, text=" > ", width=3, command=button_press)
button.place(x=560, y=365)

# Post-setup
try:
    client = OpenAI(api_key=config["api-key"])
except:
    set_topbar("Error: Invalid API Key")
    ui_print("Invalid or no API Key found in config.json")
    ui_print("Please add a valid API Key and restart the application")
    entry.configure(state=tk.DISABLED)  
    button.configure(state=tk.DISABLED)
    time.sleep(2)
    sys.exit()



root.mainloop()
