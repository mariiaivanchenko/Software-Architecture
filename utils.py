import configparser
from consul import Consul

config = configparser.ConfigParser()
config.read("configuration.ini")
CONSUL_URL = config.get("URLS", "CONSUL_URL")

def register_service(service_name, member_id, port):
    """
    Function to register services to consul.
    """
    consul = Consul()
    consul.agent.service.register(
        name=f"{service_name}",
        service_id=f"{service_name}-{member_id}-{port}",
        address="127.0.0.1",
        port=port,
    )


def deregister_service(service_name, member_id, port):
    """
    Function to deregister services from consul.
    """
    сonsul = Consul()
    сonsul.agent.service.deregister(f"{service_name}-{member_id}-{port}")


def save_element_kv(key, element):
    """
    Function to save key and element data in key/value form using consul.
    """
    consul = Consul()
    consul.kv.put(key, element)


def read_element_kv(key):
    """
    Function to read key and element data in key/value form using consul.
    """
    consul = Consul()
    _, element = consul.kv.get(key)
    return element["Value"].decode("utf-8")


if __name__ == "__main__":
    save_element_kv("app/hazelcast/cluster-name", "hello-world")
    save_element_kv("app/hazelcast/cluster-members", "127.0.0.1:5701,127.0.0.1:5702,127.0.0.1:5703")
    save_element_kv("app/kafka/topic-name", "messages-topic")
    save_element_kv("app/kafka/bootstrap-servers", "localhost:29092,localhost:39092,localhost:49092")
