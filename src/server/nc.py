import socket
import threading
import configparser
import datetime
import os
import ctypes
import sys

# Configuration directory and file paths
config_path = os.path.join("src", "config.ini")

# Ensure the configuration directory exists
if not os.path.exists(config_path):
    config = configparser.ConfigParser()
    config["NetworkClock"] = {"port": "12345"}
    with open(config_path, "w") as configfile:
        config.write(configfile)

config = configparser.ConfigParser()
config.read(config_path)
TCP_PORT = int(config["NetworkClock"]["port"])

commands = {"yyyy": "%Y", "hh": "%H", "nn": "%M", "dd": "%d", "mm": "%m", "ss": "%S"}


def drop_privileges():
    if os.name != "nt":  # Assuming a Unix-like system
        import pwd, grp

        uid = pwd.getpwnam("nobody").pw_uid
        gid = grp.getgrnam("nogroup").gr_gid
        os.setgid(gid)
        os.setuid(uid)
    else:
        # On Windows, reduce privileges by setting token privileges
        import win32api
        import win32security
        import ntsecuritycon as con

        token = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY,
        )
        privs = (
            (win32security.LookupPrivilegeValue(None, con.SE_SHUTDOWN_NAME), 0),
            (win32security.LookupPrivilegeValue(None, con.SE_SYSTEMTIME_NAME), 0),
        )
        win32security.AdjustTokenPrivileges(token, False, privs)


def sanitize_input(input_str):
    return input_str.replace("%n", "%%n")


def handle_command(command):
    if command:
        try:
            # Sanitize the input command
            command = sanitize_input(command)

            # Check for the 'set' command
            if command.startswith("set "):
                parts = command.split(" ")
                if len(parts) == 3:
                    date, time = parts[1], parts[2]
                    set_system_time(date, time)
                    return f"System time set to {date} {time}."
                else:
                    return "Invalid set command format. Use: set yyyy-mm-dd hh:nn:ss"

            # Replace commands in the format string with datetime format strings
            for cmd, fmt in commands.items():
                command = command.replace(cmd, fmt)
            current_time = datetime.datetime.now().strftime(command)
            return current_time
        except ValueError:
            return "Invalid format string."
    else:
        return "No command received."


def handle_client(client_socket, addr):
    sys.stdout.write(f"[*] Client connected from {addr}\n> ")
    sys.stdout.flush()
    buffer = ""
    while True:
        try:
            data = client_socket.recv(4096).decode("utf-8")
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if line:
                    print(f"Received command from client: {line}")
                    response = handle_command(line)
                    client_socket.send(response.encode("utf-8"))
                    sys.stdout.write(f"Sent response to client: {response}\n> ")
                    sys.stdout.flush()
        except ConnectionResetError:
            break
    client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", TCP_PORT))
    server_socket.listen(5)

    welcome_message = (
        "---------------------------------------------\n"
        "Server.\n"
        "If you have admin rights, you have access to the 'set' command to adjust the system time.\n"
        "Available command format: set yyyy-mm-dd hh:nn\n"
        "Other available commands: yyyy, dd, mm, nn, hh, ss\n"
        "To quit, use Ctrl + C.\n"
        "---------------------------------------------"
    )
    print(welcome_message)
    sys.stdout.write(f"> [*] Listening on localhost:{TCP_PORT}\n")
    sys.stdout.flush()

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, addr)
        )
        client_handler.start()


def server_thread():
    server = threading.Thread(target=start_server)
    server.daemon = True
    server.start()
    return server


def set_system_time(date, time):
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ts.py")
        params = f'"{script_path}" "{date}" "{time}"'
        if os.name == "nt":
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            if result <= 32:
                print(
                    f"Failed to execute script as admin, ShellExecuteW returned: {result}"
                )
        else:
            os.system(f"sudo python3 {params}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    try:
        server = server_thread()

        drop_privileges()

        while True:
            command = input("> ").strip()
            if command.lower() == "exit":
                print("Shutting down server...")
                break
            else:
                response = handle_command(command)
                print(response)
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nServer exited.")
        sys.exit()
