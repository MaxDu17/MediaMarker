import queue
import keyboard
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import *
import csv

# TODO: MODIFY these for your own purposes
KEY_DICT = {"1" : "CORE FACT", "2" : "MY COMMENTS", "3" : "LOOK INTO THIS", "5" : "CROSS REFERENCE", "8" : "QUOTABLE", "9": "INTERESTING FACT"} #what they print out
JOG_LENGTH = 10 #how many seconds the arrow keys jog for

# keys to listen for
CRITICAL_KEYS = list(["space", "left", "right"])
CRITICAL_KEYS.extend(KEY_DICT.keys())
# key information variables
monitoring = True
second_window = None
textBox = None
running = False
counter = 0
database = list() #records the annotations
book = "" #title of the book

root = tk.Tk()
root.title("Video Annotator")
root.attributes('-topmost',True)
root.geometry('300x385+1200+300')


lbl = Label(
    root,
    text="Page 0",
    fg="black",
    font="Verdana 40 bold"
)
lbl.place(x=10, y=10)

label_msg = Text(root, height = 8, width = 31, state = "disabled")
label_msg.place(x=10, y=100)

def mark_and_annotate(key):
    NewMark(key)
    ReadAnnotations()

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
    text='Jump To',
    width=15,
    command=lambda: SetPage(lbl)
)
change_btn.place(x=10, y=250)

dump_btn = Button(
    root,
    text='Dump',
    width=15,
    command=lambda: DumpToText()
)
dump_btn.place(x=160, y=250)

toggle_btn = Button(
    root,
    text='Next',
    width=15,
    bg = "green",
    command=lambda: UpdateCounter(lbl, 1)
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
    command=lambda: Undo()
)
undo_btn.place(x=85, y=310)

def UpdateCounter(lbl, delta):
    global counter
    counter += delta
    counter = 0 if counter < 0 else counter # make sure we don't do negative page
    lbl['text'] = f"Page {counter}"

def OnAnnotationClose():
    global monitoring
    global textBox
    global second_window
    message = textBox.get("1.0", tk.END)
    if len(message) > 0:
        database[-1].append(message.strip("\n"))
    # return states back to unopened state
    monitoring = True
    second_window.destroy()
    second_window = None
    textBox = None

def ReadAnnotations():
    global second_window
    global textBox
    global monitoring
    monitoring = False
    second_window = tk.Toplevel()

    textBox = Text(second_window, height=8, width=31)
    textBox.pack()
    textBox.focus_force()
    second_window.protocol("WM_DELETE_WINDOW", lambda: OnAnnotationClose()) # hook in thsi function to read on close

def SetPage(lbl):
    global counter
    global monitoring
    monitoring = False
    ready = False
    while not ready:
        page = int(input("enter page number "))
        response = input(f"{page} sound good? (y/n)")
        if response == "y":
            counter = page
            ready = True
    monitoring = True
    lbl['text'] = f"Page {counter}"


def ToggleIgnore():
    global monitoring
    monitoring = not monitoring
    ignore_btn["bg"] = "blue" if ignore_btn["bg"] == "white" else "white"
    ignore_btn["text"] = "Start Listening" if ignore_btn["text"] == "Stop Listening" else "Stop Listening"

def NewMark(button):
    # database.append(f"{counter} {KEY_DICT[button]}")
    database.append([counter, KEY_DICT[button]])
    label_msg.configure(state="normal")
    label_msg.insert("1.0", f"{counter} {KEY_DICT[button]}\n")
    label_msg.configure(state="disabled")

def Undo():
    if len(database) > 0:
        database.pop() #removes the last entry
        label_msg.configure(state="normal")
        label_msg.delete("0.0", "2.0")
        label_msg.configure(state="disabled")

def app_main_loop():
    # Create another thread that monitors the keyboard
    global counter
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
                UpdateCounter(lbl, 1)
            elif button == "left":
                UpdateCounter(lbl, -1)
            elif button == "right":
                UpdateCounter(lbl, 1)
            elif button == "esc":
                if second_window is not None:
                    OnAnnotationClose()
            else:
                NewMark(button)
                ReadAnnotations()
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

def DumpToText():
    global book
    global database

    with open(f"{book}.csv", "w", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        print("******* REPORT GENERATED BELOW THIS LINE *******")
        for elem in database:
            writer.writerow(elem)
            # f.write(elem + "\n")
            print(elem)
        print("******* END OF REPORT *******")

def ParseDatabase(reader):
    global counter
    global database
    for line in reader:
        try:
            page, marker, comments = int(line[0]), line[1], line[2]
            print(f"Parsed: pg {page} | {marker} | {comments}")

        except:
            print(f"Line not parsed due to error: {line}")
        database.append([page, marker, comments])
    database.sort(key = lambda x : x[0]) # just in case we messed things up last time s
    counter = database[-1][0]

if __name__ == "__main__":
    # Run the app's main logic loop in a different thread
    reloading = False


    response = input(f"name of book")
    try:
        with open(f"{response}.csv", "r") as f:
            reader = csv.reader(f)
            reloading = True
            ParseDatabase(reader)
    except:
            print("Book not found! Let's make a new entry for you.")
            reloading = False
    book = response

    input("press enter to continue")

    main_loop_thread = threading.Thread(target=app_main_loop) #, args=(my_label,))
    main_loop_thread.daemon = True
    main_loop_thread.start()


    # Run the UI's main loop
    root.mainloop()
    DumpToText()
