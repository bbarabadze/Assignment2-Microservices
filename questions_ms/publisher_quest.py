import json


def publish_message(message):

    with open("../QuasiBroker.txt", "a") as f:
        f.write(json.dumps(message, indent=4) + "\n")
