import uuid
import json
import requests
import random
import configparser
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("configuration.ini")
CONFIG_URL = config.get("URLS", "CONFIG_URL")
TOPIC_NAME = config.get("KAFKA", "TOPIC_NAME")

producer = KafkaProducer(
    # bootstrap_servers=["localhost:9092", "localhost:9093", "localhost:9094"],
    bootstrap_servers=["localhost:29092", "localhost:39092", "localhost:49092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

@app.route("/facade-service", methods=["GET"])
def get():
    """
    Handling GET request from client + Retry logic.
    """
    result_message = ""
    retry_attempts = 3
    count = 10

    config_url_logging = CONFIG_URL + "?service_name=logging"
    config_url_messages = CONFIG_URL + "?service_name=messages"

    logging_addresses_response = requests.get(config_url_logging, timeout=3)
    messages_addresses_response = requests.get(config_url_messages, timeout=3)

    logging_addresses = logging_addresses_response.text.split(" , ")
    messages_addresses = messages_addresses_response.text.split(" , ")

    logging_url = choose_services(logging_addresses, count)
    messages_url = choose_services(messages_addresses, count)
    print("Choosed logging in GET: ", logging_url)
    print("Choosed messages in GET: ", messages_url)

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
    count = 10
    message = request.get_data(as_text=True)
    random_uuid = uuid.uuid4()
    data = {"uuid": str(random_uuid), "message": message}
    headers = {"Content-type": "application/json"}

    config_url_logging = CONFIG_URL + "?service_name=logging"
    logging_addresses_response = requests.get(config_url_logging, timeout=3)
    logging_addresses = logging_addresses_response.text.split(" , ")
    logging_url = choose_services(logging_addresses, count)
    print("Choosed logging in POST: ", logging_url)

    while retry_attempts > 0:
        try:
            logging_response = requests.post(logging_url, json=data, headers=headers, timeout=3)

            producer.send(TOPIC_NAME, value=data)
            print(f"Sent to message queue: {data}")
            producer.flush()
            # producer.close()

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


def choose_services(list, count):
    while count > 0:
        url = random.choice(list)
        count -= 1
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                count = 10
                return url
        except requests.RequestException as e:
            print(
                f"Service at {url} is down. Error: {e}. Trying another service."
            )
    print(f"All services is down.")

if __name__ == "__main__":
    app.run(debug=True)
