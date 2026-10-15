# STRUTTURA DEL PROGETTO

data-analytics-pipeline/
│
├── readers/
│   ├── __init__.py
│   ├── base_reader.py
│   |── csv_reader.py
|   └── altri_reader ...
│
├── dao/
│   ├── __init__.py
│   ├── film_dao.py
│   ├── genres_dao.py
│   └── altri_dao ...
│
├── config/
│   ├── __init__.py
│   └── sources.py
|
|
├── transformers/
│   ├── film_transformer.py
│   └── altri_transformers ... 
│
├── data/
│   ├── movies.csv
│   ├── users.sql
│   ├── views.xlsx
│   └── altri_dati ...
│
│
├── database.py
├── main.py
├── requirements.txt
└── README.md

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