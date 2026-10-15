
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine


load_dotenv()


class SQLConnection:
    def __init__(self):
        self.engine: Engine | None = None

    def connect(self) -> None:
        url = URL.create(
            drivername="mysql+pymysql",
            username=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            database=os.environ["MYSQL_DATABASE"],
        )

        self.engine = create_engine(
            url,
            pool_pre_ping=True,
        )

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            print("Connessione a MySQL riuscita!")

        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
