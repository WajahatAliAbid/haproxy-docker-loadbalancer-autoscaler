import docker
import time
import ha_proxy_utils

IMAGE_NAME = 'ha-python'

def get_slim_container_object(container):
        return {'id': container.attrs['Id'], 'ip': container.attrs['NetworkSettings']['IPAddress']}
class ContainerHelper:
    def __init__(self):
        super().__init__()
        self.client = docker.from_env()
        # start with 1 container
        self.set_container_count(1)

    # only get containers for the specified image
    def get_containers(self):
        running_containers = self.client.containers.list()
        container_custom_obj = [container for container in running_containers
                                if container.attrs['Config']['Image'] == IMAGE_NAME]
        return container_custom_obj

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

    def stop(self):
        # Stop all containers
        self.set_container_count(0)