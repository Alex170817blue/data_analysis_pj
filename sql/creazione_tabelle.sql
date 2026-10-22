
use onthemovie;
CREATE TABLE IF NOT EXISTS movies (
    MovieID INT NOT NULL,
    Title VARCHAR(255) NOT NULL,
    YEAR SMALLINT NULL,
    PRIMARY KEY (MovieID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS genres (
    GenreID INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    PRIMARY KEY (GenreID),
    UNIQUE KEY uq_genres_name (Name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS movie_genres (
    MovieID INT NOT NULL,
    GenreID INT NOT NULL,

    PRIMARY KEY (MovieID, GenreID),

    CONSTRAINT fk_movie_genres_movie
        FOREIGN KEY (MovieID)
        REFERENCES movies(MovieID),

    CONSTRAINT fk_movie_genres_genre
        FOREIGN KEY (GenreID)
        REFERENCES genres(GenreID)
) ENGINE=InnoDB;

select * from movies;
select * from genres;
select * from movie_genres;


CREATE TABLE IF NOT EXISTS users (
    UserID INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Age INT NOT NULL,
    CAP VARCHAR(10) NOT NULL,
    Work VARCHAR(100) NOT NULL,
    PRIMARY KEY (UserID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ratings (
    UserID INT NOT NULL,
    MovieID INT NOT NULL,
    Rating TINYINT NOT NULL,
    Timestamp DATETIME NOT NULL,
    PRIMARY KEY (UserID, MovieID),
    CONSTRAINT fk_ratings_user
        FOREIGN KEY (UserID) REFERENCES users(UserID),
    CONSTRAINT fk_ratings_movie
        FOREIGN KEY (MovieID) REFERENCES movies(MovieID),
    CONSTRAINT chk_ratings_value
        CHECK (Rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

SELECT COUNT(*) AS numero_utenti FROM users;
SELECT COUNT(*) AS numero_valutazioni FROM ratings;

select * from genres