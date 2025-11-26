import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import socket
import threading
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from encryption import ChatEncryption

class PyChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyCHAT - Encrypted Chat")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        load_dotenv()
        
        self.host = os.getenv('CLIENT_HOST', 'localhost')
        self.port = int(os.getenv('CLIENT_PORT', 12345))
        self.socket = None
        self.running = False
        self.username = "Anonymous"
        self.encryption = None
        self.key_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg='#2b2b2b')
        
        top_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(top_frame, text="PyCHAT", font=('Arial', 24, 'bold'), 
                               bg='#1e1e1e', fg='#00ff00')
        title_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(top_frame, text="● Disconnected", 
                                     font=('Arial', 12), bg='#1e1e1e', fg='#ff4444')
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        connection_frame = tk.Frame(self.root, bg='#2b2b2b')
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(connection_frame, text="Server:", bg='#2b2b2b', 
                fg='#ffffff').pack(side=tk.LEFT, padx=5)
        self.host_entry = tk.Entry(connection_frame, width=20, bg='#1e1e1e', 
                                   fg='#ffffff', insertbackground='#ffffff')
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(connection_frame, text="Port:", bg='#2b2b2b', 
                fg='#ffffff').pack(side=tk.LEFT, padx=5)
        self.port_entry = tk.Entry(connection_frame, width=8, bg='#1e1e1e', 
                                   fg='#ffffff', insertbackground='#ffffff')
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(connection_frame, text="Username:", bg='#2b2b2b', 
                fg='#ffffff').pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(connection_frame, width=15, bg='#1e1e1e', 
                                       fg='#ffffff', insertbackground='#ffffff')
        self.username_entry.insert(0, self.username)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        key_frame = tk.Frame(self.root, bg='#2b2b2b')
        key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(key_frame, text="Encryption Key:", bg='#2b2b2b', 
                fg='#ffffff').pack(side=tk.LEFT, padx=5)
        self.key_label = tk.Label(key_frame, text="No key selected", 
                                  bg='#2b2b2b', fg='#ffaa00', font=('Arial', 9))
        self.key_label.pack(side=tk.LEFT, padx=5)
        
        self.select_key_btn = tk.Button(key_frame, text="Select Key File", 
                                        command=self.select_key_file,
                                        bg='#3a3a3a', fg='#ffffff', 
                                        activebackground='#4a4a4a')
        self.select_key_btn.pack(side=tk.LEFT, padx=5)
        
        self.generate_key_btn = tk.Button(key_frame, text="Generate New Key", 
                                          command=self.generate_new_key,
                                          bg='#3a3a3a', fg='#ffffff', 
                                          activebackground='#4a4a4a')
        self.generate_key_btn.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = tk.Button(connection_frame, text="Connect", 
                                     command=self.toggle_connection,
                                     bg='#00aa00', fg='#ffffff', 
                                     activebackground='#00cc00',
                                     font=('Arial', 10, 'bold'), width=12)
        self.connect_btn.pack(side=tk.RIGHT, padx=5)
        
        chat_frame = tk.Frame(self.root, bg='#2b2b2b')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, 
                                                       bg='#1e1e1e', fg='#ffffff',
                                                       font=('Consolas', 10),
                                                       state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display.tag_config('system', foreground='#ffaa00')
        self.chat_display.tag_config('own', foreground='#00ff00')
        self.chat_display.tag_config('other', foreground='#00aaff')
        self.chat_display.tag_config('timestamp', foreground='#888888')
        self.chat_display.tag_config('error', foreground='#ff4444')
        
        input_frame = tk.Frame(self.root, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.message_entry = tk.Entry(input_frame, bg='#1e1e1e', fg='#ffffff',
                                      font=('Arial', 11), insertbackground='#ffffff')
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.config(state=tk.DISABLED)
        
        self.send_btn = tk.Button(input_frame, text="Send", command=self.send_message,
                                  bg='#0066cc', fg='#ffffff', 
                                  activebackground='#0088ee',
                                  font=('Arial', 10, 'bold'), width=10,
                                  state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def select_key_file(self):
        filename = filedialog.askopenfilename(
            title="Select Encryption Key File",
            filetypes=[("Key Files", "*.key"), ("All Files", "*.*")]
        )
        if filename:
            self.key_file = filename
            self.encryption = ChatEncryption(filename)
            self.key_label.config(text=f"Key: {os.path.basename(filename)}", fg='#00ff00')
            self.add_message("System", f"Loaded encryption key: {os.path.basename(filename)}", 'system')
    
    def generate_new_key(self):
        filename = filedialog.asksaveasfilename(
            title="Save New Encryption Key",
            defaultextension=".key",
            filetypes=[("Key Files", "*.key"), ("All Files", "*.*")],
            initialfile="chat_key.key"
        )
        if filename:
            self.key_file = filename
            self.encryption = ChatEncryption(filename)
            self.key_label.config(text=f"Key: {os.path.basename(filename)}", fg='#00ff00')
            self.add_message("System", f"Generated new key: {os.path.basename(filename)}", 'system')
            messagebox.showinfo("Key Generated", 
                              f"New encryption key created!\n\nShare this file with other users:\n{filename}")
    
    def toggle_connection(self):
        if not self.running:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
    
    def connect_to_server(self):
        if not self.encryption:
            messagebox.showerror("No Encryption Key", 
                               "Please select or generate an encryption key first!")
            return
        
        self.host = self.host_entry.get().strip()
        try:
            self.port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Port", "Port must be a number!")
            return
        
        new_username = self.username_entry.get().strip()
        if new_username:
            self.username = new_username
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            self.status_label.config(text=f"● Connected as {self.username}", fg='#00ff00')
            self.connect_btn.config(text="Disconnect", bg='#aa0000', activebackground='#cc0000')
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.username_entry.config(state=tk.DISABLED)
            self.select_key_btn.config(state=tk.DISABLED)
            self.generate_key_btn.config(state=tk.DISABLED)
            
            self.add_message("System", f"Connected to {self.host}:{self.port}", 'system')
            
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            name_data = {
                'type': 'name_change',
                'name': self.username
            }
            name_str = json.dumps(name_data)
            self.socket.send(name_str.encode('utf-8'))
            
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to server:\n{e}")
            self.running = False
    
    def disconnect_from_server(self):
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.status_label.config(text="● Disconnected", fg='#ff4444')
        self.connect_btn.config(text="Connect", bg='#00aa00', activebackground='#00cc00')
        self.message_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.username_entry.config(state=tk.NORMAL)
        self.select_key_btn.config(state=tk.NORMAL)
        self.generate_key_btn.config(state=tk.NORMAL)
        
        self.add_message("System", "Disconnected from server", 'system')
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message_data = json.loads(data)
                self.process_received_message(message_data)
                
            except socket.error:
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error receiving message: {e}")
        
        if self.running:
            self.root.after(0, self.disconnect_from_server)
    
    def process_received_message(self, message_data):
        msg_type = message_data.get('type', 'message')
        timestamp = message_data.get('timestamp', '')
        
        if msg_type == 'system':
            message = message_data.get('message', '')
            self.add_message("System", message, 'system', timestamp)
        
        elif msg_type == 'message':
            sender = message_data.get('sender', 'Unknown')
            encrypted_message = message_data.get('message', '')
            
            decrypted_message = self.encryption.decrypt_message(encrypted_message)
            
            if sender == self.username:
                self.add_message("You", decrypted_message, 'own', timestamp)
            else:
                self.add_message(sender, decrypted_message, 'other', timestamp)
    
    def add_message(self, sender, message, tag, timestamp=None):
        self.chat_display.config(state=tk.NORMAL)
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        if not self.running:
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        if message.startswith('/'):
            self.handle_command(message)
            self.message_entry.delete(0, tk.END)
            return
        
        try:
            encrypted_message = self.encryption.encrypt_message(message)
            
            if encrypted_message is None:
                self.add_message("Error", "Failed to encrypt message", 'error')
                return
            
            message_data = {
                'type': 'message',
                'message': encrypted_message
            }
            message_str = json.dumps(message_data)
            self.socket.send(message_str.encode('utf-8'))
            
            self.message_entry.delete(0, tk.END)
            
        except socket.error:
            self.add_message("Error", "Failed to send message", 'error')
            self.disconnect_from_server()
    
    def handle_command(self, command):
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        
        if cmd == '/name':
            if len(parts) > 1:
                new_name = parts[1].strip()
                if new_name and len(new_name) <= 20:
                    old_name = self.username
                    self.username = new_name
                    
                    try:
                        name_data = {
                            'type': 'name_change',
                            'name': new_name
                        }
                        name_str = json.dumps(name_data)
                        self.socket.send(name_str.encode('utf-8'))
                        
                        self.status_label.config(text=f"● Connected as {self.username}")
                        self.add_message("System", f"Name changed to {new_name}", 'system')
                    except socket.error:
                        self.add_message("Error", "Failed to change name", 'error')
                else:
                    self.add_message("Error", "Invalid name (1-20 characters)", 'error')
            else:
                self.add_message("Error", "Usage: /name <new_name>", 'error')
        
        elif cmd == '/clear':
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
        
        elif cmd == '/quit':
            self.on_closing()
        
        else:
            self.add_message("Error", f"Unknown command: {cmd}", 'error')
    
    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("Quit", "Do you want to disconnect and quit?"):
                self.disconnect_from_server()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = PyChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()