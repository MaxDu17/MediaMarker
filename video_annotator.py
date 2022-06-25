import queue
import keyboard
import threading
import time
import tkinter as tk
from tkinter import Label
from tkinter import Text
from tkinter import *

CRITICAL_KEYS = ["1", "2", "3", "5", "space", "left", "right"]
MONITORING = True
root = tk.Tk()
root.title("Video Annotator")
root.attributes('-topmost',True)
running = False
counter = -1
root.geometry('300x320+1000+300')

#TODO: add toggle button (to prevent shortcut misery)

beginning = time.time()
reference_point = time.time()
running_time = 0
pausing_time = 0

def counter_label(lbl):
    def count():
        global running_time
        if running:
            global counter
            if counter == -1:
                display = "00:00"
            else:
                display = to_string(counter)

            lbl['text'] = display
            current_running_time = (time.time() - reference_point) + running_time
            counter = int(current_running_time)
            lbl.after(500, count) #update every 1/2 second. We might see some "jogging" action

    count()

def ToggleTimer(lbl):
    global running
    global reference_point
    global running_time
    global pausing_time
    running = not running
    if running:
        pausing_time += time.time() - reference_point #this is the time that passed in paus
        reference_point = time.time() #now, we are in a new reference point
        # print(f"running_time: {running_time}, pausing_time: {pausing_time}")
        counter_label(lbl)
    else: #we enter the pausing time
        running_time += time.time() - reference_point
        reference_point = time.time()
        # print(f"running_time: {running_time}, pausing_time: {pausing_time}")


def SetTimer(lbl):
    global MONITORING
    MONITORING = False
    ready = False
    while not ready:
        mins = int(input("enter minutes: "))
        secs = int(input("enter seconds: "))
        response = input(f"{mins}:{secs} sound good? (y/n)")
        if response == "y":
            ready = True

    global counter
    counter = mins * 60 + secs
    lbl['text'] = f"{mins}:{secs}"
    MONITORING = True

lbl = Label(
    root,
    text="00:00",
    fg="black",
    font="Verdana 40 bold"
)

label_msg = Text(root, height = 8, width = 30)
label_msg.pack()

lbl.place(x=10, y=10)
label_msg.place(x=10, y=100)
database = {}

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
    text='TG',
    width=15,
    command=lambda: ToggleTimer(lbl)
)
toggle_btn.place(x=85, y=280)


def to_string(counter):
    mins = counter // 60
    secs = counter % 60
    if mins < 10:
        mins = "0" + str(mins)
    if secs < 10:
        secs = "0" + str(secs)
    return f"{mins}:{secs}"

def app_main_loop():
    # Create another thread that monitors the keyboard
    global counter
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
                if counter > 10:
                    counter -= 10
                else:
                    counter = 0
            elif button == "right":
                counter += 10
            elif button == "1":
                database[to_string(counter)] = "CORE FACT"
                label_msg.insert("1.0", f"{to_string(counter)} CORE FACT\n")
            elif button == "2":
                database[to_string(counter)] = "LOOK INTO THIS"
                label_msg.insert("1.0", f"{to_string(counter)} LOOK INTO THIS\n")
            elif button == "3":
                database[to_string(counter)] = "INTERESTING FACT"
                label_msg.insert("1.0", f"{to_string(counter)} INTERESTING FACT\n")
            elif button == "5":
                database[to_string(counter)] = "CROSS REFERENCE"
                label_msg.insert("1.0", f"{to_string(counter)} CROSS REFERENCE\n")
        time.sleep(0.1)  # seconds


def _check_critical_keys_pressed(input_queue):
    while True:
        # check if one key is pressed
        while True:
            done = False
            for key in CRITICAL_KEYS:
                if keyboard.is_pressed(key) and MONITORING:
                    input_queue.put(key)
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

def dump_to_text(database):
    with open(f"dump_{time.time()}.txt", "w") as f:
        print("******* REPORT GENERATED BELOW THIS LINE *******")
        for key, value in database.items():
            f.write(f"{key} {value}\n")
            print(f"{key} {value}")
        print("******* END OF REPORT *******")


if __name__ == "__main__":
    # Run the app's main logic loop in a different thread
    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()

    # Run the UI's main loop
    root.mainloop()
    dump_to_text(database)