# Data Analytics Pipeline

Pipeline modulare e riutilizzabile per l'acquisizione, la pulizia, la standardizzazione, la validazione e l'esportazione di dati provenienti da fonti eterogenee.

Il progetto è pensato per preparare dati affidabili per attività di data analytics e strumenti di Business Intelligence, come Power BI, mantenendo separate le responsabilità di lettura, trasformazione, gestione in memoria, persistenza e accesso ai dati.

L'architettura è progettata per essere adattabile a clienti e dataset differenti senza dover riscrivere la logica centrale.

## Indice

- [Obiettivi](#obiettivi)
- [Struttura del progetto](#struttura-del-progetto)
- [Architettura](#architettura)
  - [Readers](#1-readers)
  - [Database](#2-database)
  - [Transformers](#3-transformers)
  - [Connessione SQL](#4-connessione-sql)
  - [DAO](#5-dao)
  - [Config](#6-config)
  - [Data](#7-data)
- [Flusso dei dati](#flusso-dei-dati)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Esecuzione della pipeline](#esecuzione-della-pipeline)
- [Esportazione in MySQL](#esportazione-in-mysql)
- [Gestione delle credenziali](#gestione-delle-credenziali)
- [Estensioni future](#estensioni-future)

## Obiettivi

Il progetto mira a:

- Acquisire dati da sorgenti e formati differenti.
- Separare la logica di lettura da quella di trasformazione.
- Standardizzare nomi delle colonne e tipi di dato.
- Pulire e validare i dati prima dell'esportazione.
- Correggere anomalie note attraverso regole ripetibili.
- Organizzare i dati in una o più tabelle logiche.
- Conservare temporaneamente le tabelle elaborate in memoria tramite Pandas.
- Esportare i risultati in formato CSV.
- Trasferire le tabelle elaborate in un database MySQL.
- Predisporre interfacce DAO per l'accesso ai dati da parte dei consumatori.
- Favorire il riutilizzo del codice tra clienti e dataset differenti.

## Struttura del progetto

```text
data-analytics-pipeline/
│
├── config/
│   ├── __init__.py
│   └── sources.py
│
├── readers/
│   ├── __init__.py
│   ├── base_reader.py
│   └── csv_reader.py
│
├── transformers/
│   ├── __init__.py
│   └── film_transformer.py
│
├── validators/
│   ├── __init__.py
│   └── film_validator.py
│
├── reports/
│   ├── __init__.py
│   └── quality_report.py
│
├── dao/
│   ├── __init__.py
│   ├── film_dao.py
│   ├── genres_dao.py
│   └── altri_dao.py
│
├── data/
│   ├── file CSV originali
│   └── movies_clean.csv
│
├── database.py
├── sql_connection.py
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

*Nota: la struttura comprende sia componenti già implementati sia moduli previsti per le evoluzioni successive. I file `validators/`, `reports/` e alcuni DAO sono da considerarsi opzionali finché non vengono effettivamente implementati.*

## Architettura

### 1. Readers

La cartella `readers/` contiene le classi responsabili dell'acquisizione dei dati dalle sorgenti.

Ogni reader implementa un'interfaccia comune definita in `base_reader.py`, attraverso il metodo `read()`, che restituisce i dati in formato `pandas.DataFrame`.

Moduli principali:

- **`base_reader.py`**: definisce la classe astratta `BaseReader` e il contratto comune dei reader.
- **`csv_reader.py`**: legge file CSV e gestisce intestazioni, delimitatori, codifica e struttura delle righe.
- **Altri reader**: potranno essere aggiunti per Excel, API HTTP, database SQL e ulteriori sorgenti.

I reader si occupano dell'acquisizione dei dati, lasciando a `Database` e ai transformer le successive operazioni di elaborazione.

### 2. Database

Il file `database.py` contiene la classe `Database`, che coordina l'elaborazione dei dati acquisiti dai reader.

Le sue responsabilità sono:

1. Ricevere un reader e avviare la lettura della sorgente.
2. Rinominare le colonne secondo uno schema standard, quando richiesto.
3. Rimuovere spazi superflui e gestire stringhe vuote.
4. Verificare la presenza delle colonne obbligatorie.
5. Convertire i tipi di dato richiesti.
6. Applicare le trasformazioni specifiche della sorgente.
7. Conservare le tabelle elaborate in memoria.
8. Esportare le tabelle in un database SQL attraverso il metodo `write_to_sql()`.

Le tabelle sono archiviate nell'attributo `self.tables`, un dizionario che associa il nome della tabella al relativo DataFrame.

Esempio:

```python
self.tables = {
    "movies_clean": df_movies,
    "genres": df_genres,
}
```

Il metodo `add_source()` consente di caricare una sorgente e applicare, quando necessario, mapping, controlli sulle colonne, conversioni di tipo e trasformazioni.

Il metodo `get_table()` restituisce una copia del DataFrame richiesto, mentre `list_tables()` restituisce i nomi delle tabelle presenti in memoria.

Una singola sorgente può generare più tabelle se il transformer restituisce un dizionario di DataFrame.

**Distinzione importante:** `Database` non è il database MySQL. È il componente Python che organizza e gestisce le tabelle durante l'esecuzione della pipeline. La persistenza viene affidata a MySQL attraverso la connessione SQL.

### 3. Transformers

La cartella `transformers/` contiene le funzioni responsabili delle trasformazioni specifiche del dominio.

Queste operazioni sono separate dalla logica generica di `Database`, per rendere il codice più modulare e riutilizzabile.

Il modulo attualmente utilizzato è `film_transformer.py`.

Le sue responsabilità comprendono:

- Verifica delle colonne necessarie per l'elaborazione dei film.
- Correzione delle anomalie conosciute nei dati.
- Estrazione dell'anno dalla colonna `Title`.
- Creazione della colonna `YEAR`.
- Rimozione dell'anno dal titolo, quando estratto correttamente.
- Standardizzazione dei generi e dei relativi separatori.

Le correzioni sono applicate al DataFrame in memoria, senza modificare il file CSV originale.

In futuro potranno essere aggiunti transformer dedicati a utenti, visualizzazioni, abbonamenti e altre entità.

### 4. Connessione SQL

Il file `sql_connection.py` contiene la classe `SQLConnection`, responsabile della comunicazione tra Python e MySQL.

La connessione utilizza:

- **SQLAlchemy** per la gestione del motore SQL.
- **PyMySQL** come driver di comunicazione con MySQL.
- **python-dotenv** per caricare le configurazioni dal file `.env`.

Le principali responsabilità sono:

- Leggere i parametri di connessione.
- Creare il motore SQLAlchemy.
- Verificare che il server sia raggiungibile e che la connessione funzioni.
- Rilasciare le risorse al termine dell'operazione.

La connessione è separata da `Database`: in questo modo, la logica di elaborazione dei DataFrame non dipende direttamente dai dettagli del server SQL.

Il trasferimento dei dati viene coordinato da `Database.write_to_sql()`, che utilizza il motore fornito da `SQLConnection`.

Nel caricamento attualmente previsto, Pandas crea la tabella di destinazione a partire dalle colonne e dai tipi rilevati nel DataFrame. Per tabelle definitive con chiavi primarie, indici e vincoli espliciti sarà opportuno predisporre uno schema SQL dedicato.

### 5. DAO

La cartella `dao/` è destinata ai *Data Access Objects*.

I DAO forniscono metodi specifici per consultare i dati senza ripetere le operazioni di acquisizione e trasformazione.

Esempi di metodi previsti:

- `get_movie(movie_id)`
- `get_movies_by_year(year)`
- `get_movies_by_genre(genre)`
- `get_all_genres()`

A seconda dell'implementazione, i DAO potranno interrogare i DataFrame gestiti in memoria oppure accedere ai dati persistiti in MySQL.

La scelta della sorgente di accesso sarà definita in base al ruolo di ciascun DAO.

I DAO rappresentano un livello di accesso ai dati distinto dai reader, dai transformer e dalla gestione della connessione SQL.

### 6. Config

La cartella `config/` contiene le configurazioni delle sorgenti.

Il file `sources.py` definisce i parametri necessari per interpretare i dati in ingresso, ad esempio:

- Percorso del file.
- Formato della sorgente.
- Presenza o assenza dell'intestazione.
- Delimitatore e codifica dei CSV.
- Mapping delle colonne.
- Tipi di dato attesi.

Esempio:

```python
SOURCES = {
    "movies": {
        "path": "data/movies.csv",
        "has_header": True,
        "delimiter": ",",
        "encoding": "utf-8-sig",
    }
}
```

La configurazione separata dal codice consente di modificare le sorgenti senza intervenire sulla logica generale della pipeline.

Le password e gli altri segreti non devono essere inseriti in `sources.py`.

### 7. Data

La cartella `data/` contiene i file utilizzati durante l'acquisizione e l'elaborazione.

Può comprendere:

- CSV originali.
- CSV elaborati.
- Dataset di test.
- Altri file di input supportati dai reader implementati.

Il file `movies_clean.csv` rappresenta l'output dell'elaborazione del dataset dei film.

Il CSV originale viene mantenuto separato dall'output pulito, così da poter rieseguire le trasformazioni senza perdere la sorgente iniziale.

I dati sensibili o riservati non devono essere caricati nella repository.

## Flusso dei dati

Il flusso principale della pipeline è il seguente:

```text
          FONTI ORIGINALI
        CSV / Excel / API / SQL
                  |
                  v
               READERS
           Acquisizione dati
                  |
                  v
              DATABASE
       Mapping e pulizia generica
        Validazione delle colonne
          Conversione dei tipi
                  |
                  v
             TRANSFORMERS
       Regole specifiche del dominio
       Standardizzazione e correzioni
                  |
                  v
              self.tables
       DataFrame elaborati in memoria
                  |
          +-------+-------+
          |               |
          v               v
    ESPORTAZIONE CSV   CONNESSIONE SQL
          |               |
          v               v
  movies_clean.csv    MySQL: movies_clean
                          |
                          v
                    ANALYTICS / BI
                      Power BI

       DAO: livello di accesso ai dati,
            in fase di sviluppo.
```

L'elaborazione e la pulizia avvengono in Python. CSV e MySQL costituiscono due destinazioni distinte per i risultati prodotti.

## Installazione

### Prerequisiti

- Python compatibile con le dipendenze del progetto.
- MySQL Server, se si desidera eseguire l'esportazione SQL.
- Visual Studio Code o un ambiente di sviluppo equivalente.

### Creazione dell'ambiente virtuale

Dalla cartella principale del progetto:

```powershell
python -m venv .venv
```

Attivazione in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Su macOS/Linux:

```bash
source .venv/bin/activate
```

### Installazione delle dipendenze

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Il file `requirements.txt` contiene le dipendenze principali:

```text
pandas>=2.2,<4.0
sqlalchemy>=2.0,<3.0
pymysql>=1.1,<2.0
python-dotenv>=1.0,<2.0
```

## Configurazione

### Configurazione della sorgente

Le sorgenti vengono definite in `config/sources.py`.

Esempio:

```python
SOURCES = {
    "movies": {
        "path": "data/movies.csv",
        "has_header": True,
        "delimiter": ",",
        "encoding": "utf-8-sig",
    }
}
```

Il percorso deve corrispondere alla posizione effettiva del file CSV.

### Configurazione MySQL

Nella cartella principale del progetto, creare un file `.env` con i parametri della connessione:

```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=il_tuo_username
MYSQL_PASSWORD=la_tua_password
MYSQL_DATABASE=onthemovie
```

Sostituire i valori di esempio con quelli del proprio ambiente.

Il database `onthemovie` deve esistere sul server MySQL e l'utente configurato deve avere i permessi necessari per creare e scrivere le tabelle.

## Esecuzione della pipeline

Il file `main.py` rappresenta il punto di ingresso dell'applicazione.

Il flusso operativo è:

1. Caricare la configurazione della sorgente.
2. Inizializzare il reader.
3. Creare un'istanza di `Database`.
4. Caricare i dati tramite `add_source()`.
5. Applicare il transformer.
6. Recuperare il DataFrame elaborato.
7. Esportare il CSV pulito.
8. Collegarsi a MySQL e trasferire la tabella.

Per eseguire il programma:

```powershell
python main.py
```

Il file di output previsto per il dataset dei film è:

```text
data/movies_clean.csv
```

Il programma può essere rieseguito a partire dal CSV originale, mantenendo le regole di trasformazione in un unico punto.

## Esportazione in MySQL

La connessione è gestita da `SQLConnection`, mentre `Database.write_to_sql()` trasferisce un DataFrame presente in memoria verso una tabella MySQL.

Esempio di utilizzo:

```python
from database import Database
from sql_connection import SQLConnection

# db deve contenere già la tabella "movies_clean"
sql = SQLConnection()

try:
    sql.connect()

    rows_written = db.write_to_sql(
        table_name="movies_clean",
        connection=sql,
        sql_table_name="movies_clean",
    )

    print(f"Righe inserite: {rows_written}")

finally:
    sql.close()
```

La tabella `movies_clean` viene creata nel database indicato da `MYSQL_DATABASE`, se non esiste già.

La versione corrente utilizza `if_exists="fail"`: se la tabella di destinazione esiste, l'operazione si interrompe per evitare di sovrascrivere dati esistenti.

Questa modalità è adatta a un primo caricamento controllato. Per le esecuzioni successive sarà necessario definire una strategia di aggiornamento, ad esempio caricamento incrementale, staging o aggiornamento basato su chiavi.

**Nota sullo schema SQL:** la creazione automatica tramite Pandas non garantisce la presenza di chiavi primarie, vincoli referenziali o indici. Questi elementi dovranno essere definiti esplicitamente per le tabelle definitive.

## Gestione delle credenziali

Il file `.env` contiene informazioni riservate e non deve essere versionato.

Aggiungere al `.gitignore` almeno:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
data/
```

Se è necessario versionare dataset di esempio, è preferibile conservarli in una cartella dedicata e autorizzata, separata dai dati locali esclusi dal controllo versione.

Non inserire password, token o credenziali direttamente nei file Python o nel README.

## Estensioni future

Le evoluzioni previste comprendono:

- Reader per Excel, API HTTP e ulteriori database.
- Validazione avanzata della qualità dei dati.
- Report automatici delle anomalie e delle correzioni.
- Controlli su duplicati, chiavi e relazioni tra tabelle.
- Schemi SQL espliciti con chiavi primarie, indici e vincoli.
- Strategie di caricamento incrementale e aggiornamento delle tabelle.
- Implementazione dei DAO per l'accesso ai dati.
- Logging strutturato e gestione centralizzata degli errori.
- Test automatici con `pytest`.
- Integrazione con Power BI e altri strumenti di Business Intelligence.
- Gestione di dataset di dimensioni maggiori e valutazione di ulteriori strategie di persistenza.

L'architettura continuerà a mantenere separate acquisizione, trasformazione, gestione in memoria, persistenza e accesso ai dati, favorendo la manutenibilità e il riutilizzo del codice.
