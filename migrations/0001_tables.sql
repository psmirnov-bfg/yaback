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

CREATE TABLE relatives (
    id SERIAL PRIMARY KEY,
    citizen_from integer,
    citizen_to integer,
    import_id integer
);

-- +goose Down

DROP TABLE imports;
DROP TABLE citizens;
DROP TABLE relatives;