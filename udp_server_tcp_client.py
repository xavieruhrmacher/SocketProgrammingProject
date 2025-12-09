# Import modules needed for networking and measuring time
import socket 
import time 


# Config Variables
REMOTE_TCP_SERVER_IP = "172.17.104.255"  # IP address of TCP server (Scott's Laptop)
REMOTE_TCP_SERVER_PORT = 5500  # TCP server port number
UDP_SERVER_LOCAL_PORT = 4001  # UDP server port number


# Handle a single UDP request, connect to TCP server, and send reply message
def handle_single_udp_request(udp_sock: socket.socket) -> None:
    
    # Wait for a UDP datagram from a client, decode & print receieved message
    data, client_addr = udp_sock.recvfrom(1024)  
    message = data.decode("utf-8").strip()  
    print(f"[UDP SERVER] Received 3-letter message '{message}' from {client_addr}") 

    #Reverse the received message and print
    reversed_message = message[::-1] 
    print(f"[UDP SERVER] Reversed message to send over TCP: '{reversed_message}'") 

    #Connect to TCP server w/ socket
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_sock.connect((REMOTE_TCP_SERVER_IP, REMOTE_TCP_SERVER_PORT))
        print(f"[TCP CLIENT] Connected to TCP server at {(REMOTE_TCP_SERVER_IP, REMOTE_TCP_SERVER_PORT)}") #debug

        #Send reversed message over TCP
        tcp_sock.sendall(reversed_message.encode("utf-8"))  
        print(f"[TCP CLIENT] Sent reversed message '{reversed_message}'") 

        #Receive response from TCP server
        tcp_response_bytes = tcp_sock.recv(1024) 
        tcp_response_str = tcp_response_bytes.decode("utf-8").strip()  
        print(f"[TCP CLIENT] Received response from TCP server: '{tcp_response_str}'") 

        #If responde is "0", message is invalid so don't send reply message
        if tcp_response_str == "0":
            print("[UDP SERVER] TCP server returned 0, message is invalid.")
            return  
        #Otherwise, calculate the sum of the ASCII values
        else:
            values = [int(x) for x in tcp_response_str.split()]  #separate the numbers
            total = sum(values)  
            print(f"[UDP SERVER] Sum of ASCII+41 values: {total}") 

            #Send the sum back to client over UDP
            reply_bytes = str(total).encode("utf-8")  
            udp_sock.sendto(reply_bytes, client_addr) 
            print(f"[UDP SERVER] Sent UDP reply '{total}' back to {client_addr}") 
                
    #Close TCP connection at end of process            
    finally:
        tcp_sock.close() 
        print("[TCP CLIENT] TCP connection closed")

# Main UDP server loop, waits for client to send message
def udp_server_loop() -> None:
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    udp_sock.bind(("", UDP_SERVER_LOCAL_PORT)) 
    print(f"[UDP SERVER] Listening for UDP on port {UDP_SERVER_LOCAL_PORT}") 

    #listen for messages
    while True: 
        handle_single_udp_request(udp_sock) 
        time.sleep(0.1)


#Startup call
if __name__ == "__main__":  # Only run when script is executed directly
    udp_server_loop()  # Start the UDP server main loop
