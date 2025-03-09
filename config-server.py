import configparser
from flask import Flask, request

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("configuration.ini")


@app.route("/config-server", methods=["GET"])
def get():
    service_name = request.args.get("service_name", default="Guest", type=str)
    if service_name == "logging":
        logging_urls = [
            member.strip().strip('"')
            for member in config.get("URLS", "LOGGING_URLS").split(" , ")
        ]
        return " , ".join(logging_urls)

    if service_name == "messages":
        messages_url = config.get("URLS", "MESSAGES_URL")
        return messages_url

    return "Invalid service name", 400


if __name__ == "__main__":
    app.run(debug=True)
