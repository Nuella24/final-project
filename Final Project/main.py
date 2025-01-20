from flask import Flask, request, render_template, send_file
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

KEY_FILE = "secret.key"

# Generate and save a key
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return "Key generated successfully!"

# Load the key from a file
def load_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return None

# Encrypt a file
def encrypt_file(file_path, output_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        original_data = file.read()
    encrypted_data = fernet.encrypt(original_data)
    with open(output_path, "wb") as file:
        file.write(encrypted_data)

# Decrypt a file
def decrypt_file(file_path, output_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_path, "wb") as file:
        file.write(decrypted_data)

@app.route("/")
def home():
    print("Serving index.html")
    return render_template("index.html")

@app.route("/generate_key", methods=["POST"])
def generate_key_route():
    try:
        print("Generate key route called")
        generate_key()
        return "Key generated and saved to 'secret.key'."
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

@app.route("/encrypt", methods=["POST"])
def encrypt_route():
    key = load_key()
    if not key:
        return "Key file not found. Please generate a key first."

    if "file" not in request.files:
        return "No file uploaded."

    file = request.files["file"]
    if file.filename == "":
        return "No selected file."

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_path = os.path.join(UPLOAD_FOLDER, f"encrypted_{file.filename}")
    encrypt_file(input_path, output_path, key)
    return send_file(output_path, as_attachment=True)

@app.route("/decrypt", methods=["POST"])
def decrypt_route():
    key = load_key()
    if not key:
        return "Key file not found. Please generate a key first."

    if "file" not in request.files:
        return "No file uploaded."

    file = request.files["file"]
    if file.filename == "":
        return "No selected file."

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_path = os.path.join(UPLOAD_FOLDER, f"decrypted_{file.filename}")
    try:
        decrypt_file(input_path, output_path, key)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error decrypting file: {e}"

if __name__ == "__main__":
    app.run(debug=True)
