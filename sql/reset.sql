USE onthemovie;

-- 1. Disattiva temporaneamente i controlli delle chiavi estere
SET foreign_key_checks = 0;

-- 2. Elimina tutte le viste esistenti (partendo da quelle che dipendono da altre)
DROP VIEW IF EXISTS vw_top10_movies_by_age_gender;
DROP VIEW IF EXISTS vw_users_by_work;
DROP VIEW IF EXISTS vw_users_by_cap;
DROP VIEW IF EXISTS vw_movie_ratings_by_age_group;
DROP VIEW IF EXISTS vw_movie_ratings_by_age_gender;
DROP VIEW IF EXISTS vw_movies_to_remove;
DROP VIEW IF EXISTS vw_films_by_genre;
DROP VIEW IF EXISTS vw_films_by_year;
DROP VIEW IF EXISTS vw_ratings_by_age_group;
DROP VIEW IF EXISTS vw_users_age_group;

-- 3. Elimina tutte le tabelle esistenti
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS movies;

-- Riattiva i controlli delle chiavi estere
SET foreign_key_checks = 1;


-- ==========================================
-- 4. RICREAZIONE DELLE TABELLE
-- ==========================================

CREATE TABLE movies (
    MovieID INT NOT NULL,
    Title VARCHAR(255) NOT NULL,
    YEAR SMALLINT NULL,
    PRIMARY KEY (MovieID)
) ENGINE=InnoDB;

CREATE TABLE genres (
    GenreID INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    PRIMARY KEY (GenreID),
    UNIQUE KEY uq_genres_name (Name)
) ENGINE=InnoDB;

CREATE TABLE movie_genres (
    MovieID INT NOT NULL,
    GenreID INT NOT NULL,
    PRIMARY KEY (MovieID, GenreID),
    CONSTRAINT fk_movie_genres_movie
        FOREIGN KEY (MovieID) REFERENCES movies(MovieID),
    CONSTRAINT fk_movie_genres_genre
        FOREIGN KEY (GenreID) REFERENCES genres(GenreID)
) ENGINE=InnoDB;

CREATE TABLE users (
    UserID INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Age INT NOT NULL,
    CAP VARCHAR(10) NOT NULL,
    Work VARCHAR(100) NOT NULL,
    PRIMARY KEY (UserID)
) ENGINE=InnoDB;

CREATE TABLE ratings (
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


-- ==========================================
-- 5. RICREAZIONE DELLE VISTE
-- ==========================================

CREATE VIEW vw_users_age_group AS
SELECT UserID, Gender, Age, CAP, Work,
       CASE
           WHEN Age < 18 THEN 'Under 18'
           WHEN Age BETWEEN 18 AND 24 THEN '18-24'
           WHEN Age BETWEEN 25 AND 34 THEN '25-34'
           WHEN Age BETWEEN 35 AND 44 THEN '35-44'
           WHEN Age BETWEEN 45 AND 54 THEN '45-54'
           ELSE 'over 55'
       END AS AgeGroup
FROM users;

CREATE VIEW vw_ratings_by_age_group AS
SELECT
    r.UserID,
    r.MovieID,
    r.Rating,
    r.Timestamp,
    CASE
        WHEN u.Age < 18 THEN '< 18'
        WHEN u.Age BETWEEN 18 AND 24 THEN '18-24'
        WHEN u.Age BETWEEN 25 AND 34 THEN '25-34'
        WHEN u.Age BETWEEN 35 AND 44 THEN '35-44'
        WHEN u.Age BETWEEN 45 AND 54 THEN '45-54'
        WHEN u.Age >= 55 THEN 'over 55'
        ELSE 'Non definita'
    END AS AgeGroup
FROM ratings r
JOIN users u ON r.UserID = u.UserID;

CREATE VIEW vw_films_by_year AS
SELECT
    `YEAR` AS FilmYear,
    COUNT(*) AS FilmCount
FROM movies
WHERE `YEAR` IS NOT NULL
GROUP BY `YEAR`;

CREATE VIEW vw_films_by_genre AS
SELECT
    g.GenreID,
    g.Name AS Genre,
    COUNT(DISTINCT mg.MovieID) AS FilmCount
FROM genres g
LEFT JOIN movie_genres mg
    ON g.GenreID = mg.GenreID
GROUP BY g.GenreID, g.Name;

CREATE VIEW vw_movies_to_remove AS
SELECT
    m.MovieID,
    m.Title,
    m.`YEAR` AS FilmYear,
    COUNT(DISTINCT r.UserID) AS ReviewerCount,
    ROUND(AVG(r.Rating), 2) AS AverageRating
FROM movies m
JOIN ratings r
    ON m.MovieID = r.MovieID
GROUP BY
    m.MovieID,
    m.Title,
    m.`YEAR`
HAVING AVG(r.Rating) < 3
   AND COUNT(DISTINCT r.UserID) >= 250;

CREATE VIEW vw_movie_ratings_by_age_gender AS
SELECT
    u.AgeGroup,
    u.Gender,
    m.MovieID,
    m.Title,
    COUNT(r.Rating) AS RatingCount,
    ROUND(AVG(r.Rating), 2) AS AverageRating
FROM ratings r
JOIN vw_users_age_group u
    ON r.UserID = u.UserID
JOIN movies m
    ON r.MovieID = m.MovieID
GROUP BY
    u.AgeGroup,
    u.Gender,
    m.MovieID,
    m.Title;

CREATE VIEW vw_movie_ratings_by_age_group AS
SELECT
    u.AgeGroup,
    m.MovieID,
    m.Title,
    COUNT(r.Rating) AS RatingCount,
    ROUND(AVG(r.Rating), 2) AS AverageRating
FROM ratings r
JOIN vw_users_age_group u
    ON r.UserID = u.UserID
JOIN movies m
    ON r.MovieID = m.MovieID
GROUP BY
    u.AgeGroup,
    m.MovieID,
    m.Title;

CREATE VIEW vw_users_by_cap AS
SELECT
    COALESCE(NULLIF(TRIM(CAP), ''), 'Non specificato') AS CAP,
    COUNT(*) AS SubscriberCount
FROM users
GROUP BY
    COALESCE(NULLIF(TRIM(CAP), ''), 'Non specificato');

CREATE VIEW vw_users_by_work AS
SELECT
    COALESCE(
        NULLIF(TRIM(Work), ''),
        'Non specificato'
    ) AS WorkCategory,
    COUNT(*) AS SubscriberCount,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users),
        2
    ) AS SubscriberPercentage
FROM users
GROUP BY
    COALESCE(
        NULLIF(TRIM(Work), ''),
        'Non specificato'
    );

CREATE VIEW vw_top10_movies_by_age_gender AS
SELECT
    ranked.AgeGroup,
    ranked.Gender,
    ranked.MovieID,
    ranked.Title,
    ranked.RatingCount,
    ranked.AverageRating,
    ranked.Position
FROM (
    SELECT
        v.AgeGroup,
        v.Gender,
        v.MovieID,
        v.Title,
        v.RatingCount,
        v.AverageRating,
        ROW_NUMBER() OVER (
            PARTITION BY v.AgeGroup, v.Gender
            ORDER BY
                v.AverageRating DESC,
                v.RatingCount DESC,
                v.Title ASC
        ) AS Position
    FROM vw_movie_ratings_by_age_gender v
    WHERE v.RatingCount > 0
) ranked
WHERE ranked.Position <= 10;