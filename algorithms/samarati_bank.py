from itertools import product
from typing import List, Dict, Tuple
import pandas as pd
from utils.loss_metrics_bank import categorical_loss_metric_bank
from operator import itemgetter

# Lattice -> gestione delle gerarchie di generalizzazione
class LatticeB:
    def __init__(self, hierarchies: Dict[str, Dict[str, str]], quasi_id: List[str], heights: Dict[str, int]):
        self.hierarchies = hierarchies  # Gerarchie di generalizzazione per ogni attributo
        self.heights = heights  # Altezze delle gerarchie
        self.total_height = sum(heights.values())  # Somma delle altezze
        self.attr_num = len(self.heights)  # Numero di attributi quasi-identifier
        self.quasi_id = quasi_id  # Lista dei quasi-identificatori
        self.height_array = [list(range(h + 1)) for h in self.heights.values()]  # Array contenente i livelli di generalizzazione per ogni attributo
        self.lattice_map = self.build_map()  # Tutte possibili combinazioni di livelli di generalizzazione

    # Costruzione del reticolo di generalizzazione
    def build_map(self) -> Dict[int, List[Tuple[int, ...]]]:
        lattice_map = {h: [] for h in range(self.total_height + 1)}
        all_combinations = list(product(*self.height_array))  # Generazione di tutte le combinazioni di livelli di generalizzazione
        for dist in all_combinations:
            temp = sum(dist)
            if temp <= self.total_height:
                lattice_map[temp].append(dist)  # Assegnamento delle combinazioni di livelli al loro livello totale corrispondente
        return lattice_map

    # Vettori di generalizzazione per un dato livello di altezza
    def get_vectors(self, height: int) -> List[Tuple[int, ...]]:
        return self.lattice_map[height]

    # Verifica dei vincoli k e maxsup
    def satisfies(self, vector: Tuple[int, ...], k: int, table: pd.DataFrame, maxsup: int) -> Tuple[bool, int, pd.DataFrame]:
        anonymized_table = self.generalization(table, vector)
        valid, anonymized_table, sup = self.validation(anonymized_table, k, maxsup)
        return valid, sup, anonymized_table

    # Applica generalizzazione ai dati
    def generalization(self, table: pd.DataFrame, vector: Tuple[int, ...]) -> pd.DataFrame:
        table = table.copy()
        for attribute, gen_level in zip(self.quasi_id, vector):
            col = [str(elem) for elem in table[attribute]]
            # Antenati nella gerarchia di generalizzazione
            ancestors = {k: k for k in set(col)}
            for k in ancestors:
                for _ in range(gen_level):
                    ancestors[k] = self.hierarchies[attribute][ancestors[k]]
            # Sostituzione vecchi valori con gli antenati generalizzati
            table[attribute] = [ancestors[elem] for elem in col]
        return table

    # Verifica k-anonymity e maxsup
    def validation(self, table: pd.DataFrame, k: int, maxsup: int) -> Tuple[bool, pd.DataFrame, int]:
        sup = 0  # Contatore delle soppressioni
        table = table.copy()
        anonymized_table = pd.DataFrame(columns=table.columns)
        while sup <= maxsup and not table.empty:
            first_row = table.iloc[0][self.quasi_id]
            row_counts = table.shape[0]
            conditions = table[self.quasi_id] != first_row
            residual_table = table[~conditions.any(axis=1)]  # Righe da sopprimere
            table = table[conditions.any(axis=1)]  # Righe rimanenti
            new_row_counts = table.shape[0]
            delta = row_counts - new_row_counts  # Numero di righe sopprimibili
            if delta < k:
                sup += delta
            else:
                anonymized_table = pd.concat([anonymized_table, residual_table])
        return sup <= maxsup, anonymized_table, sup

# Algoritmo di anonimizzazione Samarati
def samaratiB(
    table: pd.DataFrame,
    lattice: LatticeB,
    leaves_num: Dict[str, int],
    sensitive: str,
    k: int = 10,
    maxsup: int = 20,
    optimal: bool = False
) -> Tuple[pd.DataFrame, Tuple[int, ...], int, float]:
    low, high = 0, lattice.total_height
    satisfied_vector = lattice.get_vectors(lattice.total_height)[0]
    solution = lattice.generalization(table=table, vector=satisfied_vector)
    final_sup = None

    # Ricerca binaria per trovare il livello minimo di generalizzazione che soddisfa i vincoli
    while low < high:
        mid = (low + high) // 2
        vectors = lattice.get_vectors(mid)
        reach_k = False
        for v in vectors:
            valid, sup, anonymized_table = lattice.satisfies(vector=v, k=k, table=table, maxsup=maxsup)
            if valid:
                satisfied_vector = v
                final_sup = sup
                solution = anonymized_table
                reach_k = True
                break
        if reach_k:
            high = mid
        else:
            low = mid + 1

    # Calcola la metrica di perdita per la tabella anonimizzata
    loss_metric = categorical_loss_metric_bank(solution.loc[:, lattice.quasi_id], leaves_num, lattice.hierarchies, final_sup)

    return solution, satisfied_vector, final_sup, loss_metric
