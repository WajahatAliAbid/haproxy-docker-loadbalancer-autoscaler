from pyhaproxy.parse import Parser
from pyhaproxy.render import Render
import pyhaproxy.config as config
import uuid
CONFIG_PATH = './haproxy.cfg'

BACKEND_NAME = 'flask_backend'


def create_server(name, host):
    server = config.Server(
        name=name, host=host, port='5000', attributes=['check'])
    return server


def set_containers(containers):
    parser = Parser(CONFIG_PATH)
    configuration = parser.build_configuration()
    backend = configuration.backend(BACKEND_NAME)

    configured_servers = backend.servers()
    for server in configured_servers:
        backend.remove_server(server.name)

    for container in containers:
        server = create_server(name=container['id'], host=container['ip'])
        backend.add_server(server)
    config_render = Render(configuration)
    config_render.dumps_to(CONFIG_PATH)

