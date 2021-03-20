import tkinter
from tkinter import ttk
from tkinter import filedialog
import socket
import threading
import tools


def enter_recv(event=None):
    menu_frame.itemconfigure(recv_id, image=big_recv_image)


def enter_send(event=None):
    menu_frame.itemconfigure(send_id, image=big_send_image)


def leave_recv(event=None):
    menu_frame.itemconfigure(recv_id, image=recv_image)


def leave_send(event=None):
    menu_frame.itemconfigure(send_id, image=send_image)


def show_menu():
    recv_frame.pack_forget()
    send_frame.pack_forget()
    start_upload_frame.pack_forget()
    start_download_frame.pack_forget()
    validate_download_frame.pack_forget()
    wait_for_response_frame.pack_forget()
    send_frame.itemconfigure(send_error, text="")
    ip_entry.delete(0, len(ip_entry.get()))
    menu_frame.pack()
    sock.close()


def show_recv(event=None):
    menu_frame.pack_forget()
    recv_frame.pack()
    sock.close()
    threading.Thread(target=start_server).start()


def show_send(event=None):
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path != "":
        menu_frame.pack_forget()
        send_frame.pack()
        sock.close()


def start_server():
    global sock
    global client
    global file_name
    sock = socket.socket()
    sock.bind(("", 4040))
    sock.listen()
    try:
        client, client_ip = sock.accept()
        file_name = client.recv(255).decode("ISO-8859-1")
        validate_download_frame.itemconfigure(validate_download_text,
                                              text="Quelqu'un souhaite vous envoyer :\n" + file_name)
        recv_frame.pack_forget()
        validate_download_frame.pack()
    except OSError:
        pass


def join_server():
    global sock
    sock = socket.socket()
    server_ip = "192.168." + ip_entry.get()
    try:
        sock.connect((server_ip, 4040))
        sock.send(file_path.split("/")[-1].encode("ISO-8859-1"))
        try:
            response = sock.recv(255).decode("ISO-8859-1")
        except OSError:
            pass
    except (ConnectionRefusedError, TimeoutError):
        send_frame.itemconfigure(send_error, text="""
Une erreur est survenu lors de la tentative de connexion.
Assurez-vous d'être connecté sur le même réseau que le receveur,
Vérifiez vôtre connexion internet puis réessayez.""")
    except socket.gaierror:
        send_frame.itemconfigure(send_error, text="""Veuillez entrez un code valable.
Le code doit être fournit par le réceptionneur.""")

    if response == "Valider":
        start_upload()
    else:
        show_menu()


def start_download():
    global file_path
    file_path = filedialog.asksaveasfilename(initialfile=file_name)
    try:
        client.send("Valider".encode("ISO-8859-1"))
    except ConnectionResetError:
        show_menu()
        return
    validate_download_frame.pack_forget()
    start_download_frame.pack()
    root.update()
    file = open(file_path, "wb")
    data = client.recv(1024)
    while data:
        if data == "":
            break
        file.write(data)
        data = client.recv(1024)
    file.close()
    client.close()
    show_menu()


def start_upload():
    wait_for_response_frame.pack_forget()
    start_upload_frame.pack()
    root.update()
    sock.send(open(file_path, "rb").read())
    show_menu()


def launch_join_thread():
    send_frame.pack_forget()
    wait_for_response_frame.pack()
    threading.Thread(target=join_server).start()


def start_thread_download():
    threading.Thread(target=start_download).start()


root = tkinter.Tk()
root.title("CTransfer")
root.resizable(width=0, height=0)
root.iconbitmap("textures/icon.ico")

file_path = ""
file_name = ""
client = socket.socket()
sock = socket.socket()

# Menu frame
menu_frame = tkinter.Canvas(root, width=500, height=300)

send_image = tools.ImageTools.add("textures/send.png")
recv_image = tools.ImageTools.add("textures/recv.png")
big_recv_image = tools.ImageTools.add("textures/recv.png", 225, 225)
big_send_image = tools.ImageTools.add("textures/send.png", 225, 225)

send_id = menu_frame.create_image(133, 125, image=send_image)
recv_id = menu_frame.create_image(367, 125, image=recv_image)

menu_frame.tag_bind(send_id, "<Button-1>", show_send)
menu_frame.tag_bind(recv_id, "<Button-1>", show_recv)

menu_frame.tag_bind(send_id, "<Enter>", enter_send)
menu_frame.tag_bind(recv_id, "<Enter>", enter_recv)
menu_frame.tag_bind(send_id, "<Leave>", leave_send)
menu_frame.tag_bind(recv_id, "<Leave>", leave_recv)

menu_frame.create_text(133, 275, text="Envoyer", font=20)
menu_frame.create_text(367, 275, text="Recevoir", font=20)

menu_frame.pack()

# recv frame
recv_frame = tkinter.Canvas(root, width=500, height=300)

recv_return_button = ttk.Button(recv_frame, text="Retour", command=show_menu)
recv_frame.create_window(10, 10, window=recv_return_button, anchor="nw")

ip = socket.gethostbyname(socket.gethostname())

recv_frame.create_text(250, 75, text="Donnez le code suivant à l'envoyeur :", font=("Arial", 20))
recv_frame.create_text(250, 150, text=ip[8:], font=("Arial", 50))

# send frame
send_frame = tkinter.Canvas(root, width=500, height=300)

send_return_button = ttk.Button(send_frame, text="Retour", command=show_menu)
send_frame.create_window(10, 10, window=send_return_button, anchor="nw")

send_frame.create_text(250, 75, text="Entrez le code fournit par le réceptionneur :", font=("Arial", 18))

ip_entry = ttk.Entry(send_frame, justify="center", font=("Arial", 50))
send_frame.create_window(250, 150, window=ip_entry, width=300)

send_validate_button = ttk.Button(send_frame, text="Valider",
                                  command=launch_join_thread)
send_frame.create_window(250, 230, window=send_validate_button)

send_error = send_frame.create_text(250, 290, fill="red", anchor="s", justify="center")

validate_download_frame = tkinter.Canvas(root, width=500, height=300)

validate_download_text = validate_download_frame.create_text(250, 100, justify="center")

validate_download_validate_button = ttk.Button(validate_download_frame, text="Valider", command=start_thread_download)
validate_download_frame.create_window(300, 230, window=validate_download_validate_button)

validate_download_cancel_button = ttk.Button(validate_download_frame, text="Annuler", command=show_menu)
validate_download_frame.create_window(200, 230, window=validate_download_cancel_button)

start_download_frame = tkinter.Canvas(root, width=500, height=300)
start_download_frame.create_image(250, 120, image=big_recv_image)
start_download_frame.create_text(250, 275, text="Téléchargement en cours...", justify="center")

start_upload_frame = tkinter.Canvas(root, width=500, height=300)
start_upload_frame.create_image(250, 120, image=big_send_image)
start_upload_frame.create_text(250, 275, text="Envoi en cours...", justify="center")


wait_for_response_frame = tkinter.Canvas(root, width=500, height=300)
wait_for_response_frame.create_text(250, 100, text="En attente de validation...", font=("Arial", 25))

root.mainloop()

sock.close()
