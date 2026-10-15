# STRUTTURA DEL PROGETTO

data-analytics-pipeline/
│
├── config/
│   ├── __init__.py
│   └── sources.py              # Configurazioni delle fonti (delimitatori, porte, endpoint HTTP, ecc.)
│
├── dao/
│   ├── __init__.py
│   ├── film_dao.py             # Metodi specifici per accedere ai dati dei film
│   ├── genres_dao.py           # Metodi specifici per accedere ai dati dei generi
│   └── altri_dao.py            # Ulteriori Data Access Object
│
├── data/
│   ├── movies.csv              # File di dati CSV
│   ├── users.sql               # Script o dump di dati SQL
│   ├── views.xlsx              # File di dati Excel
│   └── altri_dati...
│
├── readers/
│   ├── __init__.py
│   ├── base_reader.py          # Classe base astratta per i lettori
│   ├── csv_reader.py           # Lettore specifico per file CSV
│   └── altri_reader.py         # Ulteriori moduli di lettura sorgenti
│
├── transformers/
│   ├── __init__.py
│   ├── film_transformer.py     # Logica di trasformazione specifica per i film
│   └── altri_transformers.py
│
├── database.py                 # Core engine per l'ingestione, pulizia e archiviazione in memoria
├── main.py                     # Entry point dell'applicazione
├── README.md                   # Documentazione del progetto
└── requirements.txt            # Dipendenze del progetto


# Readers
contiene le classi responsabili della lettura delle diverse sorgenti

# Database.py
prende un reader in base alla sorgente e gliela fa leggere
rinomina le colonne secondo uno schema standard
pulisce il testo e valida le colonne obbligatorie indicate
converte i tipi di dato se richiesto
salva i dati in tabelle dentro un dizionario self.tables
può produrre una o più tabelle in formato df da una sola fonte --> trasformatore

# DAO
forniscono metodi specifici per accedere alle tabelle elaborate. non si
occupano della lettura del file in sé, né ripetono le operazioni di pulizia. Fanno tipo : get movie, get movie for year, etc.

# Config
ci inseriamo le configurazioni delle fonti, eventuali porte, http, delimitatori, etc