import socket
import threading
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

#sudo apt install python3-tk

SERVER_PORT = 1234
CLIENT_PORT = 1235
PUBLIC_FOLDER = "./public"

server_ip = None

if not os.path.exists(PUBLIC_FOLDER):
    os.makedirs(PUBLIC_FOLDER)


def send_request(server_ip, message):
    try:
        print(f"[DEBUG] Sending message: {message}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, SERVER_PORT))
            client_socket.sendall(message.encode())
            return client_socket.recv(4096).decode()
    except Exception as e:
        return f"[ERROR] {e}"


def join_server(server_ip):
    response = send_request(server_ip, f"JOIN {server_ip}\n")
    if response == "CONFIRMJOIN":
        messagebox.showinfo("Response", "Conectado ao servidor com sucesso.")
    elif response == "CLIENTALREADYCONNECTED":
        messagebox.showinfo("Response", "Cliente já conectado.")
    else:
        messagebox.showerror("Error", response)


def sync_list(server_ip):
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
        try:
            size = os.path.getsize(os.path.join(PUBLIC_FOLDER, file))
            send_request(server_ip, f"CREATEFILE {file} {size}\n")
        except OSError as e:
            print(f"[ERROR] Could not get size of file {file}: {e}")
        
    deleted_files = files_server - files_local
    
    if deleted_files != {'FILE'}:
        for file in deleted_files:
            if messagebox.askyesno("Confirm Delete", f"Os seguintes arquivos serão deletados:\n{', '.join(deleted_files)}\nVocê quer prosseguir?"):
                for file in deleted_files:
                    send_request(server_ip, f"DELETEFILE {file}\n")
    messagebox.showinfo("Sync Complete", "Sincronização concluída com sucesso.")


def search_file(server_ip, filename):
    response = send_request(server_ip, f"SEARCH {filename}\n")
    if response == "FILENOTFOUND":
        messagebox.showinfo("Response", "Nenhum arquivo encontrado.")
    else:
        files = response.split("\n")
        message = "Arquivos encontrados:\n" + "\n".join(files)
        messagebox.showinfo("Response", message)


def get_file(client_ip, filename, offset_start, offset_end=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((client_ip, CLIENT_PORT))
            if offset_end is not None:
                message = f"GET {filename} {offset_start} {offset_end}\n"
            else:
                message = f"GET {filename} {offset_start}\n"
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
    if response == "CONFIRMLEAVE":
        messagebox.showinfo("Response", "Cliente desconectado com sucesso.")
    elif response == "CLIENTNOTFOUND":
        messagebox.showinfo("Response", "Cliente não encontrado.")
    else:
        messagebox.showinfo("Error", response)


def create_gui():
    def join_command():
        global server_ip
        if server_ip is None:   
            server_ip = simpledialog.askstring("Input", "Digite o ip do servidor:")
        if server_ip:
            join_server(server_ip)

    def sync_command():
        if server_ip:
            sync_list(server_ip)
        else:
            messagebox.showwarning("Warning", "Você não está conectado a nenhum servidor.")

    def refresh_command():
        if server_ip:
            tree.delete(*tree.get_children())
            response = send_request(server_ip, "LISTFILES\n")
            
            if response == "NOFILES":
                messagebox.showinfo("Info", "Sem arquivos disponíveis no servidor.")
                return

            for line in response.split("\n"):
                parts = line.split()
                print(parts)
                if len(parts) == 4:
                    type, file_name, file_size, owner_ip = parts
                    tree.insert("", "end", values=(file_name, owner_ip, file_size))
        else:
            tree.delete(*tree.get_children())
            messagebox.showwarning("Warning", "Você não está conectado a nenhum servidor.")

    def search_command():
        filename = simpledialog.askstring("Input", "Enter filename:")
        if server_ip and filename:
            search_file(server_ip, filename)
        elif not server_ip:
            messagebox.showwarning("Warning", "Você não está conectado a nenhum servidor.")

    def get_command():
        client_ip = simpledialog.askstring("Input", "Enter client IP:")
        filename = simpledialog.askstring("Input", "Enter filename:")
        offset_start = simpledialog.askinteger("Input", "Enter offset start:")
        offset_end = simpledialog.askstring("Input", "Enter offset end (optional):")
        if offset_end:
            try:
                offset_end = int(offset_end)
            except ValueError:
                offset_end = None
        if client_ip and filename and offset_start is not None:
            if offset_end is not None:
                get_file(client_ip, filename, offset_start, offset_end)
            else:
                get_file(client_ip, filename, offset_start)

    def leave_command():
        global server_ip
        if server_ip:
            leave_server(server_ip)
            server_ip = None
        else:
            messagebox.showwarning("Warning", "Você não está conectado a nenhum servidor.")


    global tree
    root = tk.Tk()
    root.title("Cliente - Compartilhamento de Arquivos")
    root.geometry("900x600")
    root.configure(bg="#2c3e50")   

    style = ttk.Style()
    style.theme_use("clam")   
    style.configure("TButton", padding=6, relief="flat", background="#3498db", font=("Arial", 11))
    style.map("TButton", background=[("active", "#2980b9")], foreground=[("active", "white")])
    style.configure("Treeview", background="#ecf0f1", fieldbackground="#ecf0f1", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3498db")

    title_frame = tk.Frame(root, bg="#34495e", height=50)
    title_frame.pack(fill="x")

    title_label = tk.Label(title_frame, text="Cliente - Compartilhamento de Arquivos", font=("Arial", 16, "bold"), fg="white", bg="#34495e")
    title_label.pack(pady=10)

     
    frame = tk.Frame(root, bg="#2c3e50")
    frame.pack(pady=10, padx=10, fill="both", expand=True)

    columns = ("Nome do Arquivo", "Tamanho (bytes)", "Dono (IP)")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    tree.heading("Nome do Arquivo", text="Nome do Arquivo")
    tree.heading("Dono (IP)", text="Dono (IP)")
    tree.heading("Tamanho (bytes)", text="Tamanho (bytes)")
    tree.column("Nome do Arquivo", anchor="w", width=350)
    tree.column("Dono (IP)", anchor="center", width=200)
    tree.column("Tamanho (bytes)", anchor="center", width=150)
    
     
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

     
    button_frame = tk.Frame(root, bg="#2c3e50")
    button_frame.pack(side=tk.BOTTOM, pady=10)

    ttk.Button(button_frame, text="Join Server", command=join_command).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Sync Files", command=sync_command).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Refresh List", command=refresh_command).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Search File", command=search_command).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Get File", command=get_command).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Leave Server", command=leave_command).pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=start_file_server, daemon=True).start()
    create_gui()
