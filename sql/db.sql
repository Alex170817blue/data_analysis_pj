#create DATABASE onthemovie;
use onthemovie;

create table users(
    UsersID int primary key,
    Gender varchar(10),
    Age int,
    CAP varchar(10),
    Work varchar(50)
);

show TABLES;

use onthemovie;

-- query di controllo per verificare che le tabelle siano state create correttamente
SELECT COUNT(*) AS totale FROM movies;
SELECT COUNT(*) AS totale FROM genres;
SELECT COUNT(*) AS totale FROM movie_genres;

select * from genres;
select * from movies;
select * from movie_genres;

USE onthemovie;

DELETE FROM movie_genres;
DELETE FROM movies;
DELETE FROM genres;