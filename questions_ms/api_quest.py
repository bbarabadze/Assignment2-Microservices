from fastapi import FastAPI, HTTPException
import uvicorn
from db_calls_quest import connection, check_question, add_question_db, \
    add_to_outbox, check_db_if_answer_arrived, delete_quest_from_db, change_status
from time import perf_counter, sleep
from publisher_quest import publish_message
from subscriber_quest import subscriber
from multiprocessing import Process

app = FastAPI(title="Questions Microservice")


@app.delete("/api/questions/{q_id}", status_code=204)
async def delete_question(q_id: str):
    if not check_question(q_id):
        raise HTTPException(status_code=404, detail="Question ID doesn't exist")

    transaction_id = add_to_outbox()

    message = {
        "transaction_id": transaction_id,
        "sender_id": 1,
        "receiver_id": 2,
        "message_type": "delete_answers",
        "resource_id": q_id
    }

    publish_message(message)

    t = 0
    while not (result := check_db_if_answer_arrived(transaction_id)):
        sleep(0.1)

        t += 0.1

        if t > 3:
            result = "timeout"
            change_status(transaction_id, result)
            break

    if result == "approved":
        delete_quest_from_db(q_id)
    else:
        raise HTTPException(status_code=404, detail="Something wrong with deleting answers")


@app.post("/api/questions/")
async def post_question(question: dict) -> dict:

    q_id = add_question_db(question["text"])

    return {"q_id": q_id}

if __name__ == '__main__':
    process = Process(target=subscriber)
    process.start()
    uvicorn.run("api_quest:app", host="192.168.111.29", port=8081, reload=True)
    connection.close()