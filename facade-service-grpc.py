import grpc
import uuid
from flask import Flask, request
import micro_basics_pb2
import micro_basics_pb2_grpc

app = Flask(__name__)

channel = grpc.insecure_channel("127.0.0.1:5001")
stub = micro_basics_pb2_grpc.LoggingServiceStub(channel)


# curl http://127.0.0.1:5000/facade-service-grpc
@app.route("/facade-service-grpc", methods=["GET"])
def get():
    """
    Handling GET request from client + Retry logic.
    """
    retry_attempts = 3

    while retry_attempts > 0:
        try:
            response = stub.Get(micro_basics_pb2.Empty())
            return "Logging response: " + ", ".join(response.messages) + "\n", 200

        except grpc.RpcError as e:
            print(f"Error: {e}, Retrying...")

        retry_attempts -= 1

    return "Error: Failed after retries.\n", 500


# curl -X POST -H "Content-Type: text/plain" -d "Hello from facade" 127.0.0.1:5000/facade-service-grpc
@app.route("/facade-service-grpc", methods=["POST"])
def post():
    """
    Handling POST request from client + Retry logic.
    """
    message = request.get_data(as_text=True)
    random_uuid = str(uuid.uuid4())

    retry_attempts = 3

    while retry_attempts > 0:
        try:
            response = stub.Post(
                micro_basics_pb2.Message(uuid=random_uuid, message=message)
            )
            message = response.message + "\n"
            return message, response.status_code

        except grpc.RpcError as e:
            print(f"Error: {e}, Retrying...")

        retry_attempts -= 1

    return "Error: Failed after retries.\n", 500


if __name__ == "__main__":
    app.run(debug=True)
