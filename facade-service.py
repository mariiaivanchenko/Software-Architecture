import uuid
import requests
from flask import Flask, request

app = Flask(__name__)

LOGGING_URL = "http://127.0.0.1:5001/logging-service"
MESSAGES_URL = "http://127.0.0.1:5002/messages-service"

# curl http://127.0.0.1:5000/facade-service
@app.route("/facade-service", methods=['GET'])
def get():
    """
    Handling GET request from client + Retry logic.
    """
    result_message = ""
    retry_attempts = 3

    while retry_attempts > 0:
        try:
            # # to test RETRY logic
            # if retry_attempts > 1:
            #     LOGGING_URL = "http://127.0.0.1:9999"
            # else:
            #     LOGGING_URL = "http://127.0.0.1:5001/logging-service"

            logging_response = requests.get(LOGGING_URL, timeout=3)
            messages_response = requests.get(MESSAGES_URL, timeout=3)

            if logging_response.status_code == 200 and messages_response.status_code == 200:
                result_message = (
                    "Logging response: "
                    + logging_response.text + "\n"
                    + "Messages response: "
                    + messages_response.text
                )
                return result_message, 200

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ) as e:
            print("Due to delays, poor connection or no response, exception occurred:", e)
            print("Retrying the operation.")

        retry_attempts -= 1

    return "Due to delays, poor connection or no response, exception occurred! \
    Retrying attempts are over.\n", 500


# curl -X POST -H "Content-Type: text/plain" -d msg http://127.0.0.1:5000/facade-service
@app.route("/facade-service", methods=['POST'])
def post():
    """
    Handling POST request from client + Retry logic. 
    """
    message = request.get_data(as_text=True)
    random_uuid = uuid.uuid4()
    data = {"uuid": str(random_uuid), "message": message}
    headers = {'Content-type': 'application/json'}

    retry_attempts = 3

    while retry_attempts > 0:
        try:
            # to test RETRY logic
            if retry_attempts > 1:
                LOGGING_URL = "http://127.0.0.1:9999"
            else:
                LOGGING_URL = "http://127.0.0.1:5001/logging-service"

            response = requests.post(LOGGING_URL, json=data, headers=headers, timeout=3)

            if response.status_code == 200:
                return "", response.status_code

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ) as e:
            print("Due to delays, poor connection or no response, exception occurred:", e)
            print("Retrying the operation.")

        retry_attempts -= 1

    return ("Due to delays, poor connection or no response, exception occurred! \
    Retrying attempts are over.\n", 500,)


# flask --app facade-service run
if __name__ == "__main__":
    app.run(debug=True)
