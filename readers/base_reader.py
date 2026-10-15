
from abc import ABC, abstractmethod
import pandas as pd

'''
CLASSE BASE READER
è una classe astratta e non viene utilizzata 
direttamente, ma serve come interfaccia per i reader specifici.
è tipo un poliziotto che controlla che i reader abbiano 
il metodo read() e restituiscano un DataFrame

'''

class BaseReader(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame:
        raise NotImplementedError
