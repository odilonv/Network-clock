import socket
import time
import os
import configparser
import sys

import socket
import threading
import configparser
import datetime
import os
import ctypes
import sys
import win32api
import win32security
import ntsecuritycon as con


# Function to determine the configuration path
def get_config_path():
    if os.name == "nt":  # Windows
        app_data = os.getenv("APPDATA")
        config_dir = os.path.join(app_data, "NetworkClock")

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

allowed_commands = ["yyyy", "hh", "nn", "dd", "mm", "ss"]

commands = {"yyyy": "%Y", "hh": "%H", "nn": "%M", "dd": "%d", "mm": "%m", "ss": "%S"}


def handle_concatenated_command(command):
    for cmd in allowed_commands:
        command = command.replace(cmd, commands[cmd])
    return command


def try_connect():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(("localhost", TCP_PORT))
            return client_socket
        except ConnectionRefusedError:
            print("Unable to connect to the server, retrying...")
            time.sleep(1)


def handle_client(client_socket):
    accumulated_response = ""

    while True:
        # Print the accumulated response if there is one
        if accumulated_response:
            print(accumulated_response)
            accumulated_response = ""

        command = input("> ").strip()
        if command.lower() == "q":
            print("Quitting...")
            client_socket.close()
            break
        elif command.startswith("set "):
            print("The 'set' command is not allowed.")
        elif command == "_":
            # Print the accumulated response when only "_" is entered
            if accumulated_response:
                print(accumulated_response)
        else:
            # Split the command by "_", treating each segment separately
            parts = command.split("_")
            for i, part in enumerate(parts):
                if part:
                    processed_command = handle_concatenated_command(part)
                    try:
                        client_socket.send((processed_command + "\n").encode("utf-8"))
                        response = client_socket.recv(4096).decode("utf-8")
                        # Print the response for each part except the last one
                        if i < len(parts) - 1:
                            print(response, end="")
                        else:
                            # Store the response to be printed later
                            accumulated_response = response
                    except (
                        ConnectionAbortedError,
                        ConnectionResetError,
                        BrokenPipeError,
                        socket.timeout,
                    ):
                        print("Connection lost. Reconnecting...")
                        client_socket = try_connect()
                        print("Reconnected to the server.")
                        break


def main():
    print(
        "---------------------------------------------\n"
        "Client.\n"
        "Available commands: yyyy, hh, nn, dd, mm, ss\n"
        "To quit, type 'q' and press enter.\n"
        "To stop, use Ctrl + C.\n"
        "---------------------------------------------"
    )

    while True:
        client_socket = try_connect()
        print("Connected to the server.")
        handle_client(client_socket)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClient exited.")
        sys.exit()
