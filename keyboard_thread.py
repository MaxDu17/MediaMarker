import queue
import keyboard
import threading
import time
import tkinter as tk
from tkinter import Label
from tkinter import Text
from tkinter import *

CRITICAL_KEYS = ["1", "2", "3", "4", "5", "space"]
root = tk.Tk()
running = False
counter = -1
root.geometry('400x450+1000+300')
def counter_label(lbl):
    def count():
        if running:
            global counter
            if counter == -1:
                display = "00:00"
            else:
                display = f"{counter // 60}:{counter % 60}"

            lbl['text'] = display
            lbl.after(1000, count)
            counter += 1

    count()

def ToggleTimer(lbl):
    global running
    running = not running
    print(running)
    if running:
        counter_label(lbl)

def SetTimer(lbl, mins, secs):
    global counter
    counter = mins * 60 + secs
    lbl['text'] = f"{mins}:{secs}"

lbl = Label(
    root,
    text="00:00",
    fg="black",
    # bg='#299617',
    font="Verdana 40 bold"
)

label_msg = Text(root, height = 8)


lbl.place(x=160, y=170)
label_msg.place(x=170, y=250)
database = {}


def app_main_loop():
    # Create another thread that monitors the keyboard
    input_queue = queue.Queue()
    kb_input_thread = threading.Thread(target=_check_critical_keys_pressed, args=(input_queue,))
    kb_input_thread.daemon = True
    kb_input_thread.start()
    # Main logic loop
    while True:
        if not input_queue.empty():
            button = input_queue.get()
            if button == "space":
                ToggleTimer(lbl)
            elif button == "1":
                database[f"{counter // 60}:{counter % 60}"] = "CORE FACT"
                label_msg.insert("1.0", f"{counter // 60}:{counter % 60}: CORE FACT\n")
            elif button == "2":
                database[f"{counter // 60}:{counter % 60}"] = "QUOTABLE LINE"
                label_msg.insert("1.0", f"{counter // 60}:{counter % 60}: QUOTABLE LINE\n")
            elif button == "3":
                database[f"{counter // 60}:{counter % 60}"] = "LOOK INTO THIS"
                label_msg.insert("1.0", f"{counter // 60}:{counter % 60}: LOOK INTO THIS\n")
            elif button == "4":
                database[f"{counter // 60}:{counter % 60}"] = "INTERESTING FACT"
                label_msg.insert("1.0", f"{counter // 60}:{counter % 60}: INTERESTING FACT\n")
            elif button == "5":
                database[f"{counter // 60}:{counter % 60}"] = "CROSS REFERENCE"
                label_msg.insert("1.0", f"{counter // 60}:{counter % 60}: CROSS REFERENCE\n")
        time.sleep(0.1)  # seconds


def _check_critical_keys_pressed(input_queue):
    while True:
        # check if one key is pressed
        while True:
            done = False
            for key in CRITICAL_KEYS:
                if keyboard.is_pressed(key):
                    input_queue.put(key)
                    print("pressed: ", key)
                    done = True
                    break
            if done:
                break
        # check if all keys are no longer pressed
        while True:
            done = True
            for key in CRITICAL_KEYS:
                if keyboard.is_pressed(key):
                    done = False
            if done:
                break
        # time.sleep(0.01)


if __name__ == "__main__":
    # Run the app's main logic loop in a different thread
    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()

    # Run the UI's main loop
    root.mainloop()