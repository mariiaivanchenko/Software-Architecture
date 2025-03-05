import hazelcast
import threading

client = hazelcast.HazelcastClient(
    cluster_name="hello-world",
    cluster_members=["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"],
)
queue = client.get_queue("bounded-queue")


def produce():
    for i in range(100):
        queue.put(i)
    print("Producer finished.")


def consume():
    consumed_count = 0
    while consumed_count < 100:
        print("Consumed: ", queue.take().result())
        consumed_count += 1


threads = []
producer = threading.Thread(target=produce)
producer.start()
producer.join()

for _ in range(2):
    t = threading.Thread(target=consume)
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

client.shutdown()
