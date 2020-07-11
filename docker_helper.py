import docker

IMAGE_NAME = 'ha-python'


class ApiDocker:
    def __init__(self):
        super().__init__()
        self.client = docker.from_env()

    def filter_container(self, container):
        return {'id': container.attrs['Id'], 'ip': container.attrs['NetworkSettings']['IPAddress']}

    def get_containers(self):
        running_containers = self.client.containers.list()
        container_custom_obj = [container for container in running_containers if container.attrs['Config']['Image'] == IMAGE_NAME]
        return container_custom_obj

    def set_container_count(self, count: int):
        running_containers = self.get_containers()
        if(len(running_containers) == count):
            return
        if(len(running_containers) < count):
            # Create new containers
            num_containers_to_create = count - len(running_containers)
            for i in range(num_containers_to_create):
                container = self.client.containers.run(image= IMAGE_NAME,detach=True)
                filtered = self.filter_container(container)
            
        if(len(running_containers) > count):
            # Remove existing containers
            num_containers_to_remove = len(running_containers) - count
            containers_to_remove = running_containers[0:num_containers_to_remove]
            for container in containers_to_remove:
                container.stop()
        running_containers = [self.filter_container(
            container) for container in self.get_containers()]