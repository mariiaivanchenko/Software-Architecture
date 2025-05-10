import configparser
from consul import Consul

import sys


config = configparser.ConfigParser()
config.read("configuration.ini")
CONSUL_URL = config.get("URLS", "CONSUL_URL")


def register_service(service_name, member_id, port):
    consul = Consul()

    service_id = f"{service_name}-{member_id}-{port}"

    consul.agent.service.register(
        name=service_name,
        service_id=service_id,
        address="127.0.0.1",
        port=port,
    )


def deregister_service(service_name, member_id, port):
    """
    Function to deregister services from consul.
    """
    сonsul = Consul()
    service_id = f"{service_name}-{member_id}-{port}"
    сonsul.agent.service.deregister(service_id)


def handle_term_signal(service_name, member_id, port, signal, frame):
    """
    Handle SIGTERM (graceful shutdown) and deregister the service.
    """
    deregister_service(service_name, member_id, port)
    sys.exit(0)


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
