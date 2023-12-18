from fastapi import FastAPI, HTTPException
import uvicorn
from db_calls_ans import connection, add_new_answer_db, add_to_outbox, \
    check_db_if_answer_arrived, get_q_id_by_ans_id, delete_ans_from_db, change_status
from time import perf_counter, sleep
from publisher_ans import publish_message
from subscriber_ans import subscriber
from multiprocessing import Process

app = FastAPI(title="Answers Microservice")


@app.delete("/api/answers/{ans_id}", status_code=204)
async def delete_answer(ans_id: int):
    if not (q_id := get_q_id_by_ans_id(ans_id)):
        raise HTTPException(status_code=404, detail="Answer ID doesn't exist")

    transaction_id = add_to_outbox()

    message = {
        "transaction_id": transaction_id,
        "sender_id": 2,
        "receiver_id": 1,
        "message_type": "check_question",
        "resource_id": q_id
    }

    publish_message(message)

    t = 0
    while not (result := check_db_if_answer_arrived(transaction_id)):
        sleep(0.1)

        t += 0.1

        if t > 1:
            result = "timeout"
            change_status(transaction_id, result)
            break

    if result == "approved":
        delete_ans_from_db(ans_id)
    else:
        raise HTTPException(status_code=404, detail="Question for this answer ID doesn't exist")




@app.post("/api/answers/")
async def post_answer(answer: dict) -> dict:

    transaction_id = add_to_outbox()


    message = {
        "transaction_id": transaction_id,
        "sender_id": 2,
        "receiver_id": 1,
        "message_type": "check_question",
        "resource_id": answer['q_id']
    }

    publish_message(message)

    t = 0
    while not (result := check_db_if_answer_arrived(transaction_id)):
        sleep(0.1)

        t += 0.1

        if t > 1:
            result = "rejected"
            #delete_pending_transaction()
            break

    if result == "approved":
        new_ans_id = add_new_answer_db(answer)
        return {"id": new_ans_id}
    else:
        raise HTTPException(status_code=404, detail="Question doesn't exist")

if __name__ == '__main__':
    process = Process(target=subscriber)
    process.start()
    uvicorn.run("api_ans:app", host="192.168.111.29", port=8082, reload=True)
    connection.close()