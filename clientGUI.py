import socket
import threading
import os
from tkinter import *
from tkinter import ttk

PORT = 5000
SERVER = '192.168.56.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT = '/disconnect'
HISTORY = '/history'
PRIVATE = '/private'
disc_status = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

client.connect(ADDR)

def get_messages():
    while True:
        if disc_status:
            break
        data = client.recv(1024).decode(FORMAT)
        ttk.Label(inside_frame, text=data, font=7, anchor='w', wraplengt=425).pack(fill='both')
        print(data, end='')
        inside_frame.bind("<Configure>", reset_scrollregion)
        e.delete(0, 'end')


def reset_scrollregion(event):
    canvas_scr.configure(scrollregion=canvas_scr.bbox("all"))


def on_closing():
    global disc_status
    disc_status = True
    client.send(DISCONNECT.encode(FORMAT))
    root.destroy()
    os._exit(0)


def start(event=None):
    message = e.get()
    if message == '':
        return 0
    if message == HISTORY:
        clear_frame()
        ttk.Label(inside_frame, text="History of the chat:\n", font=15).pack(fill='both')
        inside_frame.bind("<Configure>", reset_scrollregion)
        print("History of the chat:")
    elif message == DISCONNECT:
        on_closing()
    client.send(message.encode(FORMAT))


def login(event=None):
    nickname = e.get()
    if nickname == '':
        return 0

    client.send(nickname.encode(FORMAT))
    ans = client.recv(5).decode(FORMAT)
    if ans == "block":
        label1["text"] = "This nickname is already occupied! Try another one."
        print(label1["text"])
        return
    elif ans == "pass":
        global max_char
        max_char = 1024
        label1["text"] = f"Welcome to the group chat, {nickname}!"
        label1["font"] = 12
        print(label1["text"])
        thread = threading.Thread(target=get_messages)
        thread.start()
        sendMessage["command"] = start
        root.bind('<Return>', start)


def clear_frame():
    for widgets in inside_frame.winfo_children():
        widgets.destroy()
    inside_frame.bind("<Configure>", reset_scrollregion)


root = Tk()
root.title("Python Socket Chat")
root.geometry('500x600')
root.resizable(width=False, height=False)

canvas = Canvas(root, width=500, height=600, bg="#263D42")
canvas.pack()
mainframe = Frame(root, bg="gray")
mainframe.place(relwidth=0.9, relheight=0.08, relx=0.05, rely=0.88)


max_char = 20

def limitSizeDay(*args):
    value = dayValue.get()
    if len(value) > max_char: dayValue.set(value[:max_char])
dayValue = StringVar()

dayValue.trace('w', limitSizeDay)
e = Entry(mainframe, width=50, textvariable=dayValue)
e.grid(row=0, column=1, padx=130, pady=10, ipady=3)

title_frame = Frame(root, bg="#015f61")
title_frame.place(relwidth=0.9, relheight=0.05, relx=0.05, rely=0.02)
label1 = Label(title_frame, text="Please, enter your nickname (no more than 20 symbols)", font=20, bg="#015f61", fg="white")
label1.pack()

clear = Button(mainframe, text="Clear", padx=10, pady=5, fg="white", bg="grey", command=clear_frame)
clear.place(relx=0.02, rely=0.15)

root.bind('<Return>', login)
sendMessage = Button(mainframe, text="Send", padx=10, pady=5, fg="white", bg="grey", command=login)
sendMessage.place(relx=0.15, rely=0.15)

text_frame = Frame(root, bg="white")
text_frame.place(relwidth=0.9, relheight=0.75, relx=0.05, rely=0.08)

canvas_scr = Canvas(text_frame)
canvas_scr.pack(side=LEFT, fill=BOTH, expand=1)

scrollbar = ttk.Scrollbar(text_frame, orient=VERTICAL, command=canvas_scr.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas_scr.configure(yscrollcommand=scrollbar.set)
canvas_scr.bind('<Configure>', lambda e: canvas_scr.configure(scrollregion=canvas_scr.bbox('all')))

inside_frame = Frame(canvas_scr)
canvas_scr.create_window((0, 0), window=inside_frame, anchor='nw')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
