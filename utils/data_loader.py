import pandas as pd
import numpy as np
from sklearn import preprocessing

def display_table(table):
    print('\n====================')
    print('Tabella:\n', table)
    print('====================\n')

# Configurazione per il database Bank
default_data_config = {
    'path': 'data/adult.data', 
    # QI for samarati
    'samarati_quasi_id': ['age', 'gender', 'race', 'marital_status'],
    # QI for mondrian
    'mondrian_quasi_id': ['age', 'education_num'],
    # 'mondrian_quasi_id': ['age', 'gender', 'education_num'],
    'sensitive': 'occupation',
    'columns': ['age', 'work_class', 'final_weight', 'education', 'education_num', 
                'marital_status', 'occupation', 'relationship', 'race', 'gender', 
                'capital_gain', 'capital_loss', 'hours_per_week', 
                'native_country', 'class'],
    'samarati_generalization_type': {
        'age': 'range',
        'gender': 'categorical',
        'race': 'categorical',
        'marital_status': 'categorical',
    },
    'hierarchies': {
        'age': None,
        'gender': 'data/adult_gender.txt',
        'race': 'data/adult_race.txt',
        'marital_status': 'data/adult_marital_status.txt',
    },
    'mondrian_generalization_type': {
        'age': 'numerical',
        # 'gender': 'categorical',
        'education_num': 'numerical',
    },
}

def load_data(config):
    data_config = config['data']
    table = pd.read_csv(data_config['path'], header=None, skipinitialspace=True)

    # Eliminazione delle tuple contenenti '?'
    print('\nrow count before sanitizing:', table.shape[0])
    table = table[~table.isin(['?']).any(axis=1)]
    print('row count sanitized:', table.shape[0])
    
    # Sampling 5000 tuple rappresentative
    #table = table.sample(n=5000, replace=False, random_state=42)

    table.columns = data_config['columns']

    if config['samarati']:
        quasi_id = data_config['samarati_quasi_id']
    else:
        quasi_id = data_config['mondrian_quasi_id']

    data = {'table': table, 'quasi_id': quasi_id, 'sensitive': data_config['sensitive']}
    #print('data:', data)
    return data


def build_categorical_hierarchy(path):
    hierarchy = pd.read_csv(path, header=None)
    hierarchy.columns = ['child', 'parent']
    children = hierarchy['child'].tolist()
    parents = hierarchy['parent'].unique().tolist()
    # Creazione albero gerarchico
    tree = {k: hierarchy.loc[hierarchy['parent'] == k]['child'].tolist() for k in parents}
    # Conteggio delle foglie di ciasun sottoalbero (per loss metric)
    leaves_num = {k: subtree_leaves(tree, k) for k in parents}
    # Altezza dell'albero (per lattice)
    height = get_tree_height(tree)
    # Creazione dell'albero inverso (children to parent)
    inversed_tree = {}
    for index, row in hierarchy.iterrows():
        inversed_tree[row['child']] = row['parent']
    return inversed_tree, height, leaves_num


# Costruzione gerarchie con i range di generalizzazione
def build_range_hierarchy(attribute_column, ranges=[5, 10, 20]):
    height = len(ranges) + 1
    column = list(attribute_column)
    inversed_tree = {}
    leaves_num = {}
    visited = []

    for i, r in enumerate(ranges):
        if i == 0:
            pairs = []
            for num in column:
                if num not in visited:
                    pair = (r * int(num / r), r * (int(num / r) + 1))
                    pairs.append(pair)
                    inversed_tree[str(num)] = str(pair)

                    visited.append(num)
                    if str(pair) not in leaves_num.keys():
                        leaves_num[str(pair)] = 1
                    else:
                        leaves_num[str(pair)] += 1
        else:
            new_pairs = []
            for pair in pairs:
                if str(pair) not in visited:
                    p = (r * int(pair[0] / r), r * (int(pair[0] / r) + 1))
                    new_pairs.append(p)
                    inversed_tree[str(pair)] = str(p)
                    
                    visited.append(str(pair))
                    if str(p) not in leaves_num.keys():
                        leaves_num[str(p)] = leaves_num[str(pair)]
                    else:
                        leaves_num[str(p)] += leaves_num[str(pair)]
            pairs = new_pairs

    for pair in pairs:
        if str(pair) not in visited:
            inversed_tree[str(pair)] = '*'

            visited.append(str(pair))
            if '*' not in leaves_num.keys():
                leaves_num['*'] = leaves_num[str(pair)]
            else:
                leaves_num['*'] += leaves_num[str(pair)]

    return inversed_tree, height, leaves_num


def get_tree_height(tree, root='*'):
    height = 0
    pointer = root
    while pointer in list(tree.keys()):
        height += 1
        pointer = tree[pointer][0]
    return height


def subtree_leaves(tree, root='*'):
    if root not in tree.keys():
        return 1
    children = tree[root]
    leaves_num = sum([subtree_leaves(tree, r) for r in children])
    return leaves_num


# Codificatore per i valori categorici (Mondrian)
def preprocess_categorical_column(org_col):
    encoder = preprocessing.LabelEncoder()
    encoder.fit(org_col)
    return encoder.transform(org_col), encoder


# Decoficatore valori categorici (Mondrian)
def recover_categorical_mondrian(col, encoder):
    return encoder.inverse_transform(col)