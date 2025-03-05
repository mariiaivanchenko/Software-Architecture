import hazelcast
import uuid

if __name__ == "__main__":
    client = hazelcast.HazelcastClient(
        cluster_name="hello-world",
    )

    map = client.get_map("distributed-map").blocking()

    # write data
    for i in range(1000):
        map.put(i, uuid.uuid4())

    # read data
    for key, value in map.entry_set():
        print(key, value)

    client.shutdown()
