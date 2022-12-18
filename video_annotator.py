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
# key information variables

state_of_annotator = {
    "monitoring" : True,
    "second_window" : None,
    "textBox" : None,
    "running" : False,
    "counter" : 0,
    "beginning" : time.time(),
    "reference_point" : time.time(),
    "current_running_time" : 0,
    "running_time" : 0,
}


root = tk.Tk()
root.title("Video Annotator")
root.attributes('-topmost',True)
root.geometry('300x385+1200+300')


lbl = Label(
    root,
    text="00:00:00",
    fg="black",
    font="Verdana 40 bold"
)
lbl.place(x=10, y=10)

label_msg = Text(root, height = 8, width = 31, state = "disabled")
label_msg.place(x=10, y=100)


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

for i, key in enumerate(KEY_DICT.keys()):
    new_button(key, i)

change_btn = Button(
    root,
    text='Recalibrate',
    width=15,
    command=lambda: set_timer(lbl)
)
change_btn.place(x=10, y=250)

dump_btn = Button(
    root,
    text='Dump',
    width=15,
    command=lambda: database.data_dump(pretty_print)
)
dump_btn.place(x=160, y=250)

toggle_btn = Button(
    root,
    text='Start Timer',
    width=15,
    bg = "green",
    command=lambda: toggle_timer(lbl)
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

def update_counter(lbl):
    def count():
        if state_of_annotator["running"]:
            display = to_string(state_of_annotator["counter"])
            lbl['text'] = display
            state_of_annotator["current_running_time"] = (time.time() - state_of_annotator["reference_point"]) \
                                                 + state_of_annotator["running_time"]
            state_of_annotator["counter"] = int(state_of_annotator["current_running_time"])
            lbl.after(100, count) #update every 1/10 second. We might see some "jogging" action
    count()

def toggle_timer(lbl):
    toggle_btn["bg"] = "red" if toggle_btn["bg"] == "green" else "green"
    toggle_btn["text"] = "Start Timer" if toggle_btn["text"] == "Stop Timer" else "Stop Timer"
    state_of_annotator["running"]= not state_of_annotator["running"]
    if state_of_annotator["running"]:
        state_of_annotator["reference_point"] = time.time() #push up the bar
        update_counter(lbl)
    else: #we enter the pausing time
        state_of_annotator["running_time"] += time.time() - state_of_annotator["reference_point"]
        state_of_annotator["reference_point"] = time.time()

def on_annotation_close():
    message = state_of_annotator["textBox"].get("1.0", tk.END)
    if len(message) > 0:
        database.add_annotation(message.strip("\n"))
        # state_of_annotator["database"][-1] += f"\n\tAdditional Messages: {message}"
    # return states back to unopened state
    state_of_annotator["monitoring"] = True
    state_of_annotator["second_window"].destroy()
    state_of_annotator["second_window"] = None
    state_of_annotator["textBox"] = None

def read_annotations():
    state_of_annotator["monitoring"] = False
    state_of_annotator["second_window"]  = tk.Toplevel()

    textBox = Text(state_of_annotator["second_window"] , height=8, width=31)
    textBox.pack()
    textBox.focus_force()
    state_of_annotator["textBox"] = textBox
    state_of_annotator["second_window"].protocol("WM_DELETE_WINDOW", lambda: on_annotation_close())

def set_timer(lbl):
    beg = time.time()
    state_of_annotator["monitoring"] = False
    ready = False
    while not ready:
        raw_string = input("enter time in hh:mm:ss format ")
        hours, mins, secs = tuple(raw_string.split(":"))
        response = input(f"{hours}:{mins}:{secs} sound good? (y/n)")
        if response == "y":
            hours, mins, secs = int(hours), int(mins), int(secs)
            if hours > 99 or mins > 59 or secs > 59:
                print("Invalid numbers!")
                continue
            ready = True

    state_of_annotator["running_time"] = hours * 3600 + mins * 60 + secs
    if state_of_annotator["running"]:
        diff = time.time() - beg
        state_of_annotator["running_time"] += diff #add the time passed
        state_of_annotator["reference_point"] = time.time() #push up the bar

    lbl['text'] = to_string(state_of_annotator["running_time"])
    state_of_annotator["monitoring"] = True

def toggle_ignore():
    state_of_annotator["monitoring"] = not state_of_annotator["monitoring"]
    ignore_btn["bg"] = "blue" if ignore_btn["bg"] == "white" else "white"
    ignore_btn["text"] = "Start Listening" if ignore_btn["text"] == "Stop Listening" else "Stop Listening"

def to_string(counter):
    hours = counter // 3600
    mins = (counter - hours * 3600) // 60
    secs = counter % 60
    if hours < 10:
        hours = "0" + str(hours)
    if mins < 10:
        mins = "0" + str(mins)
    if secs < 10:
        secs = "0" + str(secs)
    return f"{hours}:{mins}:{secs}"

def pretty_print(entry):
    if len(entry) == 2:
        print(f"{to_string(entry[0])} {entry[1]}\n")
    else:
        print(f"{to_string(entry[0])} {entry[1]} \n {entry[2]}\n")

def new_mark(button):
    database.add_new_entry(state_of_annotator["counter"], KEY_DICT[button])
    label_msg.configure(state="normal")
    label_msg.insert("1.0", f"{to_string(state_of_annotator['counter'])} {KEY_DICT[button]}\n")
    label_msg.configure(state="disabled")

def undo():
    if len(database) > 0:
        database.delete_last_entry()
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
                toggle_timer(lbl)
            elif button == "left":
                if state_of_annotator["current_running_time"] > JOG_LENGTH:
                    state_of_annotator["running_time"] -= JOG_LENGTH
            elif button == "right":
                state_of_annotator["running_time"] += JOG_LENGTH
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
    response = input(f"name of subject ")
    database = Database(response)
    state_of_annotator["running_time"] = database.get_last_page()
    print(state_of_annotator["running_time"])

    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()

    # Run the UI's main loop
    root.mainloop()
    database.data_dump(pretty_print)
    # DumpToText(state_of_annotator["database"])
