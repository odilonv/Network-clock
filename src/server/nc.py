import socket
import threading
import configparser
import datetime
import os
import ctypes
import sys
import re
import subprocess
import win32api
import win32security
import ntsecuritycon as con
import win32ts


# Function to determine the configuration path
def get_config_path():
    if os.name == "nt":  # Windows
        app_data = os.getenv("APPDATA")
        if app_data is None:
            raise EnvironmentError("APPDATA environment variable not set.")
        config_dir = os.path.join(app_data, "NetworkClock")
    else:
        raise EnvironmentError("This application only supports Windows OS.")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    return os.path.join(config_dir, "config.ini")


config_path = get_config_path()

# Ensure the configuration file exists with default values if not present
if not os.path.exists(config_path):
    config = configparser.ConfigParser()
    config["NetworkClock"] = {"port": "12345"}
    with open(config_path, "w") as configfile:
        config.write(configfile)

config = configparser.ConfigParser()
config.read(config_path)


# Validate the port value
def validate_port(port_str):
    try:
        port = int(port_str)
        if 1 <= port <= 65535:
            return port
        else:
            raise ValueError("Port number out of range")
    except ValueError as e:
        print(f"Invalid port value: {e}")
        sys.exit(1)


TCP_PORT = validate_port(config["NetworkClock"]["port"])

commands = {"yyyy": "%Y", "hh": "%H", "nn": "%M", "dd": "%d", "mm": "%m", "ss": "%S"}


def subscribe_to_dep():
    try:
        if os.name == "nt":
            ctypes.windll.kernel32.SetProcessDEPPolicy(1)
    except Exception as e:
        print(f"Error subscribing to DEP: {e}")


def drop_privileges():
    try:
        # On Windows, create a restricted token
        current_process = win32api.GetCurrentProcess()
        token = win32security.OpenProcessToken(
            current_process,
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY,
        )

        # Remove all privileges except SE_SYSTEMTIME_NAME
        privilege_names = [
            win32security.LookupPrivilegeName(None, privilege[0])
            for privilege in win32security.GetTokenInformation(
                token, win32security.TokenPrivileges
            )
        ]
        unnecessary_privileges = [
            win32security.LookupPrivilegeValue(None, privilege)
            for privilege in privilege_names
            if privilege != win32security.SE_SYSTEMTIME_NAME
        ]

        # Remove unnecessary privileges
        new_privileges = [
            (privilege, win32security.SE_PRIVILEGE_REMOVED)
            for privilege in unnecessary_privileges
        ]
        win32security.AdjustTokenPrivileges(token, False, new_privileges)

        # Enable SE_SYSTEMTIME_NAME privilege
        se_systemtime_privilege = [
            (
                win32security.LookupPrivilegeValue(
                    None, win32security.SE_SYSTEMTIME_NAME
                ),
                win32security.SE_PRIVILEGE_ENABLED,
            )
        ]
        win32security.AdjustTokenPrivileges(token, False, se_systemtime_privilege)

    except Exception as e:
        print(f"Error dropping privileges: {e}")


def sanitize_input(input_str):
    dangerous_formats = ["%n", "%s", "%x", "%i", "%o", "%u"]
    input_str = input_str.replace("%", "%%")
    for fmt in dangerous_formats:
        input_str = input_str.replace(fmt, "")
    return input_str


def validate_date_time(date_str, time_str):
    # Regex to match date in YYYY-MM-DD format
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    # Regex to match time in HH:MM:SS format
    time_pattern = r"^\d{2}:\d{2}:\d{2}$"

    if not re.match(date_pattern, date_str):
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    if not re.match(time_pattern, time_str):
        raise ValueError("Invalid time format. Use HH:MM:SS.")

    # Further validation for date and time values
    year, month, day = map(int, date_str.split("-"))
    hour, minute, second = map(int, time_str.split(":"))

    try:
        datetime.datetime(year, month, day, hour, minute, second)
    except ValueError as e:
        raise ValueError(f"Invalid date/time value: {e}")

    return True


def is_interactive_user():
    try:
        session_id = win32ts.WTSGetActiveConsoleSessionId()
        if session_id == -1:
            return False

        current_session_id = win32security.GetTokenInformation(
            win32security.OpenProcessToken(
                win32api.GetCurrentProcess(), win32security.TOKEN_QUERY
            ),
            win32security.TokenSessionId,
        )

        return session_id == current_session_id
    except Exception as e:
        print(f"Error checking interactive user: {e}")
        return False


def handle_command(command, addr, interactive):
    if command:
        try:
            # Sanitize the input command
            command = sanitize_input(command)

            # Check for the 'set' command
            if command.startswith("set "):
                if not interactive:
                    return (
                        "Permission denied. Only interactive users can set the time.\n"
                    )

                parts = command.split(" ")
                if len(parts) == 3:
                    date, time = parts[1], parts[2]
                    # Validate date and time
                    validate_date_time(date, time)
                    set_system_time(date, time)
                    return f"System time set to {date} {time}.\n"
                else:
                    return "Invalid set command format. Use: set yyyy-mm-dd hh:nn:ss\n"

            # Replace commands in the format string with datetime format strings
            for cmd, fmt in commands.items():
                command = command.replace(cmd, fmt)
            current_time = datetime.datetime.now().strftime(command)
            return current_time + "\n"
        except ValueError as e:
            return str(e) + "\n"
    else:
        return "No command received.\n"


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
                    response = handle_command(line, addr, False)
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
        "Available command format: set yyyy-mm-dd hh:nn:ss\n"
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
                print("Failed to execute script as admin.")
    except Exception as e:
        print(f"Error setting system time: {e}")


if __name__ == "__main__":
    try:
        subscribe_to_dep()
        drop_privileges()
        server = server_thread()

        while True:
            command = input("> ").strip()
            if command.lower() == "exit":
                print("Shutting down server...")
                break
            else:
                response = handle_command(command, None, True)
                print(response)
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nServer exited.")
        sys.exit()
