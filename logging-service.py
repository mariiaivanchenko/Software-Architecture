import hazelcast
import configparser
from flask import Flask, request

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("configuration.ini")

CLUSTER_NAME = config.get("HAZELCAST", "CLUSTER_NAME").strip("")
CLUSTER_MEMBERS = [member.strip().strip('"') for member in config.get("HAZELCAST", "CLUSTER_MEMBERS").split(" , ")]
MEMBER_ID = int(config.get("HAZELCAST", "MEMBER_ID"))

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
            # db[message_entity["uuid"]] = message_entity["message"]
            distributed_map.put(message_entity["uuid"], message_entity["message"])
            print("Recieved messages: ", message_entity["message"])
    return "", 200


if __name__ == "__main__":
    app.run(debug=True)
