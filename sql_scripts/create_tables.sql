BEGIN TRANSACTION;
CREATE TABLE log(logdatetime TEXT, action INTEGER, comment VARCHAR(255), usernameid INTEGER REFERENCES users(id));
CREATE TABLE users(id INTEGER primary key, username VARCHAR(255), key VARCHAR(255), addedby INTEGER REFERENCES id, roles INTEGER, created TEXT);
COMMIT;
