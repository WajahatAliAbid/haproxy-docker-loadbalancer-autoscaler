import psutil
import sched
import time

DELAY_SECONDS = 20
PRIORITY = 1
scheduler = sched.scheduler(time.time, time.sleep)


def schedule_event():
    scheduler.enter(time=DELAY_SECONDS, priority=PRIORITY,
                    action=monitor_usage)


def monitor_usage():
    cpu_usage = psutil.cpu_percent()
    number_of_containers = 1 if cpu_usage < 10 else int(cpu_usage/10)
    print(number_of_containers)
    #TODO: use this number to configure HA Proxy
    schedule_event()


schedule_event()
scheduler.run()
