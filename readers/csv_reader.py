
import csv
import pandas as pd
from readers.base_reader import BaseReader

'''
READER DEI CSV
utilizzabile con csv con e senza intestazioni, n colonne, vari delimitatori
campi con virgolette e non, codifica a scelta e controllo righe.
restituisce i valori come testo e non converte nulla --> elaborazione nel
database.py
'''


class CSVReader(BaseReader):
    def __init__(
        self,
        path: str,
        has_header: bool = True,
        columns: list[str] | None = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ):
        self.path = path
        self.has_header = has_header
        self.columns = columns
        self.delimiter = delimiter
        self.encoding = encoding

        if not has_header and not columns:
            raise ValueError("Per un CSV senza intestazioni devi specificare le colonne nel parametro columns")

        if columns is not None and len(columns) != len(set(columns)):
            raise ValueError("I nomi delle colonne devono essere univoci")

    def read(self) -> pd.DataFrame:
        with open(self.path, mode="r",encoding=self.encoding, newline="") as file:

            reader = csv.reader(file, delimiter=self.delimiter, strict=True,)
            rows = []
            headers = None

            for row in reader:
                #ignoro le righe che sono vuote
                if not row or all(value.strip() == "" for value in row):
                    continue

                if headers is None and self.has_header:
                    headers = [value.strip() for value in row]

                    if len(headers) != len(set(headers)):
                        raise ValueError(
                            f"Intestazioni duplicate nel file: {self.path}"
                        )

                    continue

                rows.append(row)

        if self.has_header:
            if headers is None:
                raise ValueError(f"Il CSV è vuoto: {self.path}")

            column_names = headers
        else:
            column_names = self.columns

        expected = len(column_names)

        for row_number, row in enumerate(rows, start=1):
            if len(row) != expected:
                raise ValueError(
                    f"Riga dati {row_number} del file {self.path}: "
                    f"attese {expected} colonne, trovate {len(row)}."
                )

        return pd.DataFrame(rows, columns=column_names)

'''
Come si usa??

reader = CSVReader("mio/file.csv")
OPPURE
reader = CSVReader("mio/file.csv", has_header=False, 
    columns=["CientID", "Name", "Age", "Country"], delimiter="|")

    
'''