from pyhaproxy.parse import Parser
from pyhaproxy.render import Render
import pyhaproxy.config as config
import os

CONFIG_PATH = '/etc/haproxy/haproxy.cfg'

SERVICE_PORT = '5000'

BACKEND_NAME = 'flask_backend'

INVALIDATE_CONFIG_COMMAND = 'sudo systemctl restart haproxy'

def create_server(name, host):
    server = config.Server(
        name=name, host=host, port=SERVICE_PORT, attributes=['check'])
    return server

def set_containers(containers):
    # Read the current configuration and parse it
    parser = Parser(CONFIG_PATH)
    configuration = parser.build_configuration()
    backend = configuration.backend(BACKEND_NAME)

    # Remove all current servers from backend configuration
    configured_servers = backend.servers()
    for server in configured_servers:
        backend.remove_server(server.name)

    # Add servers according to the running docker containers
    for container in containers:
        server = create_server(name=container['id'], host=container['ip'])
        backend.add_server(server)

    # Update the ha proxy configuration
    config_render = Render(configuration)
    config_render.dumps_to(CONFIG_PATH)

    ## Restart the service for changes to take effect
    os.system(INVALIDATE_CONFIG_COMMAND)
