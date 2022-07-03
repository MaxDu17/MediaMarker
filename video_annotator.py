import queue
import keyboard
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import *

# TODO: MODIFY these for your own purposes
KEY_DICT = {"1" : "CORE FACT", "2" : "LOOK INTO THIS", "3" : "INTERESTING FACT", "5" : "CROSS REFERENCE"} #what they print out
JOG_LENGTH = 10 #how many seconds the arrow keys jog for


CRITICAL_KEYS = list(["space", "left", "right"])
CRITICAL_KEYS.extend(KEY_DICT.keys())

monitoring = True
additional_annotations = ""
second_window = None

root = tk.Tk()
root.title("Video Annotator")
root.attributes('-topmost',True)
running = False
counter = 0
root.geometry('300x385+1200+300')

beginning = time.time()
reference_point = time.time()
current_running_time = 0
running_time = 0

lbl = Label(
    root,
    text="00:00:00",
    fg="black",
    font="Verdana 40 bold"
)
lbl.place(x=10, y=10)


label_msg = Text(root, height = 8, width = 31, state = "disabled")
label_msg.pack()
label_msg.place(x=10, y=100)

database = list() #records the annotations

def new_button(key, offset):
    btn = Button(
        root,
        text=key,
        width=5,
        command = lambda: new_msg(key)
    )
    btn.place(x=10 + 50 * offset, y=350)

for i, key in enumerate(KEY_DICT.keys()):
    new_button(key, i)


change_btn = Button(
    root,
    text='Recalibrate',
    width=15,
    command=lambda: SetTimer(lbl)
)
change_btn.place(x=10, y=250)

dump_btn = Button(
    root,
    text='Dump',
    width=15,
    command=lambda: dump_to_text(database)
)
dump_btn.place(x=160, y=250)

toggle_btn = Button(
    root,
    text='Start Timer',
    width=15,
    bg = "green",
    command=lambda: ToggleTimer(lbl)
)
toggle_btn.place(x=10, y=280)

ignore_btn = Button(
    root,
    text='Stop Listening',
    width=15,
    bg = "white",
    command=lambda: ToggleIgnore()
)
ignore_btn.place(x=160, y=280)

undo_btn = Button(
    root,
    text='Delete Last',
    width=15,
    command=lambda: undo()
)
undo_btn.place(x=85, y=310)

# undo_btn = Button(
#     root,
#     text='test',
#     width=15,
#     command=lambda: read_annotations()
# )
# undo_btn.place(x=85, y=310)

def UpdateCounter(lbl):
    def count():
        global current_running_time
        global running_time
        if running:
            global counter
            display = to_string(counter)

            lbl['text'] = display
            current_running_time = (time.time() - reference_point) + running_time
            counter = int(current_running_time)
            lbl.after(100, count) #update every 1/10 second. We might see some "jogging" action
    count()

def ToggleTimer(lbl):
    toggle_btn["bg"] = "red" if toggle_btn["bg"] == "green" else "green"
    toggle_btn["text"] = "Start Timer" if toggle_btn["text"] == "Stop Timer" else "Stop Timer"
    global running
    global reference_point
    global running_time
    running = not running
    if running:
        reference_point = time.time() #push up the bar
        UpdateCounter(lbl)
    else: #we enter the pausing time
        running_time += time.time() - reference_point
        reference_point = time.time()

def msgbox_close_routine(textBox):
    global monitoring
    global second_window
    message = textBox.get("1.0", "end-1c")
    database[-1] += f"\n\tAdditional Messages: {message}"
    # return states back to normal
    monitoring = True
    second_window.destroy()
    second_window = None

def read_annotations():
    global second_window
    global monitoring
    monitoring = False
    second_window = tk.Toplevel()
    textBox = Text(second_window, height=8, width=31)
    textBox.pack()
    second_window.protocol("WM_DELETE_WINDOW", lambda: msgbox_close_routine(textBox))
    # def retrieve_input(window):
    #     global second_window
    #     global monitoring
    #     global database
    #     message = textBox.get("1.0", "end-1c")
    #     database[-1] += f"\n\tAdditional Messages: {message}"
    #     monitoring = True
    #     second_window.destroy()
    #     second_window = None



def SetTimer(lbl):
    beg = time.time()
    global monitoring
    global running_time
    global reference_point
    monitoring = False
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

    global counter
    running_time = hours * 3600 + mins * 60 + secs
    if running:
        diff = time.time() - beg
        running_time += diff #add the time passed
        reference_point = time.time() #push up the bar

    lbl['text'] = to_string(running_time)
    monitoring = True

def ToggleIgnore():
    global monitoring
    monitoring = not monitoring
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

def new_msg(button):
    database.append(f"{to_string(counter)} {KEY_DICT[button]}")
    # database[to_string(counter)] = KEY_DICT[button]
    label_msg.configure(state="normal")
    label_msg.insert("1.0", f"{to_string(counter)} {KEY_DICT[button]}\n")
    label_msg.configure(state="disabled")

def undo():
    if len(database) > 0:
        database.pop() #removes the last entry
        label_msg.configure(state="normal")
        label_msg.delete("0.0", "2.0")
        label_msg.configure(state="disabled")

def app_main_loop():
    # Create another thread that monitors the keyboard
    global counter
    global running_time
    global current_running_time
    global additional_annotations
    global second_window
    global monitoring

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
            elif button == "left":
                if current_running_time > JOG_LENGTH:
                    running_time -= JOG_LENGTH
            elif button == "right":
                running_time += JOG_LENGTH
            elif button == "esc" and second_window is not None:
                print("escaped!")
                second_window.destroy()
                second_window = None
                monitoring = True
            else:
                new_msg(button)
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
                if keyboard.is_pressed(key) and monitoring:
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

def dump_to_text(database):
    with open(f"dump_{time.time()}.txt", "w") as f:
        print("******* REPORT GENERATED BELOW THIS LINE *******")
        for elem in database:
            f.write(elem + "\n")
            print(elem)
        print("******* END OF REPORT *******")


if __name__ == "__main__":
    # Run the app's main logic loop in a different thread
    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()

    # Run the UI's main loop
    root.mainloop()
    dump_to_text(database)
