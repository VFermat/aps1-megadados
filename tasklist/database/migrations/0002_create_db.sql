DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    uuid BINARY(16) PRIMARY KEY,
    description NVARCHAR(1024),
    completed BOOLEAN,
    FOREIGN KEY (user) REFERENCES users(username)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username NVARCHAR(40) PRIMARY KEY,
    first_name NVARCHAR(20),
    last_name NVARCHAR(20)
)