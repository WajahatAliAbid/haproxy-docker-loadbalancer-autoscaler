import os
import socket
from flask import Flask, request, jsonify
app = Flask(__name__)
port_key = 'HTTP_PORT'


@app.route('/', methods=['GET'])
def get():
    return jsonify(hostname='{}, Wajahat Ali Abid'.format(socket.gethostname()))

if __name__ == '__main__':
    http_port = os.getenv(port_key,5000)
    app.run(host='0.0.0.0', debug=False, port=http_port)