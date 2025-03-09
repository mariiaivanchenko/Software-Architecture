from flask import Flask

app = Flask(__name__)

@app.route("/messages-service", methods=["GET"])
def get():
    """
    Handling GET request from facade-service.
    """
    return "Messages GET is not implemented yet.\n"

@app.route("/messages-service", methods=["POST"])
def post():
    """
    Handling POST request from facade-service.
    """
    return "POST from messages.\n"

if __name__ == "__main__":
    app.run(debug=True)
