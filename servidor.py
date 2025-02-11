import socket
import threading
import json
import os
import re

LOCK = threading.Lock()
JSON_FILE_PATH = "lista_arquivos.json"
SERVER_PORT = 1234


def load_files():
    with LOCK:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, "r") as f:
                return json.load(f)
    return {}


def save_files(dados):
    print(f"[LOG] Saving files: {dados}")
    with LOCK:
        with open(JSON_FILE_PATH, "w") as f:
            json.dump(dados, f, indent=4)


def handle_client(client_socket, client_address, all_files):
    client_ip = client_address[0]

    try:
        while message := client_socket.recv(1024).decode():
            print(f"[LOG] {client_ip} sent: {message}")
            command, *args = message.split()
            print(f"[LOG] {command} {args}")
            response = process_command(command, args, client_ip, all_files, client_socket)
            client_socket.sendall(response.encode())
    except Exception as e:
        print(f"[ERROR] {client_ip}: {e}")
    finally:
        client_socket.close()


def process_command(command, args, client_ip, all_files, client_socket):
    if command == "JOIN":
        if client_ip not in all_files:
            all_files[client_ip] = []
            save_files(all_files)
            return "CONFIRMJOIN"
        return "CLIENTALREADYCONNECTED"

    elif command == "CREATEFILE":
        if len(args) != 2:
            return "INVALIDCOMMAND"
        filename, size = args
        print(f"[LOG] {filename} {size}")
        print(f"[LOG] {args}")
        size = int(size)
        if any(f["filename"] == filename for f in all_files.get(client_ip, [])):
            return "FILEALREADYEXISTS"
        all_files[client_ip].append({"filename": filename, "size": size})
        print(f"[LOG] {all_files}")
        save_files(all_files)
        return "CONFIRMCREATEFILE"

    elif command == "DELETEFILE":
        if len(args) != 1:
            return "INVALIDCOMMAND"
        filename = args[0]
        if any(f["filename"] == filename for f in all_files.get(client_ip, [])):
            all_files[client_ip] = [
                f for f in all_files[client_ip] if f["filename"] != filename
            ]
            save_files(all_files)
            return "CONFIRMDELETEFILE"
        return "FILENOTFOUND"

    elif command == 'SEARCH':
        filename_pattern = args[0]
        try:
            regex = re.compile(filename_pattern)
            results = [
                f"FILE {f['filename']} {ip} {f['size']}" 
                for ip, files in all_files.items()
                for f in files if regex.search(f['filename'])
            ]
            if results:
                client_socket.sendall("\n".join(results).encode())
                return
            else:
                client_socket.sendall(b"FILENOTFOUND")
        except re.error:
            client_socket.sendall(b"INVALIDREGEX")


    elif command == "LEAVE":
        if client_ip in all_files:
            del all_files[client_ip]
            save_files(all_files)
            return "CONFIRMLEAVE"
        return "CLIENTNOTFOUND"

    elif command == "SYNCFILES":
        files = all_files.get(client_ip, [])
        return (
            "\n".join(f"{file['filename']} {file['size']}" for file in files)
            if files
            else "NOFILES"
        )
    
    elif command == "LISTFILES":
        files_list = [
            f"FILE {file['filename']} {ip} {file['size']}"
            for ip, files in all_files.items()
            for file in files
        ]
        return "\n".join(files_list) if files_list else "NOFILES"

    return "UNKNOWNCOMMAND"

def get_server_ip():
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    return server_ip

def start_server():
    all_files = load_files()
    server_ip = get_server_ip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("", SERVER_PORT))
        server_socket.listen(5)
        print(f"[SERVER] Listening on {server_ip} on port {SERVER_PORT}")
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"[CONNECTION] {client_address} connected.")
                print(f"[LOG] {all_files}")
                threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address, all_files),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print("[SERVER] Shutting down.")


if __name__ == "__main__":
    start_server()
