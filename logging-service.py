import atexit
import hazelcast
import configparser
from flask import Flask, request
from utils import register_service, deregister_service, read_element_kv

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("configuration.ini")

MEMBER_ID = int(config.get("HAZELCAST", "MEMBER_ID"))
LOGGING_PORT = int(config.get("PORTS", "LOGGING_PORT"))
register_service("logging-service", MEMBER_ID, LOGGING_PORT + MEMBER_ID)
atexit.register(lambda: deregister_service("logging-service", MEMBER_ID, LOGGING_PORT + MEMBER_ID))
CLUSTER_NAME = read_element_kv("app/hazelcast/cluster-name")
CLUSTER_MEMBERS = read_element_kv("app/hazelcast/cluster-members").split(",")

node = CLUSTER_MEMBERS[MEMBER_ID]

MEMBER_ID += 1
config.set("HAZELCAST", "MEMBER_ID", str(MEMBER_ID))
with open("configuration.ini", "w", encoding="utf-8") as configfile:
    config.write(configfile)


client = hazelcast.HazelcastClient(
    cluster_name=str(CLUSTER_NAME),
    cluster_members=[node],
)

distributed_map = client.get_map("distributed-map").blocking()

@app.route("/logging-service", methods=["GET"])
def get():
    """
    Handling GET request from facade-service.
    """
    messages = ""

    saved_messages = list(distributed_map.values())
    for i, elem in enumerate(saved_messages):
        if i != len(saved_messages) - 1:
            messages += elem + ", "
        else:
            messages += elem
    return messages


@app.route("/logging-service", methods=['POST'])
def post():
    """
    Handling POST request from facade-service.
    """
    message_entity = request.get_json()

    if message_entity["uuid"] not in distributed_map.values():
        if message_entity["message"] not in distributed_map.values():
            distributed_map.put(message_entity["uuid"], message_entity["message"])
            print("Recieved messages for logging: ", message_entity["message"])
    return "", 200


if __name__ == "__main__":
    app.run(debug=True)
