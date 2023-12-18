import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation

connection = psycopg2.connect(
    user="postgres",
    password="admin",
    host="127.0.0.1",
    port="5432",
    database="r_q_db",

)
connection.autocommit = True


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



def delete_quest_from_db(q_id: str) -> None:
    query_delete_quest = """
    DELETE FROM questions
    WHERE id = %s
    """
    cursor = connection.cursor()
    cursor.execute(query_delete_quest, (q_id, ))

    cursor.close()

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



def add_question_db(text: str) -> str:
    query_add_quest = """
    INSERT INTO questions
    (text)
    VALUES (%s)
    RETURNING id;
    """
    cursor = connection.cursor()
    cursor.execute(query_add_quest,
                   (text, ))

    q_id = cursor.fetchone()[0]

    cursor.close()
    return q_id


def check_question(q_id: str) -> bool:

    query_check_question = """
    SELECT id FROM questions
    WHERE id = %s
    """

    cursor = connection.cursor()
    cursor.execute(query_check_question, (q_id,))

    q_id = cursor.fetchone()

    cursor.close()
    return bool(q_id)


if __name__ == '__main__':
    print(check_question('j2opeh'))