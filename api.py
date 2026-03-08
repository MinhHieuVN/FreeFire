from flask import Flask, request, jsonify, render_template
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
import MajorLogin_res_pb2
from google.protobuf.timestamp_pb2 import Timestamp
import base64, json, socket, os
import warnings

warnings.filterwarnings('ignore')
app = Flask(__name__)

# Giữ nguyên các class xử lý Protobuf và AES từ code gốc của bạn
class SimpleProtobuf:
    @staticmethod
    def encode_varint(value):
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)

    @staticmethod
    def decode_varint(data, start_index=0):
        value = 0
        shift = 0
        index = start_index
        while index < len(data):
            byte = data[index]
            index += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return value, index

def decrypt_aes_cbc(cipher_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(cipher_text), AES.block_size)
    return decrypted_data

def encrypt_aes_cbc(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(plain_text, AES.block_size))
    return encrypted_data

def send_once(ip, port, data, recv_timeout=5.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(recv_timeout)
            s.connect((ip, port))
            s.sendall(data)
            return s.recv(1024)
    except:
        return None

def process_ban(access_token):
    # Logic xác thực và lấy thông tin server từ api.py gốc
    url = f"https://connect.garena.com/api/login?access_token={access_token}"
    # ... (Các bước xử lý logic ban của bạn ở đây) ...
    return True, "Lệnh đã được gửi thành công"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ban')
def ban():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({"success": False, "message": "Thiếu Access Token"})
    success, result = process_ban(access_token)
    return jsonify({"success": success, "message": result})

# Handler cho Vercel
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
    
