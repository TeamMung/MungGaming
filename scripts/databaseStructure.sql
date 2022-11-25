CREATE TABLE IF NOT EXISTS userRoles (
    roleID          INTEGER NOT NULL,
    role            VARCHAR(16) NOT NULL,
    PRIMARY KEY (roleID AUTOINCREMENT)
);

INSERT OR IGNORE INTO userRoles (roleID, role) VALUES
    (1, "admin"),
    (2, "user"),
    (3, "banned");

CREATE TABLE IF NOT EXISTS users (
    userID          INTEGER NOT NULL,
    roleID          INTEGER NOT NULL,
    username        VARCHAR(16) UNIQUE NOT NULL,
    passwordHash    VARCHAR(60) NOT NULL,
    email           VARCHAR(256) UNIQUE NOT NULL,
    dateOfBirth     DATE NOT NULL,
    phoneNumber     VARCHAR(20) NOT NULL,
    PRIMARY KEY (userID AUTOINCREMENT),
    FOREIGN KEY (roleID) REFERENCES userRoles(roleID)
);

CREATE TABLE IF NOT EXISTS games (
    gameID          INTEGER NOT NULL,
    gameName        VARCHAR(64) NOT NULL,
    gameDescription VARCHAR(256) NOT NULL,
    releaseDate     DATE NOT NULL,
    approved        BOOLEAN NOT NULL,
    PRIMARY KEY (gameID)
);

CREATE TABLE IF NOT EXISTS gameImages (
    imageID         INTEGER NOT NULL,
    gameID          INTEGER NOT NULL,
    imageHash       VARCHAR(32) NOT NULL,
    imageType       VARCHAR(4) NOT NULL,
    PRIMARY KEY (imageID AUTOINCREMENT),
    FOREIGN KEY (gameID) REFERENCES games(gameID)
);

CREATE TABLE IF NOT EXISTS gameReviews (
    reviewID        INTEGER NOT NULL,
    userID          INTEGER NOT NULL,
    gameID          INTEGER NOT NULL,
    datePosted      DATE NOT NULL,
    rating          INTEGER(1) NOT NULL,
    reviewText      VARCHAR(1024) NOT NULL,
    PRIMARY KEY (reviewID AUTOINCREMENT),
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (gameID) REFERENCES games(gameID)
);

CREATE TABLE IF NOT EXISTS gameLists (
    listID          INTEGER NOT NULL,
    userID          INTEGER NOT NULL,
    listName        VARCHAR(64) NOT NULL,
    public          BOOLEAN NOT NULL,
    PRIMARY KEY (listID AUTOINCREMENT),
    FOREIGN KEY (userID) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS gameListLink (
    listID          INTEGER NOT NULL,
    gameID          INTEGER NOT NULL,
    FOREIGN KEY (listID) REFERENCES gameLists(listID),
    FOREIGN KEY (gameID) REFERENCES games(gameID)
);

CREATE TABLE IF NOT EXISTS gameGenres (
    genreID         INTEGER NOT NULL,
    genre           VARCHAR(32) NOT NULL,
    PRIMARY KEY (genreID AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS gameGenresLink (
    gameID          INTEGER NOT NULL,
    genreID         INTEGER NOT NULL,
    FOREIGN KEY (gameID) REFERENCES games(gameID),
    FOREIGN KEY (genreID) REFERENCES gameGenres(genreID)
);

CREATE TABLE IF NOT EXISTS gamePublishers (
    publisherID     INTEGER NOT NULL,
    publisherName   VARCHAR(64) NOT NULL,
    PRIMARY KEY (publisherID AUTOINCREMENT)
);  

CREATE TABLE IF NOT EXISTS gamePublishersLink (
    gameID          INTEGER NOT NULL,
    publisherID     INTEGER NOT NULL,
    FOREIGN KEY (gameID) REFERENCES games(gameID),
    FOREIGN KEY (publisherID) REFERENCES gamePublishers(publisherID)
);