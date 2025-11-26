from cryptography.fernet import Fernet
import os
import json

class ChatEncryption:
    
    def __init__(self, key_file='pychat.key'):
        self.key_file = key_file
        self.cipher = None
        self.load_or_generate_key()
    
    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
            print(f"Loaded existing key from {self.key_file}")
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            print(f"Generated new key and saved to {self.key_file}")
        
        self.cipher = Fernet(key)
    
    def encrypt_message(self, message):
        try:
            encrypted = self.cipher.encrypt(message.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            print(f"Failed to encrypt: {e}")
            return None
    
    def decrypt_message(self, encrypted_message):
        try:
            decrypted = self.cipher.decrypt(encrypted_message.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Failed to decrypt: {e}")
            return "Cannot decrypt]"
    
    def get_key(self):
        with open(self.key_file, 'rb') as f:
            return f.read()
    
    def set_key(self, key):
        with open(self.key_file, 'wb') as f:
            f.write(key)
        self.cipher = Fernet(key)
        print("Updated encryption key")