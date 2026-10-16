# DB_SAC01 — Pipeline di Data Analytics

## Descrizione del progetto

Il progetto implementa una pipeline Python per la lettura, la pulizia, la trasformazione e l'organizzazione di dati cinematografici, con esportazione in CSV e MySQL.

L'obiettivo è separare le responsabilità in moduli indipendenti, rendendo il codice più riutilizzabile, manutenibile e facilmente estendibile.

## Architettura

La pipeline segue questo flusso:

**CSV sorgente → Readers → Transformations → Database in memoria → MySQL**

I DAO permettono inoltre di accedere ai dati attraverso oggetti Python, come `Movie` e `Genre`.

### Struttura del progetto

```text
DB_SAC01/
├── config/
│   └── sources.py
├── readers/
│   ├── __init__.py
│   ├── base_reader.py
│   └── csv_reader.py
├── transformations/
│   ├── __init__.py
│   ├── film_transformers.py
│   └── relational_movie_transformer.py
├── dao/
│   ├── __init__.py
│   ├── dao_movie.py
│   └── dao_genre.py
├── data/
│   ├── Elenco Movies definitivo.csv
│   └── movies_clean.csv
├── model.py
├── database.py
├── sql_connection.py
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Componenti principali

### 1. Configurazione delle sorgenti — `config/sources.py`

Contiene le informazioni necessarie per individuare le sorgenti dati, come percorso del file, presenza dell'intestazione, delimitatore e codifica.

### 2. Readers — `readers/`

- `BaseReader`: definisce l'interfaccia comune per la lettura dei dati.
- `CSVReader`: legge file CSV e restituisce DataFrame Pandas, effettuando controlli strutturali sui dati.

### 3. Transformations — `transformations/`

- `film_transformers.py`: pulisce e normalizza i dati dei film, corregge alcune anomalie, estrae l'anno dal titolo e normalizza i generi.
- `relational_movie_transformer.py`: trasforma il dataset in tre DataFrame relazionali:
  - `movies`: informazioni sui film;
  - `genres`: catalogo dei generi;
  - `movie_genres`: associazioni tra film e generi.

### 4. Database in memoria — `database.py`

La classe `Database` gestisce i DataFrame Pandas in memoria.

Le sue responsabilità comprendono:
- caricamento delle sorgenti;
- mappatura e pulizia delle colonne;
- validazione dei dati;
- conversione dei tipi;
- applicazione dei transformer;
- registrazione e recupero delle tabelle;
- esportazione dei DataFrame verso SQL.

Questa classe **non è il database MySQL**: rappresenta il livello di gestione dei dati in memoria.

### 5. Connessione SQL — `sql_connection.py`

La classe `SQLConnection` gestisce la connessione a MySQL tramite SQLAlchemy e PyMySQL, utilizzando variabili d'ambiente per le credenziali.

Il database di destinazione è `onthemovie`.

### 6. Model — `model.py`

Definisce le classi Python:
- `Movie`: rappresenta un film con ID, titolo, anno e lista dei generi associati.
- `Genre`: rappresenta un genere con nome e lista dei film associati.

Le relazioni tra film e generi sono bidirezionali in memoria.

### 7. DAO — `dao/`

- `DaoMovie`: carica i film dal CSV pulito, consente la ricerca per ID e restituisce l'elenco dei film.
- `DaoGenre`: gestisce i generi e consente la ricerca per nome e il recupero di tutti i generi.

**Nota:** nella versione attuale i DAO leggono il CSV pulito e costruiscono oggetti Python in memoria; non interrogano direttamente MySQL.

## Schema relazionale MySQL

Il database utilizza tre tabelle:

| Tabella | Contenuto |
|---|---|
| `movies` | ID, titolo e anno del film |
| `genres` | ID e nome del genere |
| `movie_genres` | Associazioni tra film e generi |

Le chiavi primarie identificano i record, mentre le chiavi esterne di `movie_genres` garantiscono i riferimenti alle tabelle `movies` e `genres`.

## Requisiti

- Python 3.10 o superiore
- MySQL
- Pacchetti Python elencati in `requirements.txt`

## Installazione e configurazione

### 1. Creare l'ambiente virtuale

Su Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Installare le dipendenze

```powershell
python -m pip install -r requirements.txt
```

### 3. Configurare MySQL

Creare un file `.env` nella root del progetto:

```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=onthemovie
```

Sostituire i valori di esempio con le proprie credenziali.

Il file `.env` non deve essere condiviso tramite Git. Inserirlo in `.gitignore`.

### 4. Configurare il CSV

Verificare che il percorso della sorgente in `config/sources.py` corrisponda al file effettivamente presente nella cartella `data/`.

## Esecuzione

Dalla root del progetto:

```powershell
python main.py
```

Lo script esegue la lettura e la trasformazione dei dati, crea le tabelle relazionali in memoria, genera il CSV pulito, inizializza i DAO e avvia la connessione a MySQL per l'esportazione.

Il CSV pulito viene salvato in:

```text
data/movies_clean.csv
```

## Risultati attesi

Sul dataset attualmente utilizzato, la pipeline produce:

| Elemento | Quantità |
|---|---:|
| Film | 3.883 |
| Generi distinti | 18 |
| Associazioni film-genere | 6.402 |

I DAO consentono, ad esempio, di recuperare un film tramite `get_movie_by_id()` e un genere tramite `get_genre_by_name()`.

## Stato attuale e sviluppi futuri

Le funzionalità implementate comprendono:
- lettura e validazione dei CSV;
- pulizia e trasformazione dei dati;
- creazione di DataFrame relazionali;
- esportazione del CSV pulito;
- connessione a MySQL;
- creazione di oggetti `Movie` e `Genre` tramite DAO.

Sviluppi futuri:
- implementare una strategia di caricamento SQL ripetibile e sicura;
- gestire aggiornamenti e reinserimenti senza conflitti di chiave primaria;
- valutare DAO che leggano direttamente da MySQL;
- aggiungere test automatici per readers, transformer e DAO.

**Attenzione:** l'esportazione SQL attuale utilizza `append`. Se le tabelle contengono già gli stessi record, una nuova esecuzione può fallire a causa delle chiavi primarie duplicate. Prima di ripetere il caricamento completo è necessario gestire esplicitamente i dati esistenti.

