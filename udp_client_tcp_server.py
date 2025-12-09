import socket  # Import the socket module for networking
import threading  # Import threading to run server and client in parallel
import random  # Import random to generate random letters
import string  # Import string to get a list of alphabet letters
import time  # Import time to optionally sleep between retries

# ====================== CONFIGURATION SECTION ======================

REMOTE_MACHINE_IP = "127.0.0.1"  # IP address of the other student's machine (update this)
UDP_CLIENT_LOCAL_PORT = 4000  # Local UDP port used by this machine's UDP client
UDP_SERVER_REMOTE_PORT = 4001  # UDP port on the remote machine where its UDP server listens
TCP_SERVER_LOCAL_PORT = 5000  # Local TCP port used by this machine's TCP server

UDP_SOCKET_TIMEOUT = 2.0  # Seconds the UDP client waits for a reply before retrying

# ====================== TCP SERVER (THIS MACHINE) ======================

def is_valid_message(message: str) -> bool:
    """Return True if message has NO vowels, False otherwise."""  # Docstring explaining the function
    vowels = set("aeiouAEIOU")  # Set of characters considered vowels (both lowercase and uppercase)
    return not any(ch in vowels for ch in message)  # Valid iff none of the characters are vowels


def tcp_server() -> None:
    """TCP server that validates messages and returns transformed ASCII values."""  # Description of server behavior
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow quick rebinding to same port
    server_sock.bind(("", TCP_SERVER_LOCAL_PORT))  # Bind to all interfaces on the configured TCP port
    server_sock.listen(5)  # Start listening with a backlog of 5 connections
    print(f"[TCP SERVER] Listening on port {TCP_SERVER_LOCAL_PORT}")  # Log listening status

    while True:  # Infinite loop to handle multiple incoming connections
        client_sock, client_addr = server_sock.accept()  # Block until a new TCP client connects
        print(f"[TCP SERVER] Connection from {client_addr}")  # Log who connected

        try:
            data = client_sock.recv(1024)  # Receive up to 1024 bytes from the TCP client
            message = data.decode("utf-8").strip()  # Decode bytes to string and strip whitespace
            print(f"[TCP SERVER] Received message: {message}")  # Log the received message

            if is_valid_message(message):  # Check if message has no vowels (valid case)
                transformed_values = [ord(ch) + 41 for ch in message]  # Compute ASCII(c) + 41 for each character
                response_str = " ".join(str(v) for v in transformed_values)  # Join values as space-separated string
                print(f"[TCP SERVER] Valid message. Sending values: {response_str}")  # Log response
            else:
                response_str = "0"  # Invalid message: send a single zero
                print("[TCP SERVER] Invalid message (has vowels). Sending 0")  # Log invalid case

            client_sock.sendall(response_str.encode("utf-8"))  # Send response back over TCP
        finally:
            client_sock.close()  # Close the client connection to free resources
            print("[TCP SERVER] Connection closed")  # Log closure of connection


# ====================== UDP CLIENT (THIS MACHINE) ======================

def generate_random_3_letter_message() -> str:
    """Generate a random 3-letter lowercase message."""  # Docstring explaining generator
    return "".join(random.choice(string.ascii_lowercase) for _ in range(3))  # Build random 3-letter string


def udp_client() -> None:
    """UDP client that keeps sending random 3-letter messages until it receives a response."""  # Behavior description
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket (IPv4, datagram)
    udp_sock.bind(("", UDP_CLIENT_LOCAL_PORT))  # Bind to local UDP port so we can receive replies
    udp_sock.settimeout(UDP_SOCKET_TIMEOUT)  # Configure timeout for recvfrom to avoid blocking forever
    print(f"[UDP CLIENT] Using local port {UDP_CLIENT_LOCAL_PORT}")  # Log bound port

    while True:  # Keep trying until a response is received
        msg = generate_random_3_letter_message()  # Generate random 3-letter message
        encoded_msg = msg.encode("utf-8")  # Encode string to bytes for sending
        print(f"[UDP CLIENT] Sending 3-letter message: {msg}")  # Log message being sent

        udp_sock.sendto(encoded_msg, (REMOTE_MACHINE_IP, UDP_SERVER_REMOTE_PORT))  # Send UDP datagram to partner

        try:
            data, addr = udp_sock.recvfrom(1024)  # Wait for UDP response (may timeout)
            response = data.decode("utf-8").strip()  # Decode received bytes into string
            print(f"[UDP CLIENT] Received response '{response}' from {addr}")  # Log response and sender
            print("[UDP CLIENT] Finished - response received. Exiting.")  # Indicate protocol is complete
            break  # Exit loop because requirement says stop once a response is received
        except socket.timeout:  # If no UDP response arrived in timeout interval
            print("[UDP CLIENT] No response (timeout). Will send a new random message...")  # Log timeout
            time.sleep(1.0)  # Optional small delay before retrying to avoid spamming too fast

    udp_sock.close()  # Close UDP socket when finished
    print("[UDP CLIENT] Socket closed")  # Log socket closure


# ====================== MAIN ENTRY POINT ======================

if __name__ == "__main__":  # Only run this block when script is executed directly (not imported)
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)  # Create background thread for TCP server
    tcp_thread.start()  # Start TCP server in background
    print("[MAIN] TCP server thread started")  # Log that TCP server is running

    time.sleep(1.0)  # Small delay to be sure TCP server is listening before partner connects

    udp_client()  # Run UDP client in main thread to initiate protocol

    print("[MAIN] Program finished")  # Log program termination
