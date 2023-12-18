
-- Function to generate random ids for questions

CREATE OR REPLACE FUNCTION generate_random_string()
RETURNS CHAR(6) AS
$$
DECLARE
    chars TEXT := 'abcdefghijklmnopqrstuvwxyz0123456789';
    result CHAR(6) := '';
    i INTEGER;
BEGIN
    FOR i IN 1..6 LOOP
        result := result || SUBSTRING(chars, (random() * length(chars) + 1)::INTEGER, 1);
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;



CREATE TABLE questions (
    id CHAR(6) PRIMARY KEY UNIQUE NOT NULL DEFAULT generate_random_string(),
    text VARCHAR(1000) NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0,
    "timestamp" double precision,
    "datetime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Fill from pandas csv

UPDATE questions
SET datetime = TO_TIMESTAMP(timestamp);

ALTER TABLE questions
DROP COLUMN "timestamp";


CREATE TABLE outbox(
    id SERIAL PRIMARY KEY UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    "datetime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



