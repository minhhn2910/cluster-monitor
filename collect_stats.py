import datetime
from fabric import SerialGroup, ThreadingGroup, Group
import threading
import json
from queue import Queue
global_res = Queue(maxsize=0)
def cpu_utils(c):
    # print ("running on {}".format(c.host))
    uname = c.run('uname -s', hide=True)
    if 'Linux' in uname.stdout:
        command = "top -bn1 | grep \"Cpu(s)\" | awk '{print $2 + $4 \"%\"}'"
        # command = "docker ps | grep taquangtrung | wc -l"
        res = c.run(command, hide=True).stdout.strip()
        command2 = "free | awk '/Mem/{printf(\"%.2f%%\\n\"), $3/$2*100}'"
        res2 = c.run(command2, hide=True).stdout.strip()
        # print (res)
        command3 = "docker ps | wc -l"
        # print (res)
        res3 = c.run(command3, hide=True).stdout.strip()
        global_res.put((int(c.host.split('-')[-1]), res, res2, res3))
        return
    print("No idea how to get disk space on {}!".format(uname))
worker_range = range(1,129)
all_hosts = [f'worker-{idx:03d}' for idx in worker_range]
all_worker_idx = list(worker_range)
# print (all_hosts[:5])
group = Group(*all_hosts)

threads = list()
for index in range(len(group)):

    x = threading.Thread(target=cpu_utils, args=(group[index],))
    threads.append(x)
    x.start()

for index, thread in enumerate(threads):
    thread.join()
print (global_res.qsize())
# print (list(global_res.queue))
all_results = list(global_res.queue)
all_results.sort(key=lambda x: x[0])
cpu_utils = list(map(lambda x: float(x[1].replace('%','')), all_results))
mem_usage = list(map(lambda x: float(x[2].replace('%','')), all_results))
docker_containers = list(map(lambda x: int(x[3]) - 1 , all_results))
# for when not all workers reply
worker_labels = list(map(lambda x: x[0], all_results))
print (worker_labels)
print ("unresponsive workers")
print (set(range(1, 129)) - set(worker_labels))
# print (cpu_utils)
# print (mem_usage)
# # print (new_res)

# Assuming the absence of a worker's data in worker_labels indicates unresponsiveness
all_workers = list(range(1,129))  # Adjust this if the total number of workers changes

# Initialize cpu_utils for all workers; if a worker is responsive, update its value from your data
full_cpu_utils = [-1] * 129
full_mem_usage = [0] * 129
full_docker_containers = [0] * 129
for i, label in enumerate(worker_labels):
    full_cpu_utils[label] = cpu_utils[i]
    full_mem_usage[label] = mem_usage[i]
    full_docker_containers[label] = docker_containers[i]
full_cpu_utils = full_cpu_utils[1:]
full_mem_usage = full_mem_usage[1:]
full_docker_containers = full_docker_containers[1:]

data_to_save = {
    "last_updated": str(datetime.datetime.now()),
    "labels": [f"worker-{idx:03d}" for idx in worker_labels],
    "cpu": full_cpu_utils,
    "ram": full_mem_usage,
    "docker": full_docker_containers,
    "unresponsive": list(set(all_workers) - set(worker_labels))
}

with open('public/data.json', 'w') as outfile:
    json.dump(data_to_save, outfile, indent=4)