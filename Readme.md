# Autoscaling and Load Balancing a Web Application
## Overview
Load balancing in cloud computing is the process in which workloads and computing resources are distributed across more than one servers. The workload is divided among two or more servers, network interfaces, hard drives and other computing resources which result in better utilization and system response time, whereas, auto-scaling is a way to automatically scale up or down the number of compute resources that are being allocated to your application based on its needs at any given time.

There are a number of ways to autoscale and load balance your applications using a wide range of tools available. In this example, We'll demonstrate auto scaling and layer 4 load balancing of a Web API using nothing but open source tools. 

Basic architecture of the implementation looks like this:
![Architecture Diagram](./res/main%20diagram.jpeg)

## Explanation of Architecture
At the center of the system lies [HA Proxy](http://www.haproxy.org/) which is free, and [open source](https://github.com/haproxy/haproxy) software that provides a high availability load balancer and proxy server for TCP and HTTP-based applications that spreads requests across multiple servers. While on the right side is the auto scaler script, which is responsible for launching or destroying docker containers based on the auto scaling matrix. 
Whenever a new docker container is launched by the script, the HA Proxy is notified about it. HA Proxy then adds this container to its load balancing group. In case a docker container is removed from the group, HA Proxy removes the container from its load balancing group.
## Environment Setup
To setup this environment, you need to have following components installed on your system.
1. HA Proxy
2. Docker
3. Python

### Steps
#### 1. Build Docker Image
```bash
docker build -t ha-python ./api
```
#### 2. Configure HA Proxy
Add the following text in the ha proxy configuration file (/etc/haproxy/haproxy.cfg).
```
frontend flask_frontend
    	bind 		*:80
    	mode 		http
    	default_backend flask_backend

backend flask_backend
    	balance 	roundrobin
```
#### 3. Run the autoscaler script
Install the required dependencies by running the command
```bash
python3 -m pip install -r requirements.txt
```
Give script execution permissions
```bash
sudo chmod +x ./autoscaler.py
```
Run the script by running the command
```bash
./autoscaler.py
```

Open localhost in browser, and you'll be greeted with the following response
```json
{
    "host": "095dd8b087c0",
    "message": "Hello"
}
```
Where `095dd8b087c0` is the hostname of the docker container. Install the [stress](https://www.cyberciti.biz/faq/stress-test-linux-unix-server-with-stress-ng/) tool and run the command to impose stress on the cpu
```bash
stress -c 2
```
This will raise the system cpu usage and now each time you open localhost, you'll see a different host in the response.