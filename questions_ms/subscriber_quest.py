import json
from pprint import pprint
from publisher_quest import publish_message
from db_calls_quest import check_question, change_status

def tail(filename):
    with open(filename, 'r') as file:
        file.seek(0, 2)  # Go to the end of the file

        while True:
            line = file.readline()
            if not line:
                continue
            yield line


def message_generator(tail_generator):

    message = ""  # error-is gasachumeblad

    for line in tail_generator:
        if line[0] == '{':
            message = line
        elif line[0] == '}':
            message += line
            yield json.loads(message)
        else:
            message += line



def process_msg(msg):

    if msg["message_type"] == "trans_status":
        change_status(msg["transaction_id"], msg["status"])
    elif msg["message_type"] == "check_question":

        result = check_question(msg["resource_id"])

        publish_message(
            {
                "transaction_id": msg['transaction_id'],
                "receiver_id": 2,
                "message_type": "trans_status",
                "status": "approved" if result else "rejected"
            }
        )

file_path = '../QuasiBroker.txt'


def subscriber():
    for msg in message_generator(tail(file_path)):
        if msg['receiver_id'] == 1:
            process_msg(msg)

