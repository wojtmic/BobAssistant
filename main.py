import customtkinter as tk
import json
import keyboard
from openai import OpenAI
import tkinter.messagebox as messagebox
import sys
import time
import os
import io
import threading
import requests
import ctypes

# Initial Setup
with open("config.json", "r") as file:
    config = json.load(file)

messages = []
chatMessages = []

if os.path.exists("rules.txt"):
    with open("rules.txt", "r") as file:
        setupMessage = [line.strip() for line in file]
else:
    setupMessage = []

initPrompt = ""

for i in setupMessage:
    initPrompt += i + " "

initPrompt = {"role": "system", "content": f"{initPrompt}"}
messages.append(initPrompt)

if os.path.exists("memory.json"):
    with open("memory.json", "r") as file:
        memory = json.load(file)

messages += memory["messages"] if "messages" in memory else []
chatMessages = memory["chatMessages"] if "chatMessages" in memory else []

# Functions
# def clear_textbox():
#     result_text.configure(state=tk.NORMAL)
#     result_text.delete(1.0, tk.END)
#     result_text.configure(state=tk.DISABLED)

def set_topbar(text):
    topbar.configure(text=text)

# def ui_print(text):
#     result_text.configure(state=tk.NORMAL)
#     result_text.insert(tk.END, text + "\n")
#     result_text.configure(state=tk.DISABLED)
#     result_text.see(tk.END)

def add_message(role, content, color="grey"):
    role = str(role)
    content = str(content)

    role = role.strip()
    content = content.strip()
    
    content = content.replace("**", "")
    content = content.replace("*", "")
    content = content.replace("```", "")

    message_frame = tk.CTkFrame(chatbox, width=550, height=50, fg_color=color)
    message_frame.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=True)

    role_label = tk.CTkLabel(message_frame, text=role, font=("Helvetica", 12, "bold"))
    role_label.grid(row=0, column=0, padx=5, sticky="nw")

    content_label = tk.CTkLabel(message_frame, text=content, font=("Helvetica", 12), wraplength=500, anchor="w", justify="left")
    content_label.grid(row=1, column=0, padx=5)

    chatbox.after(10, chatbox._parent_canvas.yview_moveto, 1.0)

def modify_message(index, content):
    chatbox.children[index].children[1].configure(text=content)

def button_press():
    text = entry.get()
    entry.delete(0, tk.END)
    send_to_ai_thread(text)
    optimize_chatbox()

def focus_entry():
    entry.focus_set()

def confirm_run_code(code,confirm=True):
        title = "Confirmation"
        if confirm:
            message = f"Do you want to run the following code?\n\n{code}"
        else:
            message = code
        result = messagebox.askyesno(title, message)
        return result

def send_to_ai(text):
    if text.strip() != "":
        global client
        global messages

        is_sudo = False

        set_topbar("Bob is thinking...")
        entry.configure(state=tk.DISABLED)
        button.configure(state=tk.DISABLED)

        if text.startswith("sudo") and confirm_run_code("Warning: By using sudo, your message will be sent to the AI as a system message and is not recommended. Are you sure you want to continue?", False):
            messages.append({"role": "system", "content": text.replace("sudo","")})
            is_sudo = True
        else:
            messages.append({"role": "user", "content": text})

        if is_sudo:
            add_message("System", text.replace("sudo",""), "#ff0000")
        else:
            add_message("You", text)

            completion = client.chat.completions.create(model=config["model"], messages=messages)
            messages.append({"role": "assistant", "content": completion.choices[0].message.content})

            generated_text = completion.choices[0].message.content
            splitText = generated_text.split("[CODE]")

            splitText[0] = splitText[0].replace("[END]","")
            add_message("Bob", splitText[0], "#1776e3")
            root.update()
            root.update_idletasks()

            if "[END]" in generated_text and False: # I'm disabling this for now, Bob is using it when he shouldn't.
                set_topbar("Goodbye!")
                time.sleep(2)
                sys.exit()

            if len(splitText) > 1:
                set_topbar("Executing code...")
                code = splitText[1]
                code = code.replace("`","")
                code = code.replace("[/CODE]","")
                if config["enable-confirmation"] == False or confirm_run_code(code):
                    set_topbar("Executing code...")
                    output = io.StringIO()
                    sys.stdout = output
                    if code.endswith("[ADMIN]"):
                        code = code.replace("[ADMIN]","")
                        if ctypes.windll.shell32.IsUserAnAdmin():
                            exec(code)
                        else:
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
                    else:
                        exec(code)
                    sys.stdout = sys.__stdout__
                    output = output.getvalue()
                    add_message("Output", output, "#0ec445")
                    messages.append({"role": "system", "content": f"Code output: {output}"})
                else:
                    set_topbar("Code execution cancelled.")
            else:
                set_topbar("No code to execute.")

        set_topbar("")
        entry.configure(state=tk.NORMAL)
        chatbox._parent_canvas.yview_moveto(1.0)

def send_to_ai_thread(text):
    threading.Thread(target=send_to_ai, args=(text,)).start()

def on_enter_key(event):
    button_press()

def save_messages_to_memory():
    global messages, chatMessages
    memory = {
        "messages": messages[1:],  # Exclude the init message
        "chatMessages": chatMessages
    }
    with open("memory.json", "w") as file:
        json.dump(memory, file)

def optimize_chatbox():
    global chatMessages
    if len(chatMessages) > 50:
        chatMessages = chatMessages[-50:]
        for i in range(50):
            chatbox.children[i].destroy()

# UI Elements
root = tk.CTk()
root.title("Bob Assistant")
root.geometry("600x400")
root.resizable(False, False)

root.bind('<Return>', on_enter_key)

top_bar = tk.CTkFrame(root, width=600, height=30)
top_bar.place(x=0, y=0)

topbar = tk.CTkLabel(top_bar, text="Send a message to begin.", font=("Helvetica", 12))
topbar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# result_text = tk.CTkTextbox(root, width=575, height=325, state=tk.DISABLED)
# result_text.place(x=10, y=35)

chatbox = tk.CTkScrollableFrame(root, width=575, height=325)
chatbox.place(x=0, y=35)

entry = tk.CTkEntry(root, width=530)
entry.place(x=20, y=365)

button = tk.CTkButton(root, text=" > ", width=3, command=button_press)
button.place(x=560, y=365)

# Post-setup
client = OpenAI(api_key=config["api-key"])

# Load Data
num_messages = len(messages)
num_to_print = min(num_messages, 50)
for i in range(num_messages - num_to_print, num_messages):
    color = "grey"
    message = messages[i]
    role = message["role"]
    content = message["content"]
    role = role.replace("user", "You")
    role = role.replace("assistant", "Bob")
    role = role.replace("system", "System")

    if role == "Bob":
        color = "#1776e3"
    elif role == "System":
        color = "#ff0000"

    if i != 0:  # Exclude the init message
        add_message(role, content, color)

root.mainloop()
save_messages_to_memory()
