CREATE TABLE IF NOT EXISTS MESSAGES (MESSAGE TEXT NOT NULL, MESSAGEID INTEGER  PRIMARY KEY AUTOINCREMENT);

INSERT INTO MESSAGES
    (MESSAGE) 
VALUES
("Impossible is nothing."),
("Drive your dreams."), 
("Donft be evil."),
("Think different."),
("Nobody is perfect."),
("Happiness requires struggle."),
("Mistakes make people."),
("Time heals everything."),
("Failure teaches success."),
("Never say never."),
(" IN THE BOOK OF LIFE THE ANSWERS ARE NOT IN THE BACK!"),
("WE ALL HAVE OUR HANG-UPS!"),
("They canft order me to stop dreaming."),
("Sometimes losing may become a great fortune later."),
("One does not care to acknowledge the mistakes of onefs youth."),
("He stole something quite preciousc your heart."),
("Youfll stumble many times in the future, but when you do, each time youfll have more strength to bounce back."),
("If you donft like where you are, change it. Youfre not a tree."),
("All your dreams can come true if you have the courage to pursue them. "),
("When you give up, thatfs when the game is over.");


-- replies table
CREATE TABLE IF NOT EXISTS REPLIES (TARGET_WORD TEXT NOT NULL, REPLY_WORD TEXT NOT NULL,REPLYID INTEGER  PRIMARY KEY AUTOINCREMENT);
INSERT INTO REPLIES(TARGET_WORD, REPLY_WORD) VALUES("hello", "Oh! hello!"),("wheather", "sunny"), ("tired","good luck!");

CREATE TABLE IF NOT EXISTS USERS (DIALY_MODE_FLAG INTEGER NOT NULL, USERID TEXT PRIMARY KEY);
