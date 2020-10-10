import socket
import configparser
import subprocess
import datetime

# Chargement de la configuration du port depuis config.ini
config = configparser.ConfigParser()
config.read("src/NC/config.ini")
TCP_PORT = int(config["NetworkClock"]["port"])


def get_current_time(format_string):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime(format_string)
    return formatted_time


def set_system_time(date, time):
    try:
        powershell_cmd = [
            "powershell.exe",
            "-Command",
            f"Start-Process py -ArgumentList ' \"src/SH/ts.py\" {date} {time}' -Verb RunAs",
        ]
        subprocess.check_call(" ".join(powershell_cmd), shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run script as admin: {e}")


def main():
    while True:
        print("\n1. Get current time")
        print("2. Set system time")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            format_input = input("Enter format string or 1 for default format: ")
            if format_input.startswith("1"):
                format_string = "%Y-%m-%d %H:%M:%S"  # Format par défaut
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
            set_system_time(new_time.split(" ")[0], new_time.split(" ")[1])

        elif choice == "3":
            break


if __name__ == "__main__":
    main()
