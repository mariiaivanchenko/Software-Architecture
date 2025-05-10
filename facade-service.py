import uuid
import json
import signal
import random
import requests
import configparser
from consul import Consul
from functools import partial
from kafka import KafkaProducer
from flask import Flask, request
from utils import register_service, handle_term_signal, read_element_kv

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("configuration.ini")
FACADE_PORT = int(config.get("PORTS", "FACADE_PORT"))
TOPIC_NAME = read_element_kv("app/kafka/topic-name")
BOOTSTRAP_SERVERS = read_element_kv("app/kafka/bootstrap-servers").strip(",")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

register_service("facade-service", 1, FACADE_PORT)
signal.signal(
    signal.SIGTERM,
    partial(handle_term_signal, "facade-service", 1, FACADE_PORT),
)

@app.route("/facade-service", methods=["GET"])
def get():
    """
    Handling GET request from client + Retry logic.
    """
    result_message = ""
    retry_attempts = 3
    logging_url = choose_service("logging-service")
    messages_url = choose_service("messages-service")

    print("Choosed logging_url: ", logging_url)
    print("Choosed messages_url: ", messages_url)

    while retry_attempts > 0:
        try:
            logging_response = requests.get(logging_url, timeout=3)
            if messages_url != None:
                messages_response = requests.get(messages_url, timeout=3)

                if (
                    logging_response.status_code == 200
                    and messages_response.status_code == 200
                ):
                    result_message = (
                        "Logging response: "
                        + logging_response.text
                        + "\n"
                        + "Messages response: "
                        + messages_response.text
                    )
            else:
                if logging_response.status_code == 200:
                    result_message = (
                        "Logging response: "
                        + logging_response.text
                        + "\n"
                        + "Messages response: "
                        + "\n"
                    )

            return result_message, 200

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ) as e:
            print(
                "Due to delays, poor connection or no response, exception occurred:", e
            )
            print("Retrying the operation.")

        retry_attempts -= 1

    return (
        "Due to delays, poor connection or no response, exception occurred! \
    Retrying attempts are over.\n",
        500,
    )


@app.route("/facade-service", methods=["POST"])
def post():
    """
    Handling POST request from client + Retry logic.
    """
    retry_attempts = 3
    message = request.get_data(as_text=True)
    random_uuid = uuid.uuid4()
    data = {"uuid": str(random_uuid), "message": message}
    headers = {"Content-type": "application/json"}
    logging_url = choose_service("logging-service")
    print("Choosed logging_url: ", logging_url)

    while retry_attempts > 0:
        try:
            logging_response = requests.post(logging_url, json=data, headers=headers, timeout=3)

            producer.send(TOPIC_NAME, value=data)
            print(f"Sent to message queue: {data}")
            producer.flush()

            if (logging_response.status_code == 200):
                return "", 200

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ) as e:
            print(
                "Due to delays, poor connection or no response, exception occurred:", e
            )
            print("Retrying the operation.")

        retry_attempts -= 1

    return (
        "Due to delays, poor connection or no response, exception occurred! \
    Retrying attempts are over.\n",
        500,
    )


def choose_service(service_name):
    """
    Function to choose a service dynamically from Consul.
    """
    consul = Consul()
    health_services = consul.health.service(service_name)
    health_services = [
        "http://"
        + str(elem["Service"]["Address"])
        + ":"
        + str(elem["Service"]["Port"])
        + "/"
        + elem["Service"]["Service"]
        for elem in health_services[1]
    ]
    print("health_services: ", health_services)
    return random.choice(health_services)


if __name__ == "__main__":
    app.run(debug=True)
