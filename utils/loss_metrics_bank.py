def generate_categorical_loss_metric_map(leaves_num, hierarchies):
    loss_metric_map = {attr: {} for attr in hierarchies.keys()}
    print('\nleaves_num:\n', leaves_num)
    for attr, vals in hierarchies.items():
        loss_metric_map[attr]['*'] = 1
        for v in vals:
            if v in leaves_num[attr].keys():
                loss_metric_map[attr][v] = (leaves_num[attr][v] - 1) / (leaves_num[attr]['*'] - 1)
            else: 
                loss_metric_map[attr][v] = 0
    return loss_metric_map

def categorical_loss_metric_bank(qi_columns, leaves_num, hierarchies, sup):
    if sup is None:
        sup = 0
    
    loss_metric_map = generate_categorical_loss_metric_map(leaves_num, hierarchies)
    print('\nloss_metric_map:\n', loss_metric_map)
    loss_metric = 0

    for attr in qi_columns:
        col = qi_columns[attr].tolist()
        # parametro di loss per un attributo è la Media di tutte i loss per tutte le tuple
        # parametro di loss per il dataset intero è la Somma dei loss di ogni attributo
        sum_attr_lm = 0
        for v in col:
            sum_attr_lm += loss_metric_map[attr].get(str(v), 0)
        loss_metric += (sum_attr_lm + sup) / (len(col) + sup) # media
    return loss_metric

def compute_numerical_loss_metric(column):
    loss = 0
    if not isinstance(column[0], int):  
        current_range = [int(i) for i in list(column[0].replace(' ', '').split('-'))]
        lowest, highest = current_range[0], current_range[1]
    else:  
        lowest, highest = column[0], column[0]

    for v in column:
        if not isinstance(v, int):
            current_range = [int(i) for i in list(v.replace(' ', '').split('-'))]
            loss += current_range[1] - current_range[0]
            lowest = min(lowest, current_range[0])
            highest = max(highest, current_range[1])
        else:
            lowest = min(lowest, v)
            highest = max(highest, v)
            
    max_range = highest - lowest
    return loss / (max_range * len(column))

def numerical_loss_metric_bank(qi_columns):
    loss_metric = 0
    for attr in qi_columns:
        col = qi_columns[attr].tolist()
        loss_metric += compute_numerical_loss_metric(col)
    return loss_metric
