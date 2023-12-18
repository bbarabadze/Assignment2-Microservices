import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation

connection = psycopg2.connect(
    user="postgres",
    password="admin",
    host="127.0.0.1",
    port="5432",
    database="r_a_db",

)
connection.autocommit = True


def delete_ans_by_q_id(q_id: str) -> None:
    query_delete_ans_by_q = """
    DELETE FROM answers
    WHERE q_id = %s
    """
    cursor = connection.cursor()
    cursor.execute(query_delete_ans_by_q, (q_id, ))

    cursor.close()



def delete_ans_from_db(ans_id) -> None:
    query_delete_ans = """
    DELETE FROM answers
    WHERE id = %s
    """
    cursor = connection.cursor()
    cursor.execute(query_delete_ans, (ans_id, ))

    cursor.close()


def get_q_id_by_ans_id(ans_id: int) -> int|None:

    query_get_q_id = """
    SELECT q_id FROM answers
    WHERE id = %s
    """

    cursor = connection.cursor()
    cursor.execute(query_get_q_id, (ans_id, ))

    result = cursor.fetchone()
    cursor.close()

    return result[0] if result else None


def check_db_if_answer_arrived(transaction_id: int) -> str:
    query_check_trans = """
    SELECT status FROM outbox
    WHERE id = %s
    """

    cursor = connection.cursor()
    cursor.execute(query_check_trans, (transaction_id,))

    trans_status = cursor.fetchone()[0]

    cursor.close()

    return None if trans_status == 'pending' else trans_status


def change_status(trans_id: int, status: str) -> None:

    query_change_status = """
    UPDATE outbox
    SET status = %s
    WHERE id = %s
    """
    cursor = connection.cursor()
    cursor.execute(query_change_status,
                   (status, trans_id))


    cursor.close()


def add_to_outbox() -> int:

    query_add_outbox = """
    INSERT INTO outbox DEFAULT VALUES
    RETURNING id;
    """

    cursor = connection.cursor()
    cursor.execute(query_add_outbox)

    trans_id = int(cursor.fetchone()[0])

    cursor.close()
    return trans_id

def add_new_answer_db(answer: dict) -> int:

    query_add_new_answer = """
    INSERT INTO answers
    (q_id, text, votes)
    VALUES (%s, %s, 0)
    RETURNING id;
    """

    cursor = connection.cursor()
    cursor.execute(query_add_new_answer,
                   (answer["q_id"], answer["text"]))

    answer_id = int(cursor.fetchone()[0])

    cursor.close()
    return answer_id


if __name__ == '__main__':
    print(check_db_if_answer_arrived(int(input())))