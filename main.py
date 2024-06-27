import argparse
import pandas as pd
from algorithms.samarati_bank import samaratiB, LatticeB
from algorithms.mondrian_bank import mondrianB
from algorithms.samarati import samarati, Lattice
from algorithms.mondrian import mondrian
from utils.data_loader_bank import load_dataB, build_categorical_hierarchyB, build_range_hierarchyB, default_data_configB, display_tableB
from utils.data_loader import load_data, build_categorical_hierarchy, build_range_hierarchy, display_table, default_data_config

def main(config):
    if config['bank']:
        data = load_dataB(config=config)
        
        if config['samarati']:
            # Inizializzazione delle gerarchie e delle altezze per algoritmo Samarati
            hierarchies, heights, leaves_num = {}, {}, {}
            for attr, path in config['data']['hierarchies'].items():
                if config['data']['samarati_generalization_type'][attr] == 'categorical':
                    hierarchies[attr], heights[attr], leaves_num[attr] = build_categorical_hierarchyB(path)
                else:
                    hierarchies[attr], heights[attr], leaves_num[attr] = build_range_hierarchyB(data['table'][attr])
            
            print('\nhierarchies:\n', hierarchies)
            print('\nhierarchy heights:\n', heights)
            
            # Esecuzione dell'algoritmo Samarati per dataset Bank
            lattice = LatticeB(hierarchies=hierarchies, quasi_id=data['quasi_id'], heights=heights)
            anonymized_table, vector, sup, loss_metric = samaratiB(
                table=data['table'], lattice=lattice, k=config['k'], maxsup=config['maxsup'], leaves_num=leaves_num, sensitive=config['data']['sensitive']
            )

            print('\n====================')
            print('\n\nmetrica di loss:', loss_metric)
            print('\nvettore delle generalizzazioni:', vector)
            print('\nsoppressione massima:', sup)
            other_columns = [col for col in data['table'].columns if col not in data['quasi_id'] + [data['sensitive']]]
            anonymized_table = anonymized_table[data['quasi_id'] + [data['sensitive']]]
            anonymized_table = pd.concat([anonymized_table, data['table'][other_columns]], axis=1)
            display_tableB(anonymized_table)
            
            # Salvtaggio risultati
            anonymized_table.to_csv('results/samarati_bank.csv', index=False)
            data['table'].to_csv('results/originalB.csv', index=False)

        elif config['mondrian']:
            table = data['table']

            # Preprocessing dati categorici
            encoders = {}
            from utils.data_loader import preprocess_categorical_column, recover_categorical_mondrian
            for attr in data['quasi_id']:
                if config['data']['mondrian_generalization_type'][attr] == 'categorical':
                    table[attr], encoder = preprocess_categorical_column(table[attr].tolist())
                    encoders[attr] = encoder
            
            # Esecuzione dell'algoritmo Mondrian per dataset Bank
            anonymized_table, loss_metric = mondrianB(
                table=table, quasi_id=data['quasi_id'], k=config['k'], sensitive=config['data']['sensitive']
            )
            
            # Recupero dei dati categorici originali
            for attr in data['quasi_id']:
                if config['data']['mondrian_generalization_type'][attr] == 'categorical':
                    table[attr] = recover_categorical_mondrian(table[attr].tolist(), encoders[attr])

            print('\n\nmetrica di loss:', loss_metric)
            other_columns = [col for col in data['table'].columns if col not in data['quasi_id'] + [data['sensitive']]]
            anonymized_table = anonymized_table[data['quasi_id'] + [data['sensitive']]]
            anonymized_table = pd.concat([anonymized_table, data['table'][other_columns]], axis=1)
            display_tableB(anonymized_table)
            
            # Salvataggio risultati
            anonymized_table.to_csv('results/mondrian_bank.csv', index=False)
            data['table'].to_csv('results/originalB.csv', index=False)
    else:
        data = load_data(config=config)
        
        if config['samarati']:
            # Inizializzazione delle gerarchie e delle altezze per l'algoritmo Samarati
            hierarchies, heights, leaves_num = {}, {}, {}
            for attr, path in config['data']['hierarchies'].items():
                if config['data']['samarati_generalization_type'][attr] == 'categorical':
                    hierarchies[attr], heights[attr], leaves_num[attr] = build_categorical_hierarchy(path)
                else:
                    hierarchies[attr], heights[attr], leaves_num[attr] = build_range_hierarchy(data['table'][attr])
            
            print('\nhierarchies:\n', hierarchies)
            print('\nhierarchy heights:\n', heights)
            
            # Esecuzione dell'algoritmo Samarati per dataset Adult
            lattice = Lattice(hierarchies=hierarchies, quasi_id=data['quasi_id'], heights=heights)
            anonymized_table, vector, sup, loss_metric = samarati(
                table=data['table'], lattice=lattice, k=config['k'], maxsup=config['maxsup'],leaves_num=leaves_num, sensitive=config['data']['sensitive']
            )
            
            print('\n====================')
            print('\n\nmetrica di loss:', loss_metric)
            print('\nvettore delle generalizzazioni:', vector)
            print('\nsoppressione massima:', sup)
            other_columns = [col for col in data['table'].columns if col not in data['quasi_id'] + [data['sensitive']]]
            anonymized_table = anonymized_table[data['quasi_id'] + [data['sensitive']]]
            anonymized_table = pd.concat([anonymized_table, data['table'][other_columns]], axis=1)
            display_table(anonymized_table)
            
            # Salvtaggio risultati
            anonymized_table.to_csv('results/samarati.csv', index=False)
            data['table'].to_csv('results/original.csv', index=False)
            
        elif config['mondrian']:
            table = data['table']

            # Preprocessing dei dati categorici
            encoders = {}
            from utils.data_loader import preprocess_categorical_column, recover_categorical_mondrian
            for attr in data['quasi_id']:
                if config['data']['mondrian_generalization_type'][attr] == 'categorical':
                    table[attr], encoder = preprocess_categorical_column(table[attr].tolist())
                    encoders[attr] = encoder
            
            # Esecuzione algoritmo Mondrian per dataset Adult
            anonymized_table, loss_metric = mondrian(
                table=table, quasi_id=data['quasi_id'], k=config['k'], sensitive=config['data']['sensitive']
            )
            
            # Recupero dati categorici originali
            for attr in data['quasi_id']:
                if config['data']['mondrian_generalization_type'][attr] == 'categorical':
                    table[attr] = recover_categorical_mondrian(table[attr].tolist(), encoders[attr])

            print('\n\nmetrica di loss:', loss_metric)
            other_columns = [col for col in data['table'].columns if col not in data['quasi_id'] + [data['sensitive']]]
            anonymized_table = anonymized_table[data['quasi_id'] + [data['sensitive']]]
            anonymized_table = pd.concat([anonymized_table, data['table'][other_columns]], axis=1)
            display_table(anonymized_table)
            
            # Salvtaggio risultati
            anonymized_table.to_csv('results/mondrian.csv', index=False)
            data['table'].to_csv('results/original.csv', index=False)

    return loss_metric
    

if __name__ == '__main__':
    # Argomenti linea di comando
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", default=10, type=int, help="Valore di k per k-anonymity")
    parser.add_argument("--maxsup", default=20, type=int, help="Valore massimo di soppressione")
    parser.add_argument("--samarati", action='store_true', help="Seleziona l'algoritmo Samarati")
    parser.add_argument("--mondrian", action='store_true', help="Seleziona l'algoritmo Mondrian")
    parser.add_argument("--bank", action='store_true', help="Esegui l'algoritmo sul dataset Bank")

    # Pasring argomenti passati
    args = parser.parse_args()
    config = vars(args)

    if not (args.samarati or args.mondrian):
        parser.error("Devi specificare almeno un algoritmo. Usa --help per vedere le opzioni disponibili.")
    else:
        if config['bank']:
            # Carica i dati del dataset Bank
            config['data'] = default_data_configB
        else:
            # Carica i dati del dataset Adult
            config['data'] = default_data_config
        
        print('\nconfiguration:\n', config)
        main(config)