# ============================================================
# MAIN - Pipeline di elaborazione dei dati OnTheMovie
# ============================================================
#
# Questo file coordina tutte le fasi del progetto:
#
# 1. Lettura dei file CSV.
# 2. Pulizia e trasformazione dei dati.
# 3. Creazione delle tabelle in memoria.
# 4. Esportazione dei dati puliti in CSV.
# 5. Verifica dei DAO per film e generi.
# 6. Validazione di utenti e valutazioni.
# 7. Caricamento di users e ratings in MySQL.
#
# Le tabelle movies, genres e movie_genres sono già presenti
# in MySQL, quindi questo script non le reinserisce.
# ============================================================


# ------------------------------------------------------------
# IMPORTAZIONE DELLE LIBRERIE E DEI MODULI DEL PROGETTO
# ------------------------------------------------------------

import os
import pandas as pd

# Configurazione dei percorsi e delle caratteristiche dei CSV
from config.sources import SOURCES

# Classe responsabile della lettura dei file CSV
from readers.csv_reader import CSVReader

# Classe che gestisce le tabelle DataFrame in memoria
# e permette di esportarle verso MySQL
from database import Database

# Classe che gestisce la connessione al database MySQL
from sql_connection import SQLConnection

# Trasformazione del CSV originale dei film in tre tabelle:
# movies, genres e movie_genres
from transformations.relational_movie_transformer import (
    transform_movies_relational
)

# Trasformazione dei film nel formato completo utilizzato dai DAO
from transformations.film_transformers import transform_movies

# DAO: classi per accedere ai dati dei film e dei generi
from dao.dao_genre import DaoGenre
from dao.dao_movie import DaoMovie

# Trasformazioni dei dati degli utenti e delle valutazioni
from transformations.user_transformers import transform_users
from transformations.rating_transformers import transform_ratings


# ============================================================
# FUNZIONE: inspect_csv
# ============================================================

def inspect_csv(reader, name):
    """
    Legge un CSV e ne stampa alcune informazioni utili
    per verificare la qualità dei dati.

    La funzione non modifica il contenuto del file:
    restituisce semplicemente il DataFrame letto.
    """

    # Lettura del CSV attraverso il reader ricevuto
    df = reader.read()

    print(f"\n--- Analisi {name} ---")

    # Numero di righe e colonne del DataFrame
    print("Dimensioni:", df.shape)

    # Elenco dei nomi delle colonne
    print("Colonne:", df.columns.tolist())

    # Conteggio dei valori mancanti per ogni colonna
    print("\nValori mancanti per colonna:")
    print(df.isna().sum())

    # Conteggio delle righe identiche in tutte le colonne
    print("\nRighe completamente duplicate:", df.duplicated().sum())

    # Ricerca delle stringhe vuote o contenenti solo spazi
    # nelle colonne di tipo object
    for column in df.select_dtypes(include=["object"]).columns:
        empty = df[column].astype("string").str.strip().eq("").sum()
        print(f"Valori vuoti in {column}: {empty}")

    # Visualizzazione delle prime cinque righe
    print("\nPrime righe:")
    print(df.head())

    # Restituisce il DataFrame per le successive elaborazioni
    return df


# ============================================================
# FUNZIONE: validate_users_ratings
# ============================================================

