import timeit
import sqlite3
import pandas as pd
from utils.data_loader import load_data, default_data_config, display_table

def create_table(conn, table_name, data):
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    data.to_sql(table_name, conn, index=False, if_exists='replace')
    conn.commit()

def measure_access_time(conn, query, number=10):
    cursor = conn.cursor()
    def access():
        cursor.execute(query)
        cursor.fetchall()
    time = timeit.timeit(access, number=number)
    return time / number


def count_rows(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return len(rows)

config = {'data': default_data_config, 'samarati': True}
data_original = load_data(config)['table']

# Creazione del database nella memoria locale
conn = sqlite3.connect(':memory:')

# Creazione delle tabelle nel database
create_table(conn, 'original', data_original)
data_anonymizedM = pd.read_csv('results/mondrian.csv')
data_anonymizedS = pd.read_csv('results/samarati.csv')
create_table(conn, 'anonymizedS', data_anonymizedS)
create_table(conn, 'anonymizedM', data_anonymizedM)

# Stampa delle colonne delle tabelle
print("\nColonne dei dati originali:", data_original.columns)
print("Colonne dei dati anonimizzati (Samarati):", data_anonymizedS.columns)
print("Colonne dei dati anonimizzati (Mondrian):", data_anonymizedM.columns)

# Visualizza prime righe dei dati
print("\nPrime righe dei dati originali:")
print(data_original.head())
print("\nPrime righe dei dati anonimizzati (Samarati):")
print(data_anonymizedS.head())
print("\nPrime righe dei dati anonimizzati (Mondrian):")
print(data_anonymizedM.head())

# Selezione dell'attributo su cui eseguire la query (utilizzo age="39" come test)
valid_column = data_original.columns[0]
valid_column_anonymizedS = data_anonymizedS.columns[0]  
valid_column_anonymizedM = data_anonymizedM.columns[0]  

query_original = f"SELECT * FROM original WHERE {valid_column} = '{data_original[valid_column].iloc[0]}'"
query_anonymizedS = f"SELECT * FROM anonymizedS WHERE \"{valid_column_anonymizedS}\" = \"{data_anonymizedS[valid_column_anonymizedS].iloc[0]}\""
#query_anonymizedM = f"SELECT * FROM anonymizedM WHERE \"{valid_column_anonymizedM}\" = \"{data_anonymizedM[valid_column_anonymizedM].iloc[28334]}\""
query_anonymizedM = f"SELECT * FROM anonymizedM WHERE \"{valid_column_anonymizedM}\" = \"39\" OR \"{valid_column_anonymizedM}\" = \"{data_anonymizedM[valid_column_anonymizedM].iloc[28334]}\" OR \"{valid_column_anonymizedM}\" = \"{data_anonymizedM[valid_column_anonymizedM].iloc[29499]}\""


print("\nQuery sulla tabella originale:")
print(query_original)
print("\nQuery sulla tabella anonimizzata (Samarati):")
print(query_anonymizedS)
print("\nQuery sulla tabella anonimizzata (Mondrian):")
print(query_anonymizedM)

# Conteggio del tempo di accesso
time_original = measure_access_time(conn, query_original)
time_anonymizedS = measure_access_time(conn, query_anonymizedS)
time_anonymizedM = measure_access_time(conn, query_anonymizedM)

# Conteggio delle tuple ritornate
rows_original = count_rows(conn, query_original)
rows_anonymizedS = count_rows(conn, query_anonymizedS)
rows_anonymizedM = count_rows(conn, query_anonymizedM)

print(f"\nTempo medio di accesso (tabella originale): {time_original:.4f} secondi")
print(f"Tempo medio di accesso (tabella anonimizzata con Samarati): {time_anonymizedS:.4f} secondi")
print(f"Tempo medio di accesso (tabella anonimizzata con Mondrian): {time_anonymizedM:.4f} secondi\n")

print(f"Numero di righe ritornate (tabella originale): {rows_original}")
print(f"Numero di righe ritornate (tabella anonimizzata con Samarati): {rows_anonymizedS}")
print(f"Numero di righe ritornate (tabella anonimizzata con Mondrian): {rows_anonymizedM}")

conn.close()
