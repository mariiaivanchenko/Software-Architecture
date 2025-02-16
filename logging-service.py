from flask import Flask, request

app = Flask(__name__)

db = {}

@app.route("/logging-service", methods=["GET"])
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


@app.route("/logging-service", methods=['POST'])
def post():
    """
    Handling POST request from facade-service.
    """
    message_entity = request.get_json()
    if message_entity["message"] not in db.values():
        db[message_entity["uuid"]] = message_entity["message"]
        print("Recieved messages: ", message_entity["message"])
    return "", 200


#  flask --app logging-service run --port=5001
if __name__ == "__main__":
    app.run(debug=True)
