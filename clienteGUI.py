import socket
import threading
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

SERVER_PORT = 1234
CLIENT_PORT = 1235
PUBLIC_FOLDER = "./public"

if not os.path.exists(PUBLIC_FOLDER):
    os.makedirs(PUBLIC_FOLDER)


def send_request(server_ip, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, SERVER_PORT))
            client_socket.sendall(message.encode())
            return client_socket.recv(4096).decode()
    except Exception as e:
        return f"[ERROR] {e}"


def join_server(server_ip):
    response = send_request(server_ip, f"JOIN {server_ip}\n")
    messagebox.showinfo("Response", response)


def refresh_list(server_ip):
    files_local = {
        f
        for f in os.listdir(PUBLIC_FOLDER)
        if os.path.isfile(os.path.join(PUBLIC_FOLDER, f))
    }
    response = send_request(server_ip, "LISTFILES\n")
    files_server = (
        set()
        if response == "NOFILES"
        else {line.split()[0] for line in response.split("\n")}
    )

    for file in files_local - files_server:
        size = os.path.getsize(os.path.join(PUBLIC_FOLDER, file))
        messagebox.showinfo("Response", send_request(server_ip, f"CREATEFILE {file} {size}\n"))

    for file in files_server - files_local:
        messagebox.showinfo("Response", send_request(server_ip, f"DELETEFILE {file}\n"))


def search_file(server_ip, filename):
    response = send_request(server_ip, f"SEARCH {filename}\n")
    messagebox.showinfo("Response", response)


def get_file(client_ip, filename, offset_start, offset_end=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((client_ip, CLIENT_PORT))
            message = (
                f"GET {filename} {offset_start} {offset_end}\n"
                if offset_end
                else f"GET {filename} {offset_start}\n"
            )
            client_socket.sendall(message.encode())
            with open(os.path.join(PUBLIC_FOLDER, filename), "wb") as file:
                while data := client_socket.recv(1024):
                    file.write(data)
            messagebox.showinfo("Info", f"File {filename} downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"[ERROR] {e}")


def handle_file_request(client_socket):
    try:
        request = client_socket.recv(1024).decode().split()
        if request[0] == "GET" and len(request) >= 3:
            filename, offset_start = request[1], int(request[2])
            offset_end = int(request[3]) if len(request) == 4 else None
            file_path = os.path.join(PUBLIC_FOLDER, filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file.seek(offset_start)
                    data = file.read(offset_end - offset_start if offset_end else None)
                    client_socket.sendall(data)
            else:
                client_socket.sendall(b"FILENOTFOUND")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()


def start_file_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("", CLIENT_PORT))
        server_socket.listen(5)
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(
                target=handle_file_request, args=(client_socket,), daemon=True
            ).start()


def leave_server(server_ip):
    response = send_request(server_ip, "LEAVE\n")
    messagebox.showinfo("Response", response)


def create_gui():
    root = tk.Tk()
    root.title("Cliente")

    def join_command():
        server_ip = simpledialog.askstring("Input", "Enter server IP:")
        if server_ip:
            join_server(server_ip)

    def refresh_command():
        server_ip = simpledialog.askstring("Input", "Enter server IP:")
        if server_ip:
            refresh_list(server_ip)

    def search_command():
        server_ip = simpledialog.askstring("Input", "Enter server IP:")
        filename = simpledialog.askstring("Input", "Enter filename:")
        if server_ip and filename:
            search_file(server_ip, filename)

    def get_command():
        client_ip = simpledialog.askstring("Input", "Enter client IP:")
        filename = simpledialog.askstring("Input", "Enter filename:")
        offset_start = simpledialog.askinteger("Input", "Enter offset start:")
        offset_end = simpledialog.askinteger("Input", "Enter offset end (optional):")
        if client_ip and filename and offset_start is not None:
            get_file(client_ip, filename, offset_start, offset_end)

    def leave_command():
        server_ip = simpledialog.askstring("Input", "Enter server IP:")
        if server_ip:
            leave_server(server_ip)

    def exit_command():
        root.quit()

    tk.Button(root, text="Join Server", command=join_command).pack(pady=5)
    tk.Button(root, text="Refresh List", command=refresh_command).pack(pady=5)
    tk.Button(root, text="Search File", command=search_command).pack(pady=5)
    tk.Button(root, text="Get File", command=get_command).pack(pady=5)
    tk.Button(root, text="Leave Server", command=leave_command).pack(pady=5)
    tk.Button(root, text="Exit", command=exit_command).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=start_file_server, daemon=True).start()
    create_gui()
