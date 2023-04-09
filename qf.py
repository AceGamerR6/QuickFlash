import tkinter as tk
import os
import subprocess
import time
from tkinter import filedialog

version = "0.2.1"
identifier = "Alpha"

def quit():
    event.set(True)

def check_flashrom():
    try:
        subprocess.run(["flashrom", "-R"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # flashrom is installed
        terminalappend(arg1=("    [QUICKFLASH] Flashrom detected.\n"))
    except:
        # flashrom is not installed
        terminalappend(arg1=("E:  [QUICKFLASH] Flashrom not detected!\n"))
        error1Window = tk.Toplevel(root)
        error1Window.title("Fatal Error - Quickflash")
        ewidth = 400
        eheight = 80
        escreen_width = root.winfo_screenwidth()
        escreen_height = root.winfo_screenheight()
        ex = round((escreen_width/2) - (ewidth/2))
        ey = round((escreen_height/2) - (eheight/2))
        error1Window.geometry(str(ewidth) + "x" + str(eheight) + "+" + str(ex) + "+" + str(ey))
        error1Window.resizable(False, False)
        error1Window.protocol("WM_DELETE_WINDOW", lambda: None)
        errorlabel = tk.Label(error1Window, text="Flashrom is not installed on your system.\nPlease read the ReadMe for troubleshooting issues.", anchor='center')
        errorlabel.pack()
        global event
        event = tk.BooleanVar(value=False)
        errorbutton = tk.Button(error1Window, text="Exit", command=lambda:quit())
        errorbutton.pack(side='right')
        root.wait_variable(event)
        root.destroy()

def terminalwipe():
    #  Generated by ChatGPT, doesn't work lmao.
    # Get the current contents of the text widget
    text_contents = terminal_output.get("1.0", tk.END)
    # Split the contents into individual lines
    lines = text_contents.split("\n")
    # Create a new list containing only the lines that do not contain "Found"
    new_lines = [line for line in lines if "Found" not in line]
    # Combine the remaining lines into a single string
    new_text_contents = "\n".join(new_lines)
    # Delete the current contents of the text widget and insert the new contents
    terminal_output.delete("1.0", tk.END)
    terminal_output.insert(tk.END, new_text_contents)

global terminalappend
def terminalappend(arg1):
    terminal_output.config(state="normal")
    terminal_output.insert('end', arg1)
    terminal_output.see('end')
    terminal_output.config(state="disabled")

def initok():
    popupWindow.destroy()
    terminalappend(arg1=("\n    [QUICKFLASH] Initialization complete!\n      Selected chip: " + selected_option.get()))
    autoflash_button.config(state="normal")
    read_save_button.config(state="normal")
    erase_button.config(state="normal")

def init():
    check_flashrom()
    terminalappend(arg1=("    [QUICKFLASH] Starting utility initialization\n"))
    print("[QUICKFLASH] Starting utility initialization")
    init_button.config(state='disabled')
    command = "flashrom --programmer ch341a_spi | grep Found"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in iter(process.stdout.readline, b''):
        terminalappend(arg1=line)
        root.update_idletasks()
    output, error = process.communicate()
    output_text = terminal_output.get("1.0", "end-1c") 
    lines = output_text.split("\n") 
    results_list = [] 
    for line in lines:
        start_index = line.find('"')
        end_index = line.find('"', start_index + 1) 
        if start_index != -1 and end_index != -1: 
            result = line[start_index + 1:end_index] 
            results_list.append(result)
    print(results_list) 
    terminalappend(arg1=("\n    Chip(s) found: " + str(results_list) + "\n  !!Please specify your chip model in the popup dialog!!"))
    global popupWindow
    popupWindow = tk.Toplevel(root)
    popupWindow.title("Specify chip - QuickFlash")
    pwidth = 400
    pheight = 80
    pscreen_width = root.winfo_screenwidth()
    pscreen_height = root.winfo_screenheight()
    px = round((pscreen_width/2) - (pwidth/2))
    py = round((pscreen_height/2) - (pheight/2))
    popupWindow.geometry(str(pwidth) + "x" + str(pheight) + "+" + str(px) + "+" + str(py))
    popupWindow.protocol("WM_DELETE_WINDOW", lambda: None)
    popupWindow.resizable(False, False)
    global selected_option
    selected_option = tk.StringVar(popupWindow)
    selected_option.set(results_list[0])
    popupdropdown = tk.OptionMenu(popupWindow, selected_option, *results_list)
    popupdropdown.pack(pady=(8, 0))
    popupok = tk.Button(popupWindow, text="Close", width=10, command=initok)
    popupok.pack(side='right', padx=6, pady=(0,2))

def autoflash():
    autoflash_button.config(state="disabled")
    terminalappend(arg1=("\n    [QUICKFLASH] Autoflash! Please specify your target file to be flashed.\n"))
    time.sleep(0.2)
    filepath = filedialog.askopenfilename()
    terminalappend(arg1=("\n      File path: " + filepath + "\n"))
    terminalappend(arg1=("\n    Please wait as flashrom wipes chip and flashes target file onto chip...\n\n"))
    command = "flashrom --programmer ch341a_spi -c " + selected_option.get() + " -w " + str(filepath)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in iter(process.stdout.readline, b''):
        terminalappend(arg1=line)
        root.update_idletasks()
    terminalappend(arg1=("\n    [QUICKFLASH] Autoflash complete."))
    autoflash_button.config(state="normal")

def readsave():
    read_save_button.config(state="disabled")
    terminalappend(arg1=("\n    [QUICKFLASH] Read & Save! Please specify savefile."))
    global save_path
    save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All files", "*.*")])
    terminalappend(arg1=("\n      Specified savefile path: " + save_path))
    terminalappend(arg1=("\n    Please wait as flashrom dumps chip contents to file...\n\n"))
    command = "flashrom --programmer ch341a_spi -c " + selected_option.get() + " -r " + str(save_path)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in iter(process.stdout.readline, b''):
        terminalappend(arg1=line)
        root.update_idletasks()
    terminalappend(arg1=("\n    [QUICKFLASH] Read & Save complete."))
    read_save_button.config(state="normal")

def erase():
    erase_button.config(state="disabled")
    terminalappend(arg1=("\n    [QUICKFLASH] Erase! Please wait as flashrom erases chip...\n\n"))
    command = "flashrom --programmer ch341a_spi -c " + selected_option.get() + " -E"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    for line in iter(process.stdout.readline, b''):
        terminalappend(arg1=line)
        root.update_idletasks()
    terminalappend(arg1=("\n    [QUICKFLASH] Erase complete."))
    erase_button.config(state="normal")
    

root = tk.Tk()
root.title("QuickFlash " + identifier)
width = 900
height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = round((screen_width/2) - (width/2))
y = round((screen_height/2) - (height/2))
root.geometry(str(width) + "x" + str(height) + "+" + str(x) + "+" + str(y))
root.resizable(False, False)

top_frame = tk.Frame(root, height=100)
top_frame.pack(fill="x")

button_frame = tk.Frame(root, height=1)
button_frame.pack(side='bottom', anchor='center')

bottom_frame = tk.Frame(root, height=410)
bottom_frame.pack(fill="both", expand=True)

header = tk.Label(top_frame, text="QuickFlash " + identifier + " v" + version + " - CH341A_SPI", font=("Arial", 16))
header.pack(fill='x', anchor="center")

init_button = tk.Button(button_frame, text="Initialize", command=lambda: init())
init_button.pack(side="left", padx=0, pady=(0, 8))

autoflash_button = tk.Button(button_frame, text="Autoflash", command=lambda: autoflash(), state="disabled")
autoflash_button.pack(side="left", padx=0, pady=(0, 8))

read_save_button = tk.Button(button_frame, text="Read & Save", command=lambda: readsave(), state="disabled")
read_save_button.pack(side="left", padx=0, pady=(0, 8))

erase_button = tk.Button(button_frame, text="Erase", command=lambda: erase(), state="disabled")
erase_button.pack(side="left", padx=0, pady=(0, 8))

exit_button = tk.Button(button_frame, text="Exit", command=root.destroy)
exit_button.pack(side="left", padx=0, pady=(0, 8))

terminal_header = tk.Label(bottom_frame, text="- Terminal output -")
terminal_header.pack(anchor='center', pady=2)
global terminal_output
terminal_output = tk.Text(bottom_frame, font=("Courier New", 13))
terminal_output.pack(fill="both", expand=True)
terminal_output.config(state="disabled")

root.mainloop()