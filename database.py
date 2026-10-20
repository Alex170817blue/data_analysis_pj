
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
        reader: BaseReader,
        column_mapping: dict[str, str] | None = None,
        required_columns: list[str] | None = None,
        dtypes: dict[str, str] | None = None,
        transformer=None,
    ) -> None:

        # Lettura della sorgente
        df = reader.read()

        # Mappatura delle colonne
        if column_mapping:
            missing = set(column_mapping) - set(df.columns)

            if missing:
                raise ValueError(
                    f"Colonne mancanti per la mappatura: {sorted(missing)}"
                )

            df = df.rename(columns=column_mapping)

        # Pulizia delle stringhe
        for column in df.select_dtypes(include=["object"]).columns:
            df[column] = df[column].map(
                lambda value: (
                    value.strip() if isinstance(value, str) else value
                )
            )
            df[column] = df[column].replace("", pd.NA)

        # Validazione delle colonne obbligatorie
        if required_columns:
            missing = set(required_columns) - set(df.columns)

            if missing:
                raise ValueError(
                    f"Colonne obbligatorie mancanti: {sorted(missing)}"
                )

        # Conversione dei tipi
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

                elif dtype in (
                    "float64", "Float64", "float", "FLOAT", "Float"
                ):
                    df[column] = pd.to_numeric(
                        df[column], errors="raise"
                    ).astype(dtype)

                elif dtype == "string":
                    df[column] = df[column].astype("string")

                else:
                    df[column] = df[column].astype(dtype)

        # Trasformazione: chiamata una sola volta
        result = transformer(df.copy()) if transformer else df

        # Normalizzo il risultato in un dizionario di DataFrame
        if isinstance(result, pd.DataFrame):
            new_tables = {table_name: result}

        elif isinstance(result, dict):
            new_tables = result

            if not all(
                isinstance(name, str)
                and name.strip()
                and isinstance(table, pd.DataFrame)
                for name, table in new_tables.items()
            ):
                raise TypeError(
                    "Il transformer deve restituire un DataFrame "
                    "oppure un dizionario con nomi e DataFrame validi."
                )

        else:
            raise TypeError(
                "Il transformer deve restituire un DataFrame "
                "oppure un dizionario di DataFrame."
            )

        # Verifico le collisioni prima di registrare tabelle
        conflicts = set(new_tables) & set(self.tables)

        if conflicts:
            raise ValueError(
                f"Tabelle già presenti: {sorted(conflicts)}"
            )

        # Registro tutte le tabelle
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

    # Crea una tabella vuota con le colonne specificate
    def create_empty_table(self, table_name, columns):
        if table_name in self.tables:
            raise ValueError(
                f"La tabella '{table_name}' esiste già."
            )

        self.tables[table_name] = pd.DataFrame(
            columns=columns
        )

    # Scrive una tabella in un database SQL    
    def write_to_sql(
            self,
            table_name: str,
            connection,
            sql_table_name: str | None = None,
            if_exists: str = "fail",
        ) -> int:
        if table_name not in self.tables:
            raise KeyError(
                f"Tabella '{table_name}' non presente in memoria."
            )

        if connection.engine is None:
            raise RuntimeError(
                "Connessione SQL non attiva. Chiama connect() prima."
            )

        if if_exists not in {"fail", "append"}:
            raise ValueError(
                "if_exists deve essere 'fail' oppure 'append'."
            )

        df = self.get_table(table_name)
        destination = sql_table_name or table_name

        df.to_sql(
            name=destination,
            con=connection.engine,
            if_exists=if_exists,
            index=False,
        )

        return len(df)

'''


    Gestisce tabelle Pandas in memoria e permette di preparare i dati
    per l'esportazione in un database SQL.

    COME SI USA
    -----------
    1. Creare un'istanza della classe Database.
    2. Caricare una sorgente tramite add_source(), passando un reader
       e, se necessario, le opzioni per la mappatura delle colonne,
       la validazione, la conversione dei tipi e la trasformazione
       dei dati.
    3. Recuperare una tabella con get_table() oppure visualizzare
       le tabelle caricate con list_tables().
    4. Creare una tabella vuota con create_empty_table(), se necessario.
    5. Esportare una tabella verso SQL con write_to_sql(), dopo aver
       stabilito la connessione al database.

    Il metodo add_source() può registrare una singola tabella oppure
    più tabelle, se il transformer restituisce un dizionario di
    DataFrame.

    Le tabelle vengono conservate in memoria: non sono salvate
    automaticamente su disco o nel database SQL.

    Nota: write_to_sql() supporta 'fail' per evitare di sovrascrivere
    una tabella esistente e 'append' per aggiungere righe. Con 'append',
    eventuali chiavi primarie già presenti possono causare errori.
    

    # 1. Creo il database in memoria
    database = Database()

    # 2. Carico e trasformo una sorgente
    database.add_source(
        table_name="movies",
        reader=reader,
        transformer=transform_movies
    )

    # 3. Visualizzo le tabelle disponibili
    print(database.list_tables())

    # 4. Recupero una tabella
    movies_df = database.get_table("movies")

    # 5. Esporto la tabella in SQL
    connection.connect()
    database.write_to_sql(
        table_name="movies",
        connection=connection,
        if_exists="append"
    )
    
'''