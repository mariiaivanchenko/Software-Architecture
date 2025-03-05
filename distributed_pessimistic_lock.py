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
        distributed_map.lock("key")
        try:
            value = distributed_map.get("key")
            value += 1
            distributed_map.put("key", value)
        finally:
            distributed_map.unlock("key")


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
