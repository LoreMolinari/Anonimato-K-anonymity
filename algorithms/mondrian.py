from statistics import median
import random
import pandas as pd
from utils.loss_metrics_bank import numerical_loss_metric_bank
from typing import List, Dict, Tuple

import warnings
warnings.filterwarnings("ignore", message="Setting an item of incompatible dtype", category=FutureWarning)


# Partizionamento dei dati per l'algoritmo Mondrian
class Partition:
    def __init__(self, table: pd.DataFrame, quasi_id: List[str], k: int):
        self.table = table  # Tabella
        self.quasi_id = quasi_id  # Lista quasi identificatori
        self.k = k  # Parametro k
        self.allow_split = self.set_allow_split()  # Mappa delle colonne
        self.lhs = None  # Partizione di sinistra
        self.rhs = None  # Partizione di destra
        self.summary = pd.DataFrame()  # Tabella anonimizzata

    # Mappatura delle divisioni possibili delle colonne
    def set_allow_split(self) -> Dict[str, bool]:
        allow_split = {}
        for qi in self.quasi_id:
            if not self.table[qi].tolist():  # Colonna vuota
                allow_split[qi] = False
                break
            split_val = median(self.table[qi].tolist())  # Valore mediano
            # Verifica del vincolo di k-anonimity
            lhs_tb = self.table[self.table[qi] <= split_val]
            rhs_tb = self.table[self.table[qi] > split_val]
            allow_split[qi] = self.check(lhs_tb, rhs_tb)
        return allow_split

    # Selezione casuale tra tutte le dimensioni divisibili
    def choose_dimension(self) -> str:
        candidates = [qi for qi in self.quasi_id if self.allow_split[qi]]
        return random.choice(candidates)

    # Divisione della tabella in base alla dimensione e al valore mediano
    def split(self, dim: str, split_val: float) -> Tuple['Partition', 'Partition']:
        lhs_tb = self.table[self.table[dim] <= split_val]
        rhs_tb = self.table[self.table[dim] > split_val]
        lhs = Partition(table=lhs_tb, quasi_id=self.quasi_id, k=self.k)
        rhs = Partition(table=rhs_tb, quasi_id=self.quasi_id, k=self.k)
        return lhs, rhs

    # Verifica del vincolo di k-anonimity
    def check(self, table1: pd.DataFrame, table2: pd.DataFrame) -> bool:
        return table1.shape[0] >= self.k and table2.shape[0] >= self.k

    # Partizionamento ricorsivo
    def strict_anonymize(self) -> pd.DataFrame:
        if not any(self.allow_split.values()): 
            for dim in self.quasi_id:  # Sostituisce i valori originali con il nuovo intervallo
                max_val = max(self.table[dim].tolist())
                min_val = min(self.table[dim].tolist())
                if min_val != max_val:  # Sostituisce la colonna della dimensione selezionata
                    self.table.loc[:, dim] = [f'{min_val}-{max_val}'] * self.table.shape[0]
            self.summary = self.table.copy()

        else:
            # Scelta della dimensione dal dominio degli attributi
            dim = self.choose_dimension()
            # Valore mediano
            split_val = median(self.table[dim].tolist())
            # Divisione tabella e verifica del vincolo di k-anonimity
            lhs, rhs = self.split(dim, split_val)
            if not self.check(lhs.table, rhs.table):
                self.allow_split[dim] = False
            
            # Combinazione delle tabelle (sinistra/destra)
            lhs_summary = lhs.strict_anonymize()
            rhs_summary = rhs.strict_anonymize()
            self.summary = pd.concat([lhs_summary, rhs_summary])

        return self.summary

# Implementazione dell'algoritmo di anonimizzazione Mondrian
def mondrian(table: pd.DataFrame, quasi_id: List[str], k: int, sensitive: str) -> Tuple[pd.DataFrame, float]:
    partition = Partition(table=table, quasi_id=quasi_id, k=k)
    partition.strict_anonymize()
    anonymized_table = partition.summary
    
    loss_metric = numerical_loss_metric_bank(anonymized_table.loc[:, quasi_id])
    print('\n====================')

    return anonymized_table, loss_metric
