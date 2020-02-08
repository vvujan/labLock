BEGIN TRANSACTION;
INSERT INTO `users` (id,username,key,addedby,roles,created) VALUES (1,'Test user','AA:4A:AA:AA',NULL,1,'2018-08-18');
COMMIT;
