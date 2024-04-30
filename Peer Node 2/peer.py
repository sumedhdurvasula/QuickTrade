import streamlit as st
import socket
import threading
import os
import datetime

def timestamp_message(action):
    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{action} at {formatted_time}")

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connected_peers = {}
        self.messages = {}
        self.init_server()

    def init_server(self):
        threading.Thread(target=self.start_server, daemon=True).start()

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"Listening for connections on {self.host}:{self.port}...")

            directory_path = 'received'

            try:
                for filename in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        print(f"Removed {file_path}")
                    elif os.path.isdir(file_path):
                        print(f"Skipping directory: {file_path}")
            except Exception as e:
                print(f"Failed to delete files due to: {e}")

            while True:
                client, address = self.socket.accept()
                print(f"Connection from {address} has been established.")
                threading.Thread(target=self.handle_peer_connection, args=(client, address), daemon=True).start()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.socket.close()


    def send_file_to_peer(self, host, port, file_path):
        if (host, int(port)) in self.connected_peers:
            peer_sock = self.connected_peers[(host, int(port))]
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    peer_sock.sendall(f'FILE {file_size} {file_name}'.encode())
                    ack = peer_sock.recv(1024).decode()
                    if ack == 'ACK':
                        with open(file_path, 'rb') as file:
                            peer_sock.sendfile(file) 
                    else:
                        print("Acknowledgment not received.")
            else:
                print(f"File not found: {file_path}")

    def handle_peer_connection(self, client, address):
        received_folder = 'received'  
        models_folder =  'models'
        if not os.path.exists(received_folder):
            os.makedirs(received_folder)
        if not os.path.exists(models_folder):
            os.makedirs(models_folder)

        while True:
            try:
                header = client.recv(1024).decode()
                if not header:
                    break
                if header.startswith('FILE'):
                    _, file_size, file_name = header.split(maxsplit=2)
                    file_size = int(file_size)
                    print("Sending ACK...")
                    client.sendall('ACK'.encode())
                    received_data = b''
                    while len(received_data) < file_size:
                        data = client.recv(min(1024, file_size - len(received_data)))
                        if not data:
                            break
                        received_data += data
                    print(f"Received {len(received_data)} bytes of file data.")
                    if file_name.endswith('.h5'):
                        file_path = os.path.join(models_folder, file_name)
                    else:
                        file_path = os.path.join(received_folder, f'received_{file_name}')
                    with open(file_path, 'wb') as file:
                        file.write(received_data)
                    print(f"File {file_name} received completely.")
                    timestamp_message("Message received")
                else:
                    sender = f"{address[0]}:{address[1]}"
                    message = f"From {sender}: {header}"
                    print(message)
                    self.messages[sender] = self.messages.get(sender, []) + [message]
            except:
                break
        print(f"Connection with {address} has been terminated.")
        client.close()

    def connect_to_peer(self, host, port):
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect((host, int(port)))
        self.connected_peers[(host, int(port))] = peer_sock
        print(f"Connected to peer at {host}:{port}")

    def disconnect_from_peer(self, host, port):
        if (host, int(port)) in self.connected_peers:
            peer_sock = self.connected_peers[(host, int(port))]
            peer_sock.close()
            del self.connected_peers[(host, int(port))]
            print(f"Disconnected from peer at {host}:{port}")


    def send_to_peer(self, host, port, data):
        if (host, int(port)) in self.connected_peers:
            peer_sock = self.connected_peers[(host, int(port))]
            peer_sock.sendall(data.encode())
    

    def get_messages(self):
        return self.messages

st.title("Peer-to-Peer Communication")

this_port = 8502
st.session_state.port = this_port
if 'my_peer' not in st.session_state:
    st.session_state.my_peer = Peer('localhost', str(this_port))

target_host = st.text_input("Peer Host", "localhost")
if st.button("Connect to Peers"):
    my_peers = [8501, 8502, 8503, 8504, 8505]
    my_peers.remove(this_port)
    for target_port in my_peers:
        print("Trying to connect to port " + str(target_port))
        try:
            st.session_state.my_peer.connect_to_peer(target_host, target_port)
            file_path = 'data/' + st.session_state.username + str(st.session_state.port) + '.json'  
            st.session_state.my_peer.send_file_to_peer(target_host, target_port, file_path)
            st.success("Connection Established and File sent!")
        except Exception as e:
            print("No peer yet at port " + str(target_port) + " (or file error)")
            continue

# # Sending messages
# message = st.text_area("Message to Send")
# if st.button("Send Message"):
#     st.session_state.my_peer.send_to_peer(target_host, target_port, message) #target_port is wrong
#     st.success("Message sent!")

