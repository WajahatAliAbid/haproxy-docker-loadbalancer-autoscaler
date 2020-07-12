import psutil, sched, time
from container_helper import ContainerHelper

DELAY_SECONDS = 3
PRIORITY = 1
scheduler = sched.scheduler(time.time, time.sleep)
docker = ContainerHelper()

def schedule_event():
    print(f'scheduling monitoring after {DELAY_SECONDS} seconds')
    scheduler.enter(delay=DELAY_SECONDS, priority=PRIORITY, action=monitor_usage)


def monitor_usage():
    cpu_usage = psutil.cpu_percent()
    print(f'CPU usage is {cpu_usage}')
    number_of_containers = 1 if cpu_usage < 10 else int(cpu_usage/10)
    print(f'setting docker container count to {number_of_containers}')
    containers = docker.set_container_count(number_of_containers)
    schedule_event()
try:
    schedule_event()
    print("Starting scheduler")
    scheduler.run()
except KeyboardInterrupt:
    pass
finally:
    print('stopping running containers')
    docker.stop()