
import pandas as pd
from readers.base_reader import BaseReader

'''
CLASSE DATABASE SUPER SCALARE
prende un reader in base alla sorgente e gliela fa leggere
rinomina le colonne secondo uno schema standard
pulisce il testo e valida le colonne obbligatorie indicate
converte i tipi di dato se richiesto
salva i dati in tabelle dentro un dizionario self.tables
può produrre una o più tabelle in formato df da una sola fonte --> trasformatore

'''

class Database:

    def __init__(self):
        self.tables: dict[str, pd.DataFrame] = {}

    def add_source(
        self,
        table_name: str,
        reader: BaseReader, #il base reader ci dice che fonte ho
        column_mapping: dict[str, str] | None = None,
        required_columns: list[str] | None = None,
        dtypes: dict[str, str] | None = None, #questo ci permette di mappare delle trasformazioni o lasciarle così come le riceviamo
        transformer=None, #aggiungi funzioni/oggetti transformatori se necessario
    ) -> None:

        #LETTURA E MAPPATURA
        df = reader.read()

        if column_mapping:
            missing = set(column_mapping) - set(df.columns)

            if missing:
                raise ValueError(
                    f"Colonne mancanti: {sorted(missing)}"
                )

            df = df.rename(columns=column_mapping)

        #PULIZIA E VALIDAZIONE
        for column in df.select_dtypes(include=["object"]).columns:
            df[column] = df[column].map(
                lambda value: ( value.strip() if isinstance(value, str) else value)
            )

            df[column] = df[column].replace("", pd.NA)

        if required_columns:
            missing = set(required_columns) - set(df.columns)

            if missing:
                raise ValueError(
                    f"Colonne obbligatorie mancanti: {sorted(missing)}"
                )

        #TRASFORMAZIONI
        if dtypes:
            for column, dtype in dtypes.items():
                if column not in df.columns:
                    raise ValueError(
                        f"Impossibile convertire '{column}': "
                        "colonna non presente."
                    )

                if dtype in ("int64", "Int64", "int", "INT"):
                    df[column] = pd.to_numeric(
                        df[column], errors="raise"
                    ).astype(dtype)

                elif dtype in ("float64", "Float64", "float", "FLOAT", "Float"):
                    df[column] = pd.to_numeric(
                        df[column], errors="raise"
                    ).astype(dtype)

                elif dtype == "string":
                    df[column] = df[column].astype("string")

                else:
                    df[column] = df[column].astype(dtype)

        result = transformer(df.copy()) if transformer else df

        #CREAZIONE TABELLE
        if isinstance(result, pd.DataFrame):
            new_tables = {table_name: result}

        elif isinstance(result, dict):
            new_tables = result

            if not all(
                isinstance(name, str)
                and isinstance(table, pd.DataFrame)
                for name, table in new_tables.items()
            ):
                raise TypeError(
                    "Il transformer deve restituire un DataFrame oppure un dizionario di DataFrame."
                )

        else:
            raise TypeError(
                "Il risultato deve essere un DataFrame oppure un dizionario di DataFrame."
            )

        if not all(name for name in new_tables):
            raise ValueError("I nomi delle tabelle non possono essere vuoti.")

        # GESTIAMO ESISTENZA DI DUPLICATI TABELLE
        conflicts = set(new_tables) & set(self.tables)

        if conflicts:
            raise ValueError(
                f"Tabelle già presenti: {sorted(conflicts)}"
            )

        self.tables.update({
            name: table.copy()
            for name, table in new_tables.items()
        })

    def get_table(self, table_name: str) -> pd.DataFrame:
        if table_name not in self.tables:
            raise KeyError(
                f"Tabella '{table_name}' non presente nel Database."
            )

        return self.tables[table_name].copy()

    def list_tables(self) -> list[str]:
        return list(self.tables.keys())

    def create_empty_table(self, table_name, columns):
        if table_name in self.tables:
            raise ValueError(
                f"La tabella '{table_name}' esiste già."
            )

        self.tables[table_name] = pd.DataFrame(
            columns=columns
        )

    
    def write_to_sql(
            self,
            table_name: str,
            connection,
            sql_table_name: str | None = None,
        ) -> int:
        if table_name not in self.tables:
            raise KeyError(
                f"Tabella '{table_name}' non presente in memoria."
            )

        if connection.engine is None:
            raise RuntimeError(
                "Connessione SQL non attiva. Chiama connect() prima."
            )

        df = self.get_table(table_name)
        destination = sql_table_name or table_name

        df.to_sql(
            name=destination,
            con=connection.engine,
            if_exists="fail",
            index=False,
        )

        return len(df)

'''

Come si usa??

reader = MioReader("mio/file.csv")
OPPURE
reader = MioReader(
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port":os.getenv("PORT"))

db = Dataabase()

db.add_source(
    table_name = "mia_tabllea",
    reader = reader,
    column_mapping={
        "colonnaID" : "id_colonna",
        "Titoli" : "titoli_film",
        ...
        },
    required_columns=["id_colonna", "titoli_film", etc],
    dtypes={
        "movie_id": "int",
        "title": "str",
        ...
        },
     )

'''