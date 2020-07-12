import psutil, sched, time
from container_helper import ContainerHelper

DELAY_SECONDS = 10
PRIORITY = 1
scheduler = sched.scheduler(time.time, time.sleep)
container_helper = ContainerHelper()

# Schedules a new event
def schedule_event():
    print(f'scheduling monitoring after {DELAY_SECONDS} seconds')
    scheduler.enter(delay=DELAY_SECONDS, priority=PRIORITY, action=monitor_usage)

# Monitors cpu usage and updates containers
def monitor_usage():
    cpu_usage = psutil.cpu_percent()
    print(f'CPU usage is {cpu_usage}')
    number_of_containers = 1 if cpu_usage < 10 else int(cpu_usage/10)
    print(f'setting docker container count to {number_of_containers}')
    # Set the container count to desired number of containers
    container_helper.set_container_count(number_of_containers)
    # Schedule another event after this event completes
    schedule_event()
try:
    schedule_event()
    print("Starting scheduler")
    scheduler.run()
except KeyboardInterrupt:
    pass
finally:
    print('stopping running containers')
    container_helper.stop()