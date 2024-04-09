from authentication import register_user, login_user, update_user_ip, get_ip_address
from discovery import discover_peers
from database import Session, User
import socket
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
is_running = True


def handle_client(client_socket):
    """Handles connections from other users."""
    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            logging.info(f"Received message: {message}")
    finally:
        client_socket.close()


def start_server(host, port):
    """Starts the server to listen for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    logging.info(f"Server is listening on {host}:{port}...")
    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Accepted connection from {addr}")
        threading.Thread(
            target=handle_client, args=(client_socket,), daemon=True
        ).start()


def send_messages(s):
    global is_running
    """Sends messages to another user."""
    while is_running:
        message = input("Enter your message: ")
        if message.lower() == "exit":
            is_running = False
            break
        s.sendall(message.encode("utf-8"))


def receive_messages(sock):
    global is_running
    """Receives messages from another user."""
    while is_running:
        try:
            message = sock.recv(1024).decode("utf-8")
            if not message:
                break
            print(f"\nReceived message: {message}")
        except ConnectionResetError:
            logging.error("Connection lost.")
            break
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            break


def main():
    global is_running
    print("Welcome to the P2P Chat Program")
    action = input("Do you want to [R]egister or [L]ogin? (R/L): ")
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    if action.lower() == "r":
        ip_address = get_ip_address()
        if register_user(username, password, ip_address):
            print("Registration successful!")
        else:
            print("Registration failed, please try again.")
            return
    elif action.lower() == "l":
        if login_user(username, password):
            print("Login successful!")
            update_user_ip(username)
        else:
            print("Login failed, please check your username and password.")
            return
    else:
        print("Unknown option, please try again.")
        return

    while True:
        choice = input("Choose an option: [D]iscovery, [C]hat, or [E]xit: ").lower()
        if choice == "d":
            peers = discover_peers()
            print("Online users:")
            for user in peers:
                print(f"Username: {user[0]}, IP: {user[1]}, Port: {user[2]}")
        elif choice == "c":
            host = "localhost"
            port = int(input("Please enter the port number you want to listen on: "))
            server_thread = threading.Thread(
                target=start_server, args=(host, port), daemon=True
            )
            server_thread.start()

            input("Press Enter to connect to another node...")

            peer_host = input("Enter the host address of the peer node: ")
            peer_port = int(input("Enter the port number of the peer node: "))
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                send_socket.connect((peer_host, peer_port))
                receive_thread = threading.Thread(
                    target=receive_messages, args=(send_socket,), daemon=True
                )
                receive_thread.start()
                send_thread = threading.Thread(
                    target=send_messages, args=(send_socket,)
                )
                send_thread.start()
                send_thread.join()
            except Exception as e:
                logging.error(f"Error connecting to the peer node: {e}")
            finally:
                if is_running:
                    is_running = False
                send_socket.shutdown(socket.SHUT_RDWR)
                send_socket.close()
                logging.info("Program has exited.")
        elif choice == "e":
            break  # Exit the program
        else:
            print("Unknown option, please try again.")


if __name__ == "__main__":
    main()
