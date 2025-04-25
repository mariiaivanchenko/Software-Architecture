import json
import threading
import configparser
from flask import Flask
from kafka import KafkaConsumer

app = Flask(__name__)
db = {}

config = configparser.ConfigParser()
config.read("configuration.ini")

TOPIC_NAME = config.get("KAFKA", "TOPIC_NAME")
MEMBER_ID = int(config.get("KAFKA", "MEMBER_ID"))

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=["localhost:29092", "localhost:39092", "localhost:49092"],
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
