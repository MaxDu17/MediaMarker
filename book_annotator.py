import queue
import keyboard
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import *
from CSVDatabase import Database

# TODO: MODIFY these for your own purposes
KEY_DICT = {"1" : "CORE FACT", "2" : "MY COMMENTS", "3" : "LOOK INTO THIS", "5" : "CROSS REFERENCE", "8" : "QUOTABLE", "9": "INTERESTING FACT"} #what they print out
JOG_LENGTH = 10 #how many seconds the arrow keys jog for

# keys to listen for
CRITICAL_KEYS = list(["space", "left", "right"])
CRITICAL_KEYS.extend(KEY_DICT.keys())

# having this structure allows for global access
state_of_annotator = {
    "monitoring" : True,
    "second_window" : None,
    "textBox" : None,
    "running" : False,
    "counter" : 0,
    "database" : None
}

root = tk.Tk()
root.title("Video Annotator")
root.attributes('-topmost',True)
root.geometry('300x385+1200+300')

def mark_and_annotate(key):
    new_mark(key)
    read_annotations()

# for the hotkeys
def new_button(key, offset):
    btn = Button(
        root,
        text=key,
        width=5,
        command = lambda: mark_and_annotate(key)
    )
    btn.place(x=10 + 50 * offset, y=350)

lbl = Label(
    root,
    text=f"",
    fg="black",
    font="Verdana 40 bold"
)
lbl.place(x=10, y=10)
label_msg = Text(root, height = 8, width = 31, state = "disabled")
label_msg.place(x=10, y=100)
for i, key in enumerate(KEY_DICT.keys()):
    new_button(key, i)

change_btn = Button(
    root,
    text='Jump To',
    width=15,
    command=lambda: set_page(lbl)
)
change_btn.place(x=10, y=250)

dump_btn = Button(
    root,
    text='Dump',
    width=15,
    command=lambda: database.data_dump()
)
dump_btn.place(x=160, y=250)

toggle_btn = Button(
    root,
    text='Next',
    width=15,
    bg = "green",
    command=lambda: update_counter(lbl, 1)
)
toggle_btn.place(x=10, y=280)

ignore_btn = Button(
    root,
    text='Stop Listening',
    width=15,
    bg = "white",
    command=lambda: toggle_ignore()
)
ignore_btn.place(x=160, y=280)

undo_btn = Button(
    root,
    text='Delete Last',
    width=15,
    command=lambda: undo()
)
undo_btn.place(x=85, y=310)

def update_counter(lbl, delta):
    state_of_annotator["counter"] += delta
    state_of_annotator["counter"] = 0 if state_of_annotator["counter"] < 0 else state_of_annotator["counter"] # make sure we don't do negative page
    lbl['text'] = f"Page {state_of_annotator['counter']}"

def on_annotation_close():
    message = state_of_annotator["textBox"].get("1.0", tk.END)
    if len(message) > 0:
        database.add_annotation(message.strip("\n"))
        # database[-1].append(message.strip("\n"))
    # return states back to unopened state
    state_of_annotator["monitoring"] = True
    state_of_annotator["second_window"].destroy()
    state_of_annotator["second_window"] = None
    state_of_annotator["textBox"] = None

def read_annotations():
    state_of_annotator["monitoring"] = False
    state_of_annotator["second_window"] = tk.Toplevel()
    textBox = Text(state_of_annotator["second_window"], height=8, width=31)
    textBox.pack()
    textBox.focus_force()
    state_of_annotator["textBox"] = textBox
    state_of_annotator["second_window"].protocol("WM_DELETE_WINDOW", lambda: on_annotation_close()) # hook in thsi function to read on close

def set_page(lbl):
    state_of_annotator["monitoring"] = False
    ready = False
    while not ready:
        page = int(input("enter page number "))
        response = input(f"{page} sound good? (y/n)")
        if response == "y":
            state_of_annotator["counter"] = page
            ready = True
    state_of_annotator["monitoring"] = True
    lbl['text'] = f"Page {state_of_annotator['counter']}"


def toggle_ignore():
    state_of_annotator["monitoring"] = not state_of_annotator["monitoring"]
    ignore_btn["bg"] = "blue" if ignore_btn["bg"] == "white" else "white"
    ignore_btn["text"] = "Start Listening" if ignore_btn["text"] == "Stop Listening" else "Stop Listening"

def new_mark(button):
    database.add_new_entry(state_of_annotator["counter"], KEY_DICT[button])
    label_msg.configure(state="normal")
    label_msg.insert("1.0", f"{state_of_annotator['counter']} {KEY_DICT[button]}\n")
    label_msg.configure(state="disabled")

def undo():
    if len(database) > 0:
        database.delete_last_entry() #removes the last entry
        label_msg.configure(state="normal")
        label_msg.delete("0.0", "2.0")
        label_msg.configure(state="disabled")

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
                update_counter(lbl, 1)
            elif button == "left":
                update_counter(lbl, -1)
            elif button == "right":
                update_counter(lbl, 1)
            elif button == "esc":
                if state_of_annotator["second_window"] is not None:
                    on_annotation_close()
            else:
                new_mark(button)
                read_annotations()
        time.sleep(0.05)  # seconds

def _check_critical_keys_pressed(input_queue):
    while True:
        # check if one key is pressed
        while True:
            time.sleep(0.01) #so we don't take like all the CPU
            done = False
            if keyboard.is_pressed("esc"):
                input_queue.put("esc") #special case
                done = True
            for key in CRITICAL_KEYS:
                if keyboard.is_pressed(key) and state_of_annotator["monitoring"]:
                    input_queue.put(key)
                    done = True
                    break
            if done:
                break
        # check if all keys are no longer pressed
        while True:
            time.sleep(0.01)
            done = True
            if keyboard.is_pressed("esc"):
                done = False
            for key in CRITICAL_KEYS:
                if keyboard.is_pressed(key):
                    done = False
            if done:
                break

if __name__ == "__main__":
    # Run the app's main logic loop in a different thread
    response = input(f"name of book ")
    database = Database(response)
    state_of_annotator["counter"] = database.get_last_page()
    update_counter(lbl, 0)
    input("Press enter to continue")
    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()


    # Run the UI's main loop
    root.mainloop()
    database.data_dump()
