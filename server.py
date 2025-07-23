import socket
import threading
import json
import time
from datetime import datetime

class ChatServer:
    def __init__(self, host='192.168.1.100', port=8080):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = None
        self.running = False
    
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"> Chat Server started on {self.host}:{self.port}")
            print("> Waiting for clients to connect...")
            print("-" * 50)
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"> New connection from {address[0]}:{address[1]}")
                    

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"> Server error: {e}")
        finally:
            self.shutdown()
    
    def handle_client(self, client_socket, address):
        client_name = f"User_{address[1]}"
        self.clients[client_socket] = {
            'name': client_name,
            'address': address
        }
        

        welcome_msg = {
            'type': 'system',
            'message': f'Welcome to the chat! Your name is {client_name}',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.send_to_client(client_socket, welcome_msg)
        

        join_msg = {
            'type': 'system',
            'message': f'{client_name} joined the chat',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.broadcast_message(join_msg, exclude=client_socket)
        
        try:
            while self.running:

                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message_data = json.loads(data)
                    self.process_message(client_socket, message_data)
                except json.JSONDecodeError:
                    continue
                    
        except socket.error:
            pass
        finally:
            self.disconnect_client(client_socket)
    
    def process_message(self, client_socket, message_data):
        msg_type = message_data.get('type', 'message')
        
        if msg_type == 'name_change':
            old_name = self.clients[client_socket]['name']
            new_name = message_data.get('name', old_name)
            self.clients[client_socket]['name'] = new_name
            

            name_change_msg = {
                'type': 'system',
                'message': f'{old_name} changed their name to {new_name}',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            self.broadcast_message(name_change_msg)
            
        elif msg_type == 'message':

            client_name = self.clients[client_socket]['name']
            chat_msg = {
                'type': 'message',
                'sender': client_name,
                'message': message_data.get('message', ''),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            self.broadcast_message(chat_msg)
            print(f" {client_name}: {message_data.get('message', '')}")
    
    def broadcast_message(self, message, exclude=None):
        message_str = json.dumps(message)
        disconnected_clients = []
        
        for client_socket in self.clients:
            if client_socket == exclude:
                continue
            
            try:
                client_socket.send(message_str.encode('utf-8'))
            except socket.error:
                disconnected_clients.append(client_socket)
        

        for client in disconnected_clients:
            self.disconnect_client(client)
    
    def send_to_client(self, client_socket, message):
        try:
            message_str = json.dumps(message)
            client_socket.send(message_str.encode('utf-8'))
        except socket.error:
            self.disconnect_client(client_socket)
    
    def disconnect_client(self, client_socket):
        if client_socket in self.clients:
            client_name = self.clients[client_socket]['name']
            address = self.clients[client_socket]['address']
            
            print(f"> {client_name} ({address[0]}:{address[1]}) disconnected")
            

            leave_msg = {
                'type': 'system',
                'message': f'{client_name} left the chat',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            self.broadcast_message(leave_msg, exclude=client_socket)
            

            del self.clients[client_socket]
            
        try:
            client_socket.close()
        except:
            pass
    
    def shutdown(self):
        print("\n> Shutting down server...")
        self.running = False
        

        for client_socket in list(self.clients.keys()):
            self.disconnect_client(client_socket)
        

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("> Server shutdown complete")

def main():
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n> Server interrupted by user")
        server.shutdown()

if __name__ == "__main__":
    main()
