import sqlite3
import socket
import threading
import os

connDB = sqlite3.connect("chatHistory.db")
cur = connDB.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS chatHistory (m_order INTEGER, port INTEGER, username TEXT, message TEXT)")

counter = cur.execute("SELECT MAX(m_order) FROM chatHistory").fetchone()
if counter == (None,):
    counter = 0
else:
    counter = counter[0]

PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT = '/disconnect'
HISTORY = '/history'
PRIVATE = '/private'
print(SERVER)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
clients = {}
sock.bind(ADDR)


def add_messageDB(push):
    with sqlite3.connect("chatHistory.db") as c:
        c.cursor().execute(f"INSERT INTO chatHistory VALUES\
                        (?, ?, ?, ?)", push)
        global counter
        counter += 1
        c.commit()


def disconnect(nickname):
    conn = clients[nickname]
    conn.close()
    claim = f'{nickname} disconnected from the server.\n'
    del clients[nickname]
    print(claim, end='')
    send_messages(claim, nickname)


def disconnect_unauthorized(conn):
    conn.close()
    print("Unauthorised used disconnected from the server.")


def send_history(nickname, port):
    with sqlite3.connect("chatHistory.db") as c:
        history = c.cursor().execute("SELECT m_order, port, username, message FROM chatHistory ORDER BY m_order ASC").fetchall()
        for x in history:
            if port == str(x[1]):
                msg = f'You ({x[1]}): {x[3]}\n'
            else:
                msg = f'{x[2]} ({x[1]}): {x[3]}\n'
            clients[nickname].send(msg.encode(FORMAT))

def send_private_msg(message, sender, port):
    conn = clients[sender]
    p_mesg = message.split()
    if len(p_mesg) < 3:
        conn.send("Incorrect structure of private message!\n".encode(FORMAT))
        return
    reciever = p_mesg[1]
    if reciever not in clients.keys():
        conn.send("No user with such nickname!\n".encode(FORMAT))
        return
    else:
        s_mesg = f'[Private message from {sender} ({port})]: '
        for x in range(2, len(p_mesg)):
            s_mesg += p_mesg[x] + " "
        s_mesg += "\n"
        clients[reciever].send(s_mesg.encode(FORMAT))
        clients[sender].send(f"Message to {reciever} was sent successfully!".encode(FORMAT))



def send_messages(message, nickname):
    answer = nickname + ": " + message + '\n'
    for x, y in clients.items():
        if x == nickname:
            y.send(f"You: {message}\n".encode(FORMAT))  # edited for GUI
        else:
            y.send(answer.encode(FORMAT))
    return 0


def handle_client(conn, addr):
    port = str(addr[1])

    while True:
        nickname = conn.recv(20).decode(FORMAT)
        if nickname == DISCONNECT:
            disconnect_unauthorized(conn)
            return 0
        if nickname in clients:
            conn.send("block".encode(FORMAT))
        else:
            conn.send("pass".encode(FORMAT))
            break

    clients[nickname] = conn
    claim = f"{nickname} {addr} is connected to the server!\n"
    push = (int(counter), str(addr[1]), nickname, '/The user connected to the server.')
    add_messageDB(push)
    send_messages(claim, nickname)
    print(claim, end='')
    while True:
        message = conn.recv(1024).decode(FORMAT)
        if message == DISCONNECT:
            push = (int(counter), str(addr[1]), nickname, '/The user disconnected from the server.')
            add_messageDB(push)
            disconnect(nickname)
            break
        elif message == HISTORY:
            send_history(nickname, port)
            print(nickname + ": " + message, end='')
            continue
        elif message.startswith(PRIVATE):
            send_private_msg(message, nickname, port)
            print(111)
            continue
        push = (int(counter), port, nickname, message)
        add_messageDB(push)
        print(nickname + ": " + message + '\n', end='')
        send_messages(message, nickname)


def find_clients():
    print("Server is listening on", str(SERVER))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'Active connections: {threading.active_count() - 2}')

def server_time():
    claim = "Server was shut down. Kick all clients from the server."
    while True:
        command = input()
        if command == "exit":
            for x in clients.values():
                x.send(claim.encode(FORMAT))
                x.close()
            os._exit(0)

print('Server is started!')
thread = threading.Thread(target=server_time)
thread.start()
find_clients()
connDB.close()