import json
import signal
import threading
import configparser
from flask import Flask
from functools import partial
from kafka import KafkaConsumer
from utils import register_service, handle_term_signal, read_element_kv

app = Flask(__name__)
db = {}

config = configparser.ConfigParser()
config.read("configuration.ini")

MEMBER_ID = int(config.get("KAFKA", "MEMBER_ID"))
MESSAGES_PORT = int(config.get("PORTS", "MESSAGES_PORT"))
TOPIC_NAME = read_element_kv("app/kafka/topic-name")
BOOTSTRAP_SERVERS = read_element_kv("app/kafka/bootstrap-servers").split(",")

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers= BOOTSTRAP_SERVERS, 
    group_id=f"message_service{MEMBER_ID}_group",
    enable_auto_commit=True,
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

MEMBER_ID += 1
config.set("KAFKA", "MEMBER_ID", str(MEMBER_ID))
with open("configuration.ini", "w", encoding="utf-8") as configfile:
    config.write(configfile)

def consume_messages():
    for message in consumer:
        print(f"Received from messages queue (service {MEMBER_ID}): {message.value}")
        uuid = message.value['uuid']
        message = message.value['message']
        db[uuid] = message

threading.Thread(target=consume_messages, daemon=True).start()

register_service("messages-service", MEMBER_ID, MESSAGES_PORT + MEMBER_ID - 1)
signal.signal(
    signal.SIGTERM,
    partial(
        handle_term_signal, "messages-service", MEMBER_ID, MESSAGES_PORT + MEMBER_ID - 1
    ),
)

@app.route("/messages-service", methods=["GET"])
def get():
    """
    Handling GET request from facade-service.
    """
    messages = ""
    saved_messages = list(db.values())
    for i, elem in enumerate(saved_messages):
        if i != len(saved_messages) - 1:
            messages += elem + ", "
        else:
            messages += elem
    return messages


@app.route("/messages-service", methods=["POST"])
def post():
    """
    Handling POST request from facade-service.
    """
    return "Not implemented yet."

if __name__ == "__main__":
    app.run(debug=True)
