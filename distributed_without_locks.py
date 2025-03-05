import hazelcast
import threading

client = hazelcast.HazelcastClient(
    cluster_name="hello-world",
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"],
)

distributed_map = client.get_map("distributed-map").blocking()
distributed_map.put("key", 0)


def increment_map():
    for _ in range(10000):
        value = distributed_map.get("key")
        value += 1
        distributed_map.put("key", value)


threads = []
for _ in range(3):
    t = threading.Thread(target=increment_map)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Count value:", distributed_map.get("key"))
client.shutdown()
