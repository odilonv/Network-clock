import socket
import threading
import configparser
import datetime
import subprocess

# Chargement de la configuration du port depuis config.ini
config = configparser.ConfigParser()
config.read('src/NC/config.ini')
TCP_PORT = int(config['NetworkClock']['port'])

def handle_client(client_socket):
    # Fonction pour gérer une connexion client
    request = client_socket.recv(4096).decode('utf-8').strip()
    
    # Traitement de la requête
    if request.startswith("GETTIME:"):
        format_str = request.split(":", 1)[1].strip()
        try:
            current_time = datetime.datetime.now().strftime(format_str)
            client_socket.send(current_time.encode('utf-8'))
        except ValueError:
            client_socket.send("Invalid format string.".encode('utf-8'))
    
    elif request.startswith("SETTIME:"):
        new_time = request.split(":", 1)[1].strip()
        result = set_system_time_through_ts(new_time)
        client_socket.send(result.encode('utf-8'))
    
    client_socket.close()

def set_system_time_through_ts(new_time):
    # Appel du programme TS pour définir l'heure système
    try:
        result = subprocess.run(['python', 'src/SH/ts.pyw', new_time], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Failed to set system time: {str(e)}"
    
def start_server():
    # Fonction pour démarrer le serveur NC
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', TCP_PORT))
    server_socket.listen(5)
    print(f"[*] Listening on localhost:{TCP_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_server()
