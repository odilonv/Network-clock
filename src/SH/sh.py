import socket
import configparser
import ctypes
import os
import sys

config = configparser.ConfigParser()
config.read("src/NC/config.ini")
TCP_PORT = int(config["NetworkClock"]["port"])


def set_system_time(date, time):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "ts.py")

        params = f'"{script_path}" "{date}" "{time}"'
        print(f"Executing: python {params}")

        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )

        if result <= 32:
            print(
                f"Failed to execute script as admin, ShellExecuteW returned: {result}"
            )
        else:
            print(f"Script executed, ShellExecuteW returned: {result}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    while True:
        print("\n1. Get current time")
        print("2. Set system time")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            format_input = input("Enter format string or 1 for default format: ")
            if format_input.startswith("1"):
                format_string = "%Y-%m-%d %H:%M:%S"
            else:
                format_string = format_input

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect(("localhost", TCP_PORT))
                    client_socket.send(f"GETTIME:{format_string}".encode("utf-8"))
                    current_time = client_socket.recv(4096).decode("utf-8")
                    print(f"Current time: {current_time}")
            except ConnectionRefusedError:
                print(
                    f"Failed to connect to localhost:{TCP_PORT}. Is the server running?"
                )
            except ValueError:
                print("Invalid format string provided.")

        elif choice == "2":
            new_time = input("Enter new system time (YYYY-MM-DD HH:MM:SS): ")
            try:
                date, time = new_time.split(" ")
                set_system_time(date, time)
            except ValueError:
                print("Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS")

        elif choice == "3":
            break


if __name__ == "__main__":
    main()
