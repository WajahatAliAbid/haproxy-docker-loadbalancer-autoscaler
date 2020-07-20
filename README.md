# Load Balancing and Auto Scaling using HAProxy
This repository demonstrates dockerizing a Flask API, and Load Balancing and Autoscaling it using HA Proxy and a python script. 

## Pre Requisites
1. ### Install Python 3.6
You should have [Python 3.6](https://www.python.org/downloads/release/python-360/) installed on your system. Python 3.7, 3.8 or 3.9 would also work for this.

2. ### Install HA Proxy
You should have [HA Proxy](http://www.haproxy.org/) installed on your system. The version used for this demonstration however is `1.8.8-1ubuntu0.10`.

3. ### Install [Docker](https://docs.docker.com/get-docker/)

## Steps

1. ### Build Flask API
Build a simple [Flask API](./api/api.py) running on port 5000. Having a GET / method  which will return a simple JSON Object with host name of the system.
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
curl http://<container_ip>:5000
```

3. ### Configure HA Proxy
Launch two docker containers for `ha-python` and get their IPs. Assuming the IPs for two docker containers are 172.21.0.2 and 172.21.0.3, add following configuration at the end of HA Proxy config (/etc/haproxy/haproxy.cfg)
```
frontend flask_frontend
    	bind 		*:5000
    	mode 		http
    	default_backend flask_backend

backend flask_backend
    	balance 	roundrobin
    	server 		node1 172.21.0.2:5000 check
    	server 		node2 172.21.0.3:5000 check
```
This will expose our API at port 5000, while load balancing using round-robin approach between node1 and node2. Restart the service using 
```bash
sudo systemctl restart haproxy
```
and open localhost at port 5000 or run the command
```bash
curl http://localhost:5000
```
This will return different host name (alternatively) each time you hit this API. This verifies that load balancing is working as expected.

4. ### Monitor & Autoscale

In a real world scenerio, you may want to autoscale based on some matrix, for example CPU or memory usage. For this example, consider autoscaling using CPU utlization as a matrix for autoscaling; when CPU utilization is less than 10%, we'll have a single container running, otherwise we'll use the following equation to calculate the number of docker docker containers.
``` python
number_of_containers = int(cpu_percentage / 10)
```
Based on number of containers we require and the number of currently running containers we'll need to start new containers or stop existing containers. Whenever a new container is created, we'll need to update the HA Proxy configuration to add entry for that container so HA Proxy can route to it. Whenever a container is removed, we'll need to update HA Proxy configuration to remove that entry. 

To achieve this, create a new requirements file, this time for the monitoring scripts.
```
psutil==5.7.0
docker==4.2.2
haproxy==0.3.7
```
Here `psutil` is used for monitoring cpu usage, `docker` is used to manage docker containers and `haproxy` is used to manage server entries in HA Proxy config file.

1. #### Monitor CPU Usage
[This script](./monitor.py) uses [sched](https://docs.python.org/3/library/sched.html) module to contineously monitor the CPU usage after set amount of time. In our case, we've configured it to every 3 seconds using `DELAY_SECONDS`, but it can be changed in the code easily. When the script starts, it sets running docker containers to 1 and updates the HA Proxy configuration. In the initializer of `ContainerHelper`, we call the function to set number of running containers to 1. 

When the script starts we call `schedule_event()` function, which is defined as 
```python
def schedule_event():
    scheduler.enter(delay=DELAY_SECONDS, priority=PRIORITY, action=monitor_usage)
```
and the `monitor_usage` function is defined as 
```python
def monitor_usage():
    cpu_usage = psutil.cpu_percent()
    print(f'CPU usage is {cpu_usage}')
    number_of_containers = 1 if cpu_usage < 10 else int(cpu_usage/10)
    print(f'setting docker container count to {number_of_containers}')
    # Set the container count to desired number of containers
    container_helper.set_container_count(number_of_containers)
    # Schedule another event after this event completes
    schedule_event()
```
When `scheduler.run()` function is called, the scheduler invokes `monitor_usage` function, which in turn gets the current cpu percentage, calculates the number of containers there should be running and and instructs container_helper to set the number of running containers to the calculated count. Once its done, it'll reschedule execution of `monitor_usage` function after set amount of time.

2. #### Handle Docker Containers
For docker containers, [this script](./container_helper.py) will assume you've docker image named as `ha-python`. Class `ContainerHelper` has a function `set_containers_count(self, count:int)` which updates the count of running docker containers to desired amount. It desides whether to remove the containers or add new ones.
```python
def set_container_count(self, count: int):
    running_containers = self.get_containers()
    # If numbers of running contaienrs match with desired count then do nothing
    # If number of running containers is less than desried count, then create containers to match desired count
    if(len(running_containers) < count):
        num_containers_to_create = count - len(running_containers)
        for i in range(num_containers_to_create):
            container = self.client.containers.run(
                image=IMAGE_NAME, detach=True)

    # If number of running containers is greater than desried count, then stop containers to match desired count
    elif(len(running_containers) > count):
        num_containers_to_remove = len(running_containers) - count
        containers_to_remove = running_containers[0:num_containers_to_remove]
        for container in containers_to_remove:
            container.stop()
    # get the ip and id for each container that we require to update the ha proxy config
    running_containers = [get_slim_container_object(container) for container in self.get_containers()]
    # update ha proxy config
    ha_proxy_utils.set_containers(running_containers)
    return running_containers
```
After updating containers, it'll update the HAProxy using [ha_proxy_utils](./ha_proxy_utils.py).

3. #### Manage HA Proxy Config
For HA Proxy, [this script](./ha_proxy_utils.py) will assume that you've backend name set as `flask-backend` as defined above and will add entries for docker containers to the said backend. This function is defined as 

```python
INVALIDATE_CONFIG_COMMAND = 'sudo systemctl restart haproxy'
def set_containers(containers):
    # Read the current configuration and parse it
    parser = Parser(CONFIG_PATH)
    configuration = parser.build_configuration()
    backend = configuration.backend(BACKEND_NAME)

    # remove all current servers from backend configuration
    configured_servers = backend.servers()
    for server in configured_servers:
        backend.remove_server(server.name)

    # add servers according to the running docker containers
    for container in containers:
        server = create_server(name=container['id'], host=container['ip'])
        backend.add_server(server)

    # update the ha proxy configuration
    config_render = Render(configuration)
    config_render.dumps_to(CONFIG_PATH)

    # Restart the service for changes to take effect
    os.system(INVALIDATE_CONFIG_COMMAND)
```
The function `create_server` is defined as follows
```python
def create_server(name, host):
    server = config.Server(
        name=name, host=host, port=SERVICE_PORT, attributes=['check'])
    return server
```
This script will read the current HA Proxy configuration, update the server entries according to currently running contianers for the image `ha-python`, update the configuration and restart the service for changes to take effect.

5. ### Testing
Run the `monitor.py` using 
```python
sudo python3 monitor.py
```
We're running using sudo privilages, because updating HAProxy config and restarting service `haproxy` requires admin privilages. When we start the script, we'll have a single container running which we can find out by running 
```bash
docker container ls
```
We can also see a single entry for servers in the backend of `flask_backend` in HAProxy configuration file by using following command
```bash
cat /etc/haproxy/haproxy.config
```
Use the [stress tool](https://pypi.org/project/stress/) to increase the CPU load using the command
```bash
stress -c 4
```
CPU usage will immediately skyrocket and docker containers will start spawning as the monitor script observes the CPU usage increasing. This will also add entries in HAProxy config file which will result in different output when each time we open http://localhost:5000 on our system.

If we stop the stress tool, CPU usage will start going down and number of containers will decrease according to the CPU usage. This will also end up removing extra entries from HAProxy config. Eventually reducing to 1, which will result in http://localhost:5000 returning a single output for the single container running at the moment. 