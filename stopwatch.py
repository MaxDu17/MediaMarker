from tkinter import *

ws = Tk()
ws.geometry('400x450+1000+300')
# ws.config(bg='#299617')
# ws.iconbitmap('stopwatch.ico')
ws.resizable(0, 0)

counter = -1
running = False


def counter_label(lbl):
    def count():
        if running:
            global counter
            if counter == -1:
                display = "00"
            else:
                display = str(counter)

            lbl['text'] = display

            lbl.after(1000, count)
            counter += 1

    count()


def StartTimer(lbl):
    global running
    running = True
    counter_label(lbl)
    # start_btn['state'] = 'disabled'
    # stop_btn['state'] = 'normal'
    # reset_btn['state'] = 'normal'


def StopTimer():
    global running
    # start_btn['state'] = 'normal'
    # stop_btn['state'] = 'disabled'
    # reset_btn['state'] = 'normal'
    running = False


def ResetTimer(lbl):
    global counter
    counter = -1
    if running == False:
        # reset_btn['state'] = 'disabled'
        lbl['text'] = '00'
    else:
        lbl['text'] = ''


# bg = PhotoImage(file='stopwatch.png')
# img = Label(ws, image=bg, bg='#299617')
# img.place(x=75, y=50)

lbl = Label(
    ws,
    text="00",
    fg="black",
    bg='#299617',
    font="Verdana 40 bold"
)

label_msg = Label(
    ws, text="minutes",
    fg="black",
    bg='#299617',
    font="Verdana 10 bold"
)

lbl.place(x=160, y=170)
label_msg.place(x=170, y=250)

# start_btn = Button(
#     ws,
#     text='Start',
#     width=15,
#     command=lambda: StartTimer(lbl)
# )

def keypress(event):
    print(event)

StartTimer(lbl)
ws.bind("r", keypress)
ws.mainloop()