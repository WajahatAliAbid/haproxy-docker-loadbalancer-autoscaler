# Docker Load Balancing and Auto Scaling using HAProxy
This repository demonstrates dockerizing a Flask API, and Load Balancing and Autoscaling it using HA Proxy and a python script. 

## Pre Requisites
1. ### Install Python 3.6
You should have [Python 3.6](https://www.python.org/downloads/release/python-360/) installed on your system. Python 3.7, 3.8 or 3.9 would also work for this.
2. ### Install HA Proxy
You should have [HA Proxy](http://www.haproxy.org/) installed on your system. The version used for this demonstration however is `1.8.8-1ubuntu0.10`.
3. ### Install Docker
You should've [Docker](https://docs.docker.com/get-docker/) installed on your system. 

## Steps

1. ### Build Flask API
Build a simple [Flask API](./api.py) with its GET / method to return a simple JSON Object running on port 5000.
```python
@app.route('/', methods=['GET'])
def get():
    return jsonify(hostname='{}, Wajahat Ali Abid'.format(socket.gethostname()))
```
There is an option to specify port number via environment variable `FLASK_PORT`, although we do not need it for this demonstration. Add a `requirements.txt` file as follows
```
flask==1.1.2
jsonify==0.5
```
and run the command
```bash
python3 -m pip install -r requirements.txt
```
This will download the dependencies for API. Run the following command to start the API
```bash
python3 api.py
```
and run the following command (or open the url http://localhost:5000 in your browser)
```bash
curl http://localhost:5000
```

2. ### Dockerize API
Use python 3.6 Alpine image for dockerizing this Flask API. 
```bash
FROM python:3.6-alpine
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ADD . /app
ENTRYPOINT [ "python3","api.py" ]
```
Build it using the following command
```bash
docker build -t ha-python .
```
and run it using command
```bash
docker run -p 5000:5000 ha-python
```
This will expose Flask API at port 5000. If you do not want to expose it on localhost, you can choose to not expose it and instead use the IP of container to call on the API.
```bash
docker run ha-python
```
List the running containers using command
```bash
docker container ls
```
To get the ip for the container, use the command
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id>
```
Use this ip to call the API
```bash
curl http://<container_id>:5000
```

3. ### Configure HA Proxy
4. ### Monitor the system
5. ### Test Autoscaling