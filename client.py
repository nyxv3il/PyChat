import socket
import threading
import json
import os
import sys
import shutil
from datetime import datetime
from dotenv import load_dotenv

class PyChatClient:
    def __init__(self, host=None, port=None):
        load_dotenv()
        
        self.host = host or os.getenv('CLIENT_HOST', 'localhost')
        self.port = int(port or os.getenv('CLIENT_PORT', 12345))
        self.socket = None
        self.running = False
        self.username = "Anonymous"
        self.messages = []
        self.terminal_width = shutil.get_terminal_size().columns
        self.terminal_height = shutil.get_terminal_size().lines
        self.message_area_height = self.terminal_height - 6  
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def start(self):
        self.clear_screen()
        self.setup_terminal()
        
        if not self.connect():
            return
        
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        self.refresh_display()
        
        self.input_loop()
    
    def setup_terminal(self):
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    
    def cleanup_terminal(self):
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def refresh_display(self):
        self.clear_screen()
        self.show_header()
        self.show_messages()
        self.show_input_area()
    
    def show_header(self):
        header_line = "PyCHAT - Real-time Terminal Chat"
        status_line = f"Connected as: {self.username}"
        commands_line = "Commands: /name <new_name>, /clear, /quit"
        
        padding = (self.terminal_width - len(header_line)) // 2
        print("=" * self.terminal_width)
        print(" " * padding + header_line)
        print(f" Status: {status_line} | {commands_line}")
        print("=" * self.terminal_width)
    
    def show_messages(self):
        display_messages = self.messages[-(self.message_area_height - 1):]
        
        for i, msg in enumerate(display_messages):
            print(msg)
        
        remaining_lines = (self.message_area_height - 1) - len(display_messages)
        for _ in range(remaining_lines):
            print()
    
    def show_input_area(self):
        print("-" * self.terminal_width)
        print("Message: ", end="", flush=True)
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    
    def format_message(self, message_data, is_own=False):
        msg_type = message_data.get('type', 'message')
        timestamp = message_data.get('timestamp', '')
        
        if msg_type == 'system':
            message = message_data.get('message', '')
            formatted = f"[SYSTEM] [{timestamp}] {message}"
            if len(formatted) < self.terminal_width:
                padding = max(0, (self.terminal_width - len(formatted)) // 2)
                return " " * padding + formatted
            else:
                return formatted[:self.terminal_width-1]  
            
        elif msg_type == 'message':
            sender = message_data.get('sender', 'Unknown')
            message = message_data.get('message', '')
            
            message = message.replace('\n', ' ').replace('\r', ' ')
            
            if is_own:
                timestamp_part = f"[{timestamp}]"
                content = f"You: {message} {timestamp_part}"
                
                if len(content) < self.terminal_width - 1:
                    padding = max(0, self.terminal_width - len(content) - 1)
                    return " " * padding + content
                else:
                    max_msg_len = self.terminal_width - len("You: ") - len(timestamp_part) - 2
                    truncated_msg = message[:max_msg_len] + "..." if len(message) > max_msg_len else message
                    content = f"You: {truncated_msg} {timestamp_part}"
                    padding = max(0, self.terminal_width - len(content) - 1)
                    return " " * padding + content
            else:
                colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
                reset = '\033[0m'
                color = colors[hash(sender) % len(colors)]
                
                content = f"{color}{sender}{reset}: {message} [{timestamp}]"
                
                if len(content) > self.terminal_width - 1:
                    visible_length = len(f"{sender}: {message} [{timestamp}]")
                    if visible_length > self.terminal_width - 1:
                        max_msg_len = self.terminal_width - len(f"{sender}:  [{timestamp}]") - 4
                        truncated_msg = message[:max_msg_len] + "..." if len(message) > max_msg_len else message
                        content = f"{color}{sender}{reset}: {truncated_msg} [{timestamp}]"
                
                return content
        
        return ""
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message_data = json.loads(data)
                
                is_own = (message_data.get('type') == 'message' and 
                         message_data.get('sender') == self.username)
                
                formatted_msg = self.format_message(message_data, is_own)
                if formatted_msg:
                    self.messages.append(formatted_msg)
                    if len(self.messages) > 1000:
                        self.messages = self.messages[-500:]
                    
                    self.refresh_display()
                
            except socket.error:
                break
            except json.JSONDecodeError:
                continue
        
        if self.running:
            self.messages.append("[ERROR] Lost connection to server")
            self.refresh_display()
            self.running = False
    
    def input_loop(self):
        while self.running:
            try:
                user_input = input().strip()
                
                if not user_input:
                    self.refresh_display()
                    continue
                
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_message(user_input)
                
                self.refresh_display()
                    
            except KeyboardInterrupt:
                self.disconnect()
                break
            except EOFError:
                self.disconnect()
                break
    
    def handle_command(self, command):
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        cmd_display = f"You: {command} [{timestamp}]"
        cmd_padding = max(0, self.terminal_width - len(cmd_display) - 1)
        self.messages.append(f"{' ' * cmd_padding}{cmd_display}")
        
        if cmd == '/quit' or cmd == '/exit':
            self.disconnect()
            
        elif cmd == '/name':
            if len(parts) > 1:
                new_name = parts[1].strip()
                if new_name and len(new_name) <= 20:  
                    old_name = self.username
                    self.change_name(new_name)
                    success_msg = f"[SUCCESS] Name changed from {old_name} to {new_name}"
                    padding = max(0, self.terminal_width - len(success_msg) - 1)
                    self.messages.append(" " * padding + success_msg)
                else:
                    error_msg = "[ERROR] Please provide a valid name (1-20 characters)!"
                    padding = max(0, self.terminal_width - len(error_msg) - 1)
                    self.messages.append(" " * padding + error_msg)
            else:
                error_msg = "[ERROR] Usage: /name <new_name>"
                padding = max(0, self.terminal_width - len(error_msg) - 1)
                self.messages.append(" " * padding + error_msg)
                
        elif cmd == '/clear':
            self.messages.clear()
            
        else:
            error_msg = f"[ERROR] Unknown command: {cmd}. Available: /name, /clear, /quit"
            padding = max(0, self.terminal_width - len(error_msg) - 1)
            self.messages.append(" " * padding + error_msg)
    
    def send_message(self, message):
        if not self.running:
            return
        
        try:
            message_data = {
                'type': 'message',
                'message': message
            }
            message_str = json.dumps(message_data)
            self.socket.send(message_str.encode('utf-8'))
        except socket.error:
            self.messages.append("[ERROR] Failed to send message")
            self.running = False
    
    def change_name(self, new_name):
        if not self.running:
            return
        
        try:
            name_data = {
                'type': 'name_change',
                'name': new_name
            }
            name_str = json.dumps(name_data)
            self.socket.send(name_str.encode('utf-8'))
            self.username = new_name
        except socket.error:
            self.messages.append("[ERROR] Failed to change name")
            self.running = False
    
    def disconnect(self):
        self.messages.append("[INFO] Disconnecting from chat...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.cleanup_terminal()
        self.clear_screen()
        print("[INFO] Disconnected successfully!")
        print("Thank you for using PyCHAT!")
        sys.exit(0)

def main():
    print("PyCHAT Client v1.0")
    print("==================")
    print("Starting PyCHAT Client...")
    
    client = PyChatClient()
    
    try:
        client.start()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
