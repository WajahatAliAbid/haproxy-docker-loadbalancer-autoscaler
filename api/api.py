import os
import socket
from flask import Flask, jsonify
app = Flask(__name__)
port_key = 'FLASK_PORT'


@app.route('/', methods=['GET'])
def get():
    return jsonify(host=socket.gethostname(),message='Hello')

if __name__ == '__main__':
    http_port = os.getenv(port_key,5000)
    app.run(host='0.0.0.0', debug=False, port=http_port)