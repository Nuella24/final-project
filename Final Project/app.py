from flask import Flask, render_template, request, redirect, url_for, send_file;
from cryptography.fernet import Fernet;
import os

app = Flask(__name__)

KEY_FILE = "secret.key"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_key():
    try:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return "Key generated successfully!"
    except Exception as e:
        return str(e), 500

def load_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return None
    
def encrypt_file(file_path, output_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        original_data = file.read()
    encrypted_data = fernet.encrypt(original_data)
    with open(output_path, "wb") as file:
        file.write(encrypted_data)

def decrypt_file(file_path, output_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_path, "wb") as file:
        file.write(decrypted_data)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_key", methods=["POST"])
def generate_key_route():
    try:
        print("Generate key route called")
        generate_key()
        return "Key generated and saved"
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

@app.route("/encrypt", methods=["POST"])
def encrypt_route():
    try:
        key = load_key()
        if key is None:
            return "No key found. Please generate a key.", 400
        if "file" not in request.files:
            return "No file uploaded.", 400
        
        file = request.files["file"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        encrypt_file(file_path, file_path + ".enc", key)
        return send_file(file_path + ".enc", as_attachment=True)
    except Exception as e:
        return str(e), 500

@app.route("/decrypt", methods=["POST"])
def decrypt_route():
    try:
        key = load_key()
        if key is None:
            return "No key found. Please generate a key.", 400
        
        if "file" not in request.files:
            return "No file uploaded.", 400
        
        file = request.files["file"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.splitext(file_path)[0]
        file.save(file_path)

        
        decrypt_file(file_path, output_path, key)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)