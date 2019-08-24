-- +goose Up

CREATE TABLE imports (
    id SERIAL PRIMARY KEY,
    timestamp integer
);

CREATE TABLE citizens (
    id SERIAL PRIMARY KEY,
    import_id integer,
    citizen_id integer,
    town text,
    street text,
    building text,
    apartment integer,
    name text,
    birth_date bigint,
    gender boolean
);

CREATE INDEX citizens_import_id_citizen_id_idx ON citizens(import_id int4_ops,citizen_id int4_ops);
CREATE INDEX citizens_import_id_idx ON citizens(import_id int4_ops);


CREATE TABLE relatives (
    id SERIAL PRIMARY KEY,
    citizen_from integer,
    citizen_to integer,
    import_id integer
);

CREATE INDEX relatives_import_id_citizen_to_idx ON relatives(import_id int4_ops,citizen_to int4_ops);
CREATE INDEX relatives_import_id_citizen_from_idx ON relatives(import_id int4_ops,citizen_from int4_ops);
CREATE INDEX relatives_import_id_idx ON relatives(import_id int4_ops);


-- +goose Down

DROP TABLE imports;
DROP TABLE citizens;
DROP TABLE relatives;