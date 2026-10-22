use OnTheMovie;

CREATE OR REPLACE VIEW vw_users_age_group AS
SELECT UserID, Gender, Age, CAP, Work,
       CASE
           WHEN Age <= 10 THEN 'under 10'
           WHEN Age BETWEEN 11 AND 15 THEN '11-15'
           WHEN Age BETWEEN 16 AND 20 THEN '16-20'
           WHEN Age BETWEEN 21 AND 25 THEN '21-25'
           WHEN Age BETWEEN 26 AND 30 THEN '26-30'
           WHEN Age BETWEEN 31 AND 35 THEN '31-35'
           WHEN Age BETWEEN 36 AND 40 THEN '36-40'
           WHEN Age BETWEEN 41 AND 45 THEN '41-45'
           WHEN Age BETWEEN 46 AND 50 THEN '46-50'
           WHEN Age BETWEEN 51 AND 55 THEN '51-55'
           ELSE 'over 56'
       END AS AgeGroup
FROM users;

select AgeGroup, COUNT(*) AS TotalUsers
from vw_users_age_group
group by AgeGroup;

CREATE OR REPLACE VIEW vw_ratings_by_age_group AS
SELECT
    r.UserID,
    r.MovieID,
    r.Rating,
    r.Timestamp,
    CASE
        WHEN u.Age <= 10 THEN 'under 10'
        WHEN u.Age BETWEEN 11 AND 15 THEN '11-15'
        WHEN u.Age BETWEEN 16 AND 20 THEN '16-20'
        WHEN u.Age BETWEEN 21 AND 25 THEN '21-25'
        WHEN u.Age BETWEEN 26 AND 30 THEN '26-30'
        WHEN u.Age BETWEEN 31 AND 35 THEN '31-35'
        WHEN u.Age BETWEEN 36 AND 40 THEN '36-40'
        WHEN u.Age BETWEEN 41 AND 45 THEN '41-45'
        WHEN u.Age BETWEEN 46 AND 50 THEN '46-50'
        WHEN u.Age BETWEEN 51 AND 55 THEN '51-55'
        WHEN u.Age >= 56 THEN 'over 56'
        ELSE 'Non definita'
    END AS AgeGroup
FROM ratings r
JOIN users u ON r.UserID = u.UserID;

-- numero film per ogni anno
CREATE OR REPLACE VIEW vw_films_by_year AS
SELECT
    `YEAR` AS FilmYear,
    COUNT(*) AS FilmCount
FROM vw_movies_after_1980
WHERE `YEAR` IS NOT NULL
GROUP BY `YEAR`;

SELECT *
FROM vw_films_by_year
ORDER BY FilmYear;

-- numero di film per ogni genere
CREATE OR REPLACE VIEW vw_films_by_genre AS
SELECT
    g.GenreID,
    g.Name AS Genre,
    COUNT(DISTINCT mg.MovieID) AS FilmCount
FROM genres g
LEFT JOIN movie_genres mg
    ON g.GenreID = mg.ID
GROUP BY g.GenreID, g.Name;

SELECT *
FROM vw_films_by_genre
ORDER BY FilmCount DESC;

-- film con media inferiore a 3 e almeno 250 voti
CREATE OR REPLACE VIEW vw_movies_to_remove AS
SELECT
    m.MovieID,
    m.Title,
    m.`YEAR` AS FilmYear,
    COUNT(DISTINCT r.UserID) AS ReviewerCount,
    ROUND(AVG(r.Rating), 2) AS AverageRating
FROM vw_movies_after_1980 m
JOIN ratings r
    ON m.MovieID = r.MovieID
GROUP BY
    m.MovieID,
    m.Title,
    m.`YEAR`
HAVING AVG(r.Rating) < 3
   AND COUNT(DISTINCT r.UserID) >= 250;

SELECT *
FROM vw_movies_to_remove
ORDER BY AverageRating ASC, ReviewerCount DESC;

-- top 10 film per ogni gruppo di età e genere
CREATE OR REPLACE VIEW vw_movie_ratings_by_age_gender AS
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
JOIN vw_movies_after_1980 m
    ON r.MovieID = m.MovieID
GROUP BY
    u.AgeGroup,
    u.Gender,
    m.MovieID,
    m.Title;

-- distribuzione iscritti per provincia
CREATE OR REPLACE VIEW vw_users_by_cap AS
SELECT
    COALESCE(NULLIF(TRIM(CAP), ''), 'Non specificato') AS CAP,
    COUNT(*) AS SubscriberCount
FROM users
GROUP BY
    COALESCE(NULLIF(TRIM(CAP), ''), 'Non specificato');

SELECT *
FROM vw_users_by_cap
ORDER BY SubscriberCount DESC
LIMIT 20;

-- view per la distribuzione degli utenti per lavoro
CREATE OR REPLACE VIEW vw_users_by_work AS
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

SELECT *
FROM vw_users_by_work
ORDER BY SubscriberCount DESC;

-- top 10 film per ogni gruppo di età e genere
CREATE OR REPLACE VIEW vw_top10_movies_by_age_gender AS
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

SELECT *
FROM vw_top10_movies_by_age_gender
ORDER BY AgeGroup, Gender, Position;

-- dal meno preferito al più preferito per ogni gruppo di età
CREATE OR REPLACE VIEW vw_movie_ratings_by_age_group AS
SELECT
    u.AgeGroup,
    m.MovieID,
    m.Title,
    COUNT(r.Rating) AS RatingCount,
    ROUND(AVG(r.Rating), 2) AS AverageRating
FROM ratings r
JOIN vw_users_age_group u
    ON r.UserID = u.UserID
JOIN vw_movies_after_1980 m
    ON r.MovieID = m.MovieID
GROUP BY
    u.AgeGroup,
    m.MovieID,
    m.Title;
 
SELECT *
FROM vw_movie_ratings_by_age_group
ORDER BY
    AgeGroup,
    AverageRating ASC,
    RatingCount DESC;

-- filtra i film tutti dopo il 1980
CREATE OR REPLACE VIEW vw_movies_after_1980 AS
SELECT *
FROM movies
WHERE `YEAR` > 1980;
