# Data Analytics Pipeline

Pipeline modulare e riutilizzabile per l'acquisizione, la pulizia, la standardizzazione e l'organizzazione di dati provenienti da fonti eterogenee, con l'obiettivo di renderli disponibili per analisi e strumenti di Business Intelligence, come Power BI.

Il progetto è progettato per supportare fonti differenti e poter essere adattato a clienti e dataset diversi senza dover riscrivere la logica centrale.

## Indice

- [Obiettivi](#obiettivi)
- [Struttura del progetto](#struttura-del-progetto)
- [Architettura](#architettura)
  - [Readers](#1-readers)
  - [Database](#2-database)
  - [Transformers](#3-transformers)
  - [DAO](#4-dao)
  - [Config](#5-config)
  - [Data](#6-data)
- [Flusso dei dati](#flusso-dei-dati)
- [Installazione](#installazione)
- [Configurazione e utilizzo](#configurazione-e-utilizzo)
- [Estensioni future](#estensioni-future)

## Obiettivi

Il progetto mira a:

- Acquisire dati da sorgenti e formati differenti.
- Separare la logica di lettura da quella di trasformazione.
- Standardizzare nomi delle colonne e tipi di dato.
- Pulire e validare i dati prima di renderli disponibili.
- Normalizzare i dati in una o più tabelle logiche.
- Esporre un'interfaccia di accesso ai dati tramite DAO.
- Favorire il riutilizzo del codice tra clienti e dataset differenti.

## Struttura del progetto

```text
data-analytics-pipeline/
│
├── config/
│   ├── __init__.py
│   └── sources.py
│
├── dao/
│   ├── __init__.py
│   ├── film_dao.py
│   ├── genres_dao.py
│   └── altri_dao.py
│
├── data/
│   ├── movies.csv
│   ├── users.sql
│   ├── views.xlsx
│   └── altri_dati...
│
├── readers/
│   ├── __init__.py
│   ├── base_reader.py
│   ├── csv_reader.py
│   └── altri_reader.py
│
├── transformers/
│   ├── __init__.py
│   ├── film_transformer.py
│   └── altri_transformers.py
│
├── tests/
│   └── ...
│
├── database.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

*Nota: la struttura rappresenta l'organizzazione prevista del progetto. I moduli non ancora implementati verranno aggiunti durante lo sviluppo.*

## Architettura

### 1. Readers

La cartella `readers/` contiene le classi responsabili della lettura delle diverse sorgenti.

Ogni reader espone un'interfaccia comune, definita in `base_reader.py`, attraverso il metodo `read()`. Il metodo restituisce i dati in un formato tabellare compatibile con `pandas.DataFrame`.

Moduli principali:

- **`base_reader.py`**: definisce la classe astratta `BaseReader` e il contratto comune dei reader.
- **`csv_reader.py`**: legge file CSV e gestisce intestazioni, delimitatori, codifica e struttura delle righe.
- **Altri reader**: potranno essere implementati per Excel, API HTTP, database SQL e altre sorgenti.

L'obiettivo è rendere `Database` indipendente dal formato originale dei dati.

### 2. Database

Il file `database.py` contiene la classe `Database`, che coordina l'elaborazione dei dati acquisiti dai reader.

Le sue responsabilità sono:

1. Ricevere il reader corrispondente alla sorgente e avviare la lettura.
2. Rinominare le colonne secondo uno schema standard.
3. Pulire i valori e gestire i dati mancanti secondo le regole definite.
4. Validare la presenza delle colonne obbligatorie.
5. Convertire i tipi di dato quando richiesto.
6. Applicare trasformazioni specifiche.
7. Conservare le tabelle elaborate in memoria.

Le tabelle sono archiviate nell'attributo `self.tables`, un dizionario che associa il nome di ogni tabella al relativo `pandas.DataFrame`.

Esempio:

```python
self.tables = {
    "dim_film": df_film,
    "dim_genre": df_genre,
    "bridge_film_genre": df_film_genre,
}
```

Una singola sorgente può quindi generare più tabelle, quando una trasformazione lo richiede.

**Nota:** nella versione attuale, `Database` gestisce tabelle in memoria e non costituisce un database persistente. I dati vengono conservati durante l'esecuzione dell'applicazione.

### 3. Transformers

La cartella `transformers/` contiene le funzioni responsabili delle trasformazioni specifiche del dominio.

Queste operazioni sono separate dalla logica generica di `Database`, così da poter essere riutilizzate o sostituite senza modificare i reader.

Esempi:

- **`film_transformer.py`**: estrae l'anno dal titolo di un film e prepara i dati per le elaborazioni successive.
- **Altri transformer**: potranno gestire la normalizzazione di generi, visualizzazioni, utenti, abbonamenti o altre entità.

Un transformer può restituire un singolo `DataFrame` oppure, se previsto dal flusso di elaborazione, più tabelle.

### 4. DAO

La cartella `dao/` contiene i *Data Access Objects*, che forniscono metodi specifici per consultare le tabelle elaborate.

Esempi di metodi:

- `get_movie(movie_id)`
- `get_movies_by_year(year)`
- `get_movies_by_genre(genre)`
- `get_all_genres()`

Ogni DAO si occupa dell'accesso ai dati e delle query applicative, senza ripetere le operazioni di lettura, pulizia o standardizzazione.

I DAO utilizzano le tabelle messe a disposizione da `Database` e presuppongono che queste rispettino lo schema standard concordato.

### 5. Config

La cartella `config/` contiene le configurazioni delle sorgenti e i parametri necessari per acquisire e interpretare i dati.

Il file `sources.py` può contenere informazioni come:

- Percorso o identificativo della sorgente.
- Formato del file.
- Presenza o assenza di intestazioni.
- Delimitatori e codifica dei CSV.
- Mapping tra colonne originali e nomi standard.
- Colonne obbligatorie e tipi di dato attesi.
- Parametri specifici per API HTTP o connessioni ad altre fonti.

L'obiettivo è separare la configurazione dal codice, evitando di modificare `Database` ogni volta che cambiano i parametri di una sorgente.

Credenziali, token e altri segreti non devono essere inseriti direttamente nei file versionati della configurazione.

### 6. Data

La cartella `data/` è destinata ai dataset di input utilizzati durante lo sviluppo e i test.

Può contenere, ad esempio:

- File CSV con dati sui film.
- File con informazioni sugli utenti.
- Dati relativi alle visualizzazioni.
- Dati sugli abbonamenti.
- Dataset in altri formati, quando saranno implementati i reader corrispondenti.

I dati sensibili o riservati dei clienti non devono essere caricati nella repository. I dataset di esempio condivisi devono essere autorizzati e privi di informazioni riservate.

## Flusso dei dati

Il flusso generale della pipeline è il seguente:

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
     Mapping e standardizzazione
       Pulizia e validazione
      Conversione dei tipi
               |
               v
          TRANSFORMERS
    Trasformazioni specifiche
      e normalizzazione
               |
               v
          self.tables
     Tabelle in memoria (DataFrame)
               |
               v
             DAO
       Accesso ai dati
               |
               v
       ANALYTICS / POWER BI
```

## Installazione

### Prerequisiti

- Python compatibile con le versioni utilizzate dal progetto.
- Git.

### Creazione dell'ambiente virtuale

Dalla cartella principale del progetto:

```bash
python -m venv .venv
```

Attivazione dell'ambiente:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### Installazione delle dipendenze

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configurazione e utilizzo

Le sorgenti vengono configurate in `config/sources.py`.

Esempio di configurazione CSV:

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

Il punto di ingresso `main.py` utilizza la configurazione per inizializzare il reader e caricare i dati in `Database`.

Esempio:

```python
from config.sources import SOURCES
from database import Database
from readers.csv_reader import CSVReader

config = SOURCES["movies"]

reader = CSVReader(
    path=config["path"],
    has_header=config["has_header"],
    delimiter=config["delimiter"],
    encoding=config["encoding"],
)

db = Database()
db.add_source("raw_movies", reader)

movies = db.get_table("raw_movies")
print(movies.head())
```

Per avviare il programma:

```bash
python main.py
```

Il percorso del file deve corrispondere alla posizione effettiva del dataset. La configurazione può essere adattata localmente senza modificare la logica generale della pipeline.

## Estensioni future

Le possibili evoluzioni del progetto includono:

- Implementazione di reader per Excel, API HTTP e database SQL.
- Configurazione completa delle sorgenti e dei relativi mapping.
- Validazione avanzata della qualità dei dati.
- Controllo di duplicati, chiavi primarie e relazioni tra tabelle.
- Normalizzazione delle entità e definizione di uno schema standard.
- Implementazione dei DAO per tutte le tabelle.
- Introduzione di logging e report degli errori.
- Test automatici con `pytest`.
- Valutazione di una soluzione di persistenza per dataset di dimensioni maggiori.

L'architettura verrà sviluppata progressivamente, mantenendo separate acquisizione, trasformazione e accesso ai dati.