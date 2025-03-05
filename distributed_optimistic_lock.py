import hazelcast
import threading
import time

client = hazelcast.HazelcastClient(
    cluster_name="hello-world",
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"],
)

distributed_map = client.get_map("distributed-map").blocking()
distributed_map.put("key", 0)


def increment_map():
    for _ in range(10000):
        while True:
            value = distributed_map.get("key")
            new_value = value + 1
            if distributed_map.replace_if_same("key", value, new_value):
                break


threads = []
start_time = time.time()
for _ in range(3):
    t = threading.Thread(target=increment_map)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

end_time = time.time()
print("Count value: ", distributed_map.get("key"))
print("Time taken: ", end_time - start_time)
