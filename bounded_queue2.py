import hazelcast
import threading

client = hazelcast.HazelcastClient(
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"],
)

queue = client.get_queue("bounded-queue")


def produce():
    for i in range(100):
        queue.put(i)
        print("Produced: ", i)


producer = threading.Thread(target=produce)
producer.start()
producer.join()