def validate_users_ratings(users_df, ratings_df, movies_df):
    """
    Controlla la qualità dei dati di utenti e valutazioni.

    Verifica:
    - validità e unicità degli identificativi;
    - valori numerici;
    - intervallo dei rating;
    - duplicati nelle coppie UserID-MovieID;
    - esistenza degli utenti e dei film referenziati.

    I controlli vengono eseguiti su copie dei DataFrame,
    così da non modificare i dati originali.
    """

    # Copie utilizzate esclusivamente per la validazione
    users = users_df.copy()
    ratings = ratings_df.copy()
    movies = movies_df.copy()

    # Conversione temporanea degli identificativi degli utenti
    # in numeri. errors="coerce" converte i valori non validi
    # in NaN, rendendoli individuabili nei controlli.
    users["UserID"] = pd.to_numeric(
        users["UserID"],
        errors="coerce"
    )

    # Conversione dei campi numerici delle valutazioni
    for column in ["UserID", "MovieID", "Rating", "Timestamp"]:
        ratings[column] = pd.to_numeric(
            ratings[column],
            errors="coerce"
        )

    # Conversione degli identificativi dei film
    movies["MovieID"] = pd.to_numeric(
        movies["MovieID"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Controlli sulla tabella USERS
    # --------------------------------------------------------

    print("\n--- Verifica USERS ---")

    # Identificativi mancanti o non convertibili
    print("UserID non validi:", users["UserID"].isna().sum())

    # Ogni utente dovrebbe avere un UserID univoco
    print("UserID duplicati:", users["UserID"].duplicated().sum())

    # Valori distinti della colonna Gender
    print("Gender distinti:", sorted(users["Gender"].unique()))

    # Età distinte presenti nel dataset
    print(
        "Age distinti:",
        sorted(users["Age"].astype(str).unique())
    )

    # Numero di categorie lavorative differenti
    print("Numero di valori Work distinti:", users["Work"].nunique())

    # Il CAP deve essere conservato come testo,
    # per non perdere eventuali zeri iniziali.
    print("CAP da conservare come testo.")

    # --------------------------------------------------------
    # Controlli sulla tabella RATINGS
    # --------------------------------------------------------

    print("\n--- Verifica RATINGS ---")
    print("Valori numerici non validi:")

    # Conta i valori che non possono essere convertiti in numeri
    for column in ["UserID", "MovieID", "Rating", "Timestamp"]:
        print(
            f"  {column}:",
            ratings[column].isna().sum()
        )

    # La stessa persona non dovrebbe valutare due volte
    # lo stesso film, secondo la chiave primaria prevista.
    print(
        "Coppie UserID-MovieID duplicate:",
        ratings.duplicated(["UserID", "MovieID"]).sum()
    )

    # Visualizza i valori distinti dei rating
    print(
        "Valori Rating distinti:",
        sorted(ratings["Rating"].dropna().unique())
    )

    # I rating ammessi devono essere compresi tra 1 e 5
    print(
        "Rating fuori dall'intervallo 1-5:",
        (~ratings["Rating"].between(1, 5)).sum()
    )

    # Mostra i limiti dei timestamp Unix originali
    print("Timestamp minimo:", ratings["Timestamp"].min())
    print("Timestamp massimo:", ratings["Timestamp"].max())

    # --------------------------------------------------------
    # Controllo delle relazioni tra le tabelle
    # --------------------------------------------------------

    # Insieme degli identificativi validi di utenti e film
    user_ids = set(users["UserID"].dropna())
    movie_ids = set(movies["MovieID"].dropna())

    # Individua le valutazioni che fanno riferimento
    # a utenti inesistenti
    missing_users = ~ratings["UserID"].isin(user_ids)

    # Individua le valutazioni che fanno riferimento
    # a film inesistenti
    missing_movies = ~ratings["MovieID"].isin(movie_ids)

    print("\n--- Verifica RELAZIONI ---")
    print("Ratings con UserID inesistente:", missing_users.sum())
    print("Ratings con MovieID inesistente:", missing_movies.sum())


# ============================================================
# FUNZIONE PRINCIPALE
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. CONFIGURAZIONE E LETTURA DEL CSV DEI FILM
    # --------------------------------------------------------

    # Recupera dal dizionario SOURCES la configurazione
    # relativa al file originale dei film.
    config = SOURCES["movies"]

    # Crea un reader usando le impostazioni configurate:
    # percorso, presenza dell'intestazione, separatore e encoding.
    reader = CSVReader(
        path=config["path"],
        has_header=config["has_header"],
        delimiter=config["delimiter"],
        encoding=config["encoding"],
    )

    # Crea i reader per utenti e valutazioni.
    # In questo modo si utilizzano anche le rispettive
    # impostazioni definite in config/sources.py.
    users_config = SOURCES["users"]
    ratings_config = SOURCES["ratings"]

    users_reader = CSVReader(
        path=users_config["path"],
        has_header=users_config["has_header"],
        delimiter=users_config["delimiter"],
        encoding=users_config["encoding"],
    )

    ratings_reader = CSVReader(
        path=ratings_config["path"],
        has_header=ratings_config["has_header"],
        delimiter=ratings_config["delimiter"],
        encoding=ratings_config["encoding"],
    )

    # --------------------------------------------------------
    # 2. CREAZIONE DEL DATABASE IN MEMORIA
    # --------------------------------------------------------

    # Database è una classe del progetto che conserva
    # le tabelle Pandas in un dizionario.
    # Non è ancora una connessione a MySQL.
    db = Database()

    # Legge il CSV dei film, verifica le colonne obbligatorie
    # e applica la trasformazione relazionale.
    #
    # Il transformer restituisce un dizionario contenente:
    # - movies;
    # - genres;
    # - movie_genres.
    db.add_source(
        table_name="movies_clean",
        reader=reader,
        required_columns=["MovieID", "Title", "Genres"],
        transformer=transform_movies_relational,
    )

    # Legge e trasforma i dati degli utenti.
    # La tabella risultante viene registrata in memoria
    # con il nome "users".
    db.add_source(
        table_name="users",
        reader=users_reader,
        required_columns=[
            "UserID", "Gender", "Age", "CAP", "Work"
        ],
        transformer=transform_users,
    )

    # Legge e trasforma le valutazioni.
    # Il transformer converte anche il timestamp Unix
    # nel formato datetime compatibile con MySQL.
    db.add_source(
        table_name="ratings",
        reader=ratings_reader,
        required_columns=[
            "UserID", "MovieID", "Rating", "Timestamp"
        ],
        transformer=transform_ratings,
    )

    # Visualizza le tabelle attualmente registrate
    # e il numero di record pronti per le successive operazioni.
    print("\nTabelle disponibili:", db.list_tables())
    print("Utenti pronti per SQL:", len(db.get_table("users")))
    print("Valutazioni pronte per SQL:", len(db.get_table("ratings")))

    # --------------------------------------------------------
    # 3. RECUPERO DELLE TABELLE RELAZIONALI DEI FILM
    # --------------------------------------------------------

    # get_table restituisce una copia del DataFrame richiesto.
    movies = db.get_table("movies")
    genres = db.get_table("genres")
    movie_genres = db.get_table("movie_genres")

    # Stampa i conteggi e i nomi delle colonne
    # per verificare che la trasformazione sia corretta.
    print("\n--- Tabelle relazionali dei film ---")
    print("Numero di film:", len(movies))
    print("Numero di generi:", len(genres))
    print("Numero di associazioni:", len(movie_genres))

    print("Colonne movies:", movies.columns.tolist())
    print("Colonne genres:", genres.columns.tolist())
    print("Colonne movie_genres:", movie_genres.columns.tolist())

    # --------------------------------------------------------
    # 4. ESPORTAZIONE DEI CSV RELAZIONALI
    # --------------------------------------------------------

    # Crea la cartella data se non esiste già.
    os.makedirs("data", exist_ok=True)

    # Esporta la tabella dei film.
    movies.to_csv(
        "data/movies.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Esporta l'elenco dei generi.
    genres.to_csv(
        "data/genres.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Esporta le associazioni tra film e generi.
    movie_genres.to_csv(
        "data/movie_genres.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nCSV relazionali esportati:")
    print("- data/movies.csv")
    print("- data/genres.csv")
    print("- data/movie_genres.csv")

    # --------------------------------------------------------
    # 5. ESPORTAZIONE DEL CSV COMPLETO PER I DAO
    # --------------------------------------------------------

    # Questa trasformazione produce il formato completo
    # utilizzato dai DAO, mantenendo la colonna Genres.
    flat_movies = transform_movies(reader.read())

    output_path = "data/movies_clean.csv"

    # Il CSV viene esportato una sola volta.
    # utf-8-sig aiuta la compatibilità con alcuni programmi
    # che aprono i CSV, ad esempio Excel.
    flat_movies.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"CSV pulito esportato in: {output_path}")

    # --------------------------------------------------------
    # 6. CREAZIONE E VERIFICA DEI DAO
    # --------------------------------------------------------

    # DaoGenre gestisce l'accesso agli oggetti Genre.
    dao_genre = DaoGenre()

    # DaoMovie legge il CSV completo e usa DaoGenre
    # per collegare i film ai rispettivi generi.
    dao_movie = DaoMovie(output_path, dao_genre)

    # Verifica il numero di oggetti caricati nei DAO.
    print("Film caricati nei DAO:", len(dao_movie.get_all_movies()))
    print("Generi caricati nei DAO:", len(dao_genre.get_all_genres()))

    # Cerca il film con identificativo 16.
    movie = dao_movie.get_movie_by_id(16)
    print("Film con ID 16:", movie)

    # Se il film esiste, mostra i suoi generi.
    if movie is not None:
        print("Generi del film:", movie.genres)

    # Cerca il genere Comedy e conta i film associati.
    genre = dao_genre.get_genre_by_name("Comedy")

    if genre is not None:
        print("Film di genere Comedy:", len(genre.movies))

    # --------------------------------------------------------
    # 7. ANALISI PRELIMINARE DI USERS E RATINGS
    # --------------------------------------------------------

    # Legge i CSV e stampa statistiche utili per
    # individuare valori mancanti, duplicati e anomalie.
    users_df = inspect_csv(users_reader, "users")
    ratings_df = inspect_csv(ratings_reader, "ratings")

    # Applica le trasformazioni ai DataFrame.
    # Le versioni trasformate vengono usate per l'esportazione
    # e per controllare i tipi di dato.
    users_clean = transform_users(users_df)
    ratings_clean = transform_ratings(ratings_df)

    print("\n--- Users trasformati ---")
    print(users_clean.dtypes)
    print(users_clean.head())

    print("\n--- Ratings trasformati ---")
    print(ratings_clean.dtypes)
    print(ratings_clean.head())

    # Esporta gli utenti nel formato pulito.
    users_clean.to_csv(
        "data/users.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Esporta le valutazioni nel formato pulito.
    ratings_clean.to_csv(
        "data/ratings.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("CSV utenti esportato in: data/users.csv")
    print("CSV valutazioni esportato in: data/ratings.csv")

    # --------------------------------------------------------
    # 8. VALIDAZIONE DELLE RELAZIONI
    # --------------------------------------------------------

    # Verifica che gli identificativi delle valutazioni
    # corrispondano a utenti e film esistenti.
    #
    # Si usano i dati originali letti dai CSV:
    # la funzione effettua le proprie conversioni temporanee.
    validate_users_ratings(
        users_df,
        ratings_df,
        movies,
    )

    # --------------------------------------------------------
    # 9. CARICAMENTO DATI IN MYSQL
    # --------------------------------------------------------

    # Crea l'oggetto che gestisce la connessione SQL.
    sql = SQLConnection()

    try:
        # Apre la connessione al database.
        sql.connect()

        #carico prima i film, generi e associazioni.
        movies_inserted = db.write_to_sql(table_name="movies", connection=sql, if_exists="append")
        print(f"Film inviati a MySQL: {movies_inserted}")
        genres_inserted = db.write_to_sql(table_name="genres", connection=sql, if_exists="append")
        print(f"Generi inviati a MySQL: {genres_inserted}")
        movie_genres_inserted = db.write_to_sql(table_name="movie_genres", connection=sql, if_exists="append")
        print(f"Associazioni Film-Genere inviate a MySQL: {movie_genres_inserted}")

        # Carica prima gli utenti.
        # È necessario perché ratings contiene una chiave
        # esterna che fa riferimento a users.UserID.
        #
        # append aggiunge i record alla tabella esistente:
        # non ricrea la tabella e non cancella i dati.
        users_inserted = db.write_to_sql(
            table_name="users",
            connection=sql,
            if_exists="append",
        )

        print(f"Utenti inviati a MySQL: {users_inserted}")

        # Carica poi le valutazioni.
        # I relativi utenti e film devono già esistere,
        # altrimenti i vincoli di chiave esterna possono fallire.
        ratings_inserted = db.write_to_sql(
            table_name="ratings",
            connection=sql,
            if_exists="append",
        )

        print(f"Valutazioni inviate a MySQL: {ratings_inserted}")

        print("Caricamento SQL completato.")



    finally:
        # Chiude la connessione anche se si verifica
        # un errore durante il caricamento.
        sql.close()


# ============================================================
# PUNTO DI INGRESSO DEL PROGRAMMA
# ============================================================

# Chiama main() solo quando questo file viene eseguito
# direttamente, ad esempio con:
#
#     python main.py
#
# Se main.py viene importato da un altro modulo,
# la pipeline non parte automaticamente.
if __name__ == "__main__":
    main()
