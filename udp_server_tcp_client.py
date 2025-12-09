import socket  # Import socket module for network communication
import time  # Import time module for optional pauses

# ====================== CONFIGURATION SECTION ======================

REMOTE_TCP_SERVER_IP = "127.0.0.1"  # IP address of the other student's machine (its TCP server)
REMOTE_TCP_SERVER_PORT = 5000  # TCP port number where the other machine's TCP server listens

UDP_SERVER_LOCAL_PORT = 4001  # UDP port on this machine where we act as the UDP server

# ====================== UDP SERVER + TCP CLIENT (THIS MACHINE) ======================

def handle_single_udp_request(udp_sock: socket.socket) -> None:
    """
    Handle exactly one incoming UDP message, contact the TCP server,
    and possibly send a UDP reply back.
    """
    data, client_addr = udp_sock.recvfrom(1024)  # Receive datagram and address of original sender
    message = data.decode("utf-8").strip()  # Decode bytes to string and strip whitespace
    print(f"[UDP SERVER] Received 3-letter message '{message}' from {client_addr}")  # Log received message

    reversed_message = message[::-1]  # Reverse the string (e.g., "abc" -> "cba")
    print(f"[UDP SERVER] Reversed message to send over TCP: '{reversed_message}'")  # Log reversed message

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP client socket (IPv4, stream)

    try:
        tcp_sock.connect((REMOTE_TCP_SERVER_IP, REMOTE_TCP_SERVER_PORT))  # Connect to remote TCP server
        print(f"[TCP CLIENT] Connected to TCP server at {(REMOTE_TCP_SERVER_IP, REMOTE_TCP_SERVER_PORT)}")  # Log connect

        tcp_sock.sendall(reversed_message.encode("utf-8"))  # Send reversed message to TCP server
        print(f"[TCP CLIENT] Sent reversed message '{reversed_message}'")  # Confirm what was sent

        tcp_response_bytes = tcp_sock.recv(1024)  # Receive server's response (either "0" or three numbers)
        tcp_response_str = tcp_response_bytes.decode("utf-8").strip()  # Decode bytes into string
        print(f"[TCP CLIENT] Received response from TCP server: '{tcp_response_str}'")  # Log raw response

        if tcp_response_str == "0":  # If TCP server indicates invalid message
            print("[UDP SERVER] TCP server returned 0 (invalid). NOT sending UDP reply.")  # Requirement: no reply
            return  # End handling for this request without replying
        else:
            try:
                values = [int(x) for x in tcp_response_str.split()]  # Split into parts and convert to integers
                total = sum(values)  # Sum the three ASCII+41 values
                print(f"[UDP SERVER] Sum of ASCII+41 values: {total}")  # Log computed sum

                reply_bytes = str(total).encode("utf-8")  # Encode sum as bytes
                udp_sock.sendto(reply_bytes, client_addr)  # Send UDP reply back to original UDP client
                print(f"[UDP SERVER] Sent UDP reply '{total}' back to {client_addr}")  # Log reply
            except ValueError:  # If conversion to integers fails
                print("[UDP SERVER] ERROR: Could not parse numbers from TCP response.")  # Log parsing error
    finally:
        tcp_sock.close()  # Close TCP connection regardless of success/failure
        print("[TCP CLIENT] TCP connection closed")  # Log TCP connection closure


def udp_server_loop() -> None:
    """Main loop for UDP server that also acts as a TCP client."""  # Describe loop behavior
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket (IPv4, datagram)
    udp_sock.bind(("", UDP_SERVER_LOCAL_PORT))  # Bind to all interfaces on given UDP port
    print(f"[UDP SERVER] Listening for UDP on port {UDP_SERVER_LOCAL_PORT}")  # Log listening status

    while True:  # Infinite loop to handle incoming requests
        handle_single_udp_request(udp_sock)  # Process one request (including TCP interaction, if any)
        time.sleep(0.1)  # Short delay to avoid a tight loop (optional)


# ====================== MAIN ENTRY POINT ======================

if __name__ == "__main__":  # Only run when script is executed directly
    udp_server_loop()  # Start the UDP server main loop
