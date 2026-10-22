
-- aggiunge l'anno
UPDATE movies 
SET Title = 'Casino (1995)' 
WHERE MovieID = 16;

-- Sostituisce 'Dramatic' con 'Drama'
UPDATE movies 
SET Genres = REPLACE(Genres, 'Dramatic', 'Drama') 
WHERE Genres LIKE '%Dramatic%'
AND MovieID > 0;

-- Sostituisce 'Dramma' con 'Drama'
UPDATE movies 
SET Genre = REPLACE(Genre, 'Dramma', 'Drama') 
WHERE Genre LIKE '%Dramma%'
AND MovieID > 0;

-- Corregge il doppio trattino in 'Comedy--Horror'
UPDATE movies 
SET Genres = REPLACE(Genres, 'Comedy--Horror', 'Comedy|Horror') 
WHERE Genres LIKE '%Comedy--Horror%'
AND MovieID > 0;


UPDATE movies
SET title = 'Phantom of theOpera, the'
WHERE MovieID = 3936;

DELETE FROM Movies
WHERE MovieID IN (
    SELECT MovieID
    FROM ratings
    GROUP BY MovieID
    HAVING AVG(Rating) < 3
       AND COUNT(DISTINCT UserID) >= 250
);

use onthemovie;
select * from movies;