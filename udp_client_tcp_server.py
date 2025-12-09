# imports needed for networking, threading, random message generation, and timing
import socket
import threading
import random
import string
import time


REMOTE_MACHINE_IP = "172.17.113.167"  # IP address student B's machine (Xavier's)
UDP_CLIENT_LOCAL_PORT = 4000  # Local UDP port used by machine's UDP client
UDP_SERVER_REMOTE_PORT = 4001  # UDP port on the remote machine where UDP server listens
TCP_SERVER_LOCAL_PORT = 5500  # Local TCP port used by this machine's TCP server
UDP_SOCKET_TIMEOUT = 2.0  # Amount of time UDP client waits for a reply before retrying


def is_valid_message(message: str) -> bool:
    """
    Method that checks if a message contains any vowels.
    Returns true if message has NO vowels, False otherwise.
    """ 
    # Character set of vowels (both lowercase & uppercase)
    vowels = set("aeiouAEIOU")
    # Valid iff none of the characters are vowels
    return not any(ch in vowels for ch in message)


def tcp_server() -> None:
    """
    Method that runs a TCP server that validates messages and returns transformed ASCII values.
    """ 
    # Creates TCP/IP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allows quick rebinding to same port after restart
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind to all interfaces on the configured TCP port
    server_sock.bind(("", TCP_SERVER_LOCAL_PORT))
    # Start listening w/ backlog of 5 connections
    server_sock.listen(5)  
    # Log listening status for debugging and verification
    print(f"[TCP SERVER] Listening on port {TCP_SERVER_LOCAL_PORT}")  

    # Infinite loop that handles multiple incoming connections
    while True:  
        # Block until new TCP client connects
        client_sock, client_addr = server_sock.accept()  
        # Log who connected to the server
        print(f"[TCP SERVER] Connection from {client_addr}")  

        # Handle the connected client in separate function
        try:
            # Receive up to 1024 bytes from TCP client
            data = client_sock.recv(1024)  
            # Decode bytes to string and strip whitespace
            message = data.decode("utf-8").strip()  
            # Log the received message for debugging and verification
            print(f"[TCP SERVER] Received message: {message}")  

            # Check if message is valid (no vowels)
            if is_valid_message(message): 
                # Compute ASCII(c) + 41 for each character in message
                transformed_values = [ord(ch) + 41 for ch in message]  
                # Join values as space-separated string for response
                response_str = " ".join(str(v) for v in transformed_values)  
                # Log response being sent
                print(f"[TCP SERVER] Valid message. Sending values: {response_str}")  

            # If message is invalid (contains vowels)
            else:
                # Indicate invalid message: send a single zero "0"
                response_str = "0" 
                 # Log invalid case
                print("[TCP SERVER] Invalid message (has vowels). Sending 0") 

            # Send response string encoded as bytes back to TCP client
            client_sock.sendall(response_str.encode("utf-8")) 

        # Ensure client socket is closed after handling
        finally:
            # Close client connection
            client_sock.close()
            # Log closure of connection
            print("[TCP SERVER] Connection closed")



def generate_random_3_letter_message() -> str:
    """
    Method to generate a random 3-letter lowercase message.
    """
    # Build random 3-letter string from lowercase letters
    return "".join(random.choice(string.ascii_lowercase) for _ in range(3))


def udp_client() -> None:
    """
    Method that runs a UDP client that keeps sending random 3-letter messages until it receives a response.
    """
    # Create UDP socket (IPv4, datagram)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind to local UDP port so replies can be received
    udp_sock.bind(("", UDP_CLIENT_LOCAL_PORT))
    # Configure timeout for recvfrom to avoid blocking forever
    udp_sock.settimeout(UDP_SOCKET_TIMEOUT)
    # Log bound port for debugging and verification
    print(f"[UDP CLIENT] Using local port {UDP_CLIENT_LOCAL_PORT}")

    # Infinite loop to keep sending messages until a response is received
    while True:
        # Generate random 3-letter message
        msg = generate_random_3_letter_message()
        # Encode string to bytes for sending
        encoded_msg = msg.encode("utf-8")  
        # Log message being sent for debugging and verification
        print(f"[UDP CLIENT] Sending 3-letter message: {msg}") 

        # Send UDP datagram to partner's UDP server (Xavier's) for testing code functionality
        udp_sock.sendto(encoded_msg, (REMOTE_MACHINE_IP, UDP_SERVER_REMOTE_PORT))  

        # Wait for UDP response w/ timeout handling
        try:
            # Wait for response from UDP server
            data, addr = udp_sock.recvfrom(1024)
            # Decode received bytes into string
            response = data.decode("utf-8").strip()
            # Log received response and sender address
            print(f"[UDP CLIENT] Received response '{response}' from {addr}")
            # Indicate protocol completion
            print("[UDP CLIENT] Finished - response received. Exiting.")

            # Exit from loop since we got a response (via requirement for project)
            break  

        # If no response is received within timeout period
        except socket.timeout:
            # Log timeout event and intention to retry
            print("[UDP CLIENT] No response (timeout). Will send a new random message...") 
            # Add small delay before retrying
            time.sleep(1.0)

    # Close UDP socket when finished
    udp_sock.close()
    # Log socket closure for debugging and verification
    print("[UDP CLIENT] Socket closed")


# Main execution block to start TCP server thread and run UDP client
if __name__ == "__main__":
    # Create background thread for TCP server
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    # Start TCP server in background
    tcp_thread.start()
    # Log indicating TCP server is running properly
    print("[MAIN] TCP server thread started")

    # Add small delay to ensure TCP server is listening before Xavier connects
    time.sleep(1.0)

    # Run UDP client in main thread to initiate protocol
    udp_client()

    # Log program termination for debugging and verification
    print("[MAIN] Program finished")
