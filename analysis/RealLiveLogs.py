from tabulate import tabulate # for pretty printing of tables
from tqdm import tqdm # for showing a progress bar

from modelcomplexity import ModelComplexityMeasures # (internal) for calculating model complexity scores


def calculate_log_complexity_scores(event_log, measures: list):
    complexity_scores = []
    for measure in measures:
        complexity_scores += [measure.calculate_for(event_log)]
    return complexity_scores

def calculate_model_complexity_scores(event_log, miner, measures: list):
    complexity_scores = []
    net, im, fm = miner.discover_for(event_log)
    for measure in measures:
        if type(measure) in [ModelComplexityMeasures.Depth, ModelComplexityMeasures.Diameter]:
            complexity_scores += [measure.calculate_for(net, im, fm)]
        else:
            complexity_scores += [measure.calculate_for(net)]
    return complexity_scores

def update_relation_table(relation_table, row_index, column_index, score1, score2):
    less = "\033[92m" + '<' + "\x1b[0m"
    leq = "\033[93m" + '≤' + "\x1b[0m"
    equal = "\033[94m" + '=' + "\x1b[0m"
    geq = "\033[93m" + '≥' + "\x1b[0m"
    greater = "\033[92m" + '>' + "\x1b[0m"
    norel = "\033[91m" + 'X' + "\x1b[0m"
    if score1 is not None and score2 is not None:
        # model complexity has strictly increased
        if score1 < score2:
            if relation_table[row_index][column_index] == '':
                relation_table[row_index][column_index] = less
            elif relation_table[row_index][column_index] == greater:
                relation_table[row_index][column_index] = norel
            elif relation_table[row_index][column_index] == equal:
                relation_table[row_index][column_index] = leq
        # model complexity stayed the same as before
        elif score1 == score2:
            if relation_table[row_index][column_index] == '':
                relation_table[row_index][column_index] = equal
            elif relation_table[row_index][column_index] == greater:
                relation_table[row_index][column_index] = geq
            elif relation_table[row_index][column_index] == less:
                relation_table[row_index][column_index] = leq
        # model complexity has strictly decreased
        else: # score1 > score2:
            if relation_table[row_index][column_index] == '':
                relation_table[row_index][column_index] = greater
            elif relation_table[row_index][column_index] == less:
                relation_table[row_index][column_index] = norel
            elif relation_table[row_index][column_index] == equal:
                relation_table[row_index][column_index] = geq


def investigate_real_life_log(event_log, log_threshold: int, log_measures: list, model_measures: list, mining_algorithm):
    log_column_names = [measure.abbreviation for measure in log_measures]
    model_column_names = [measure.abbreviation for measure in model_measures]
    # initialize the table for the relations found in the event log
    found_relations = [model_column_names]
    for i in range(len(log_column_names)):
        row = [log_column_names[i]]
        for j in range(len(model_column_names)):
            row += [''] # use empty string as initial placeholder
        found_relations += [row]
    previous_log_complexity_scores = calculate_log_complexity_scores(event_log[:1], log_measures)
    previous_model_complexity_scores = calculate_model_complexity_scores(event_log[:1], mining_algorithm, model_measures)
    try:
        for i in tqdm(range(1, log_threshold + 1), desc="calculating relations in the event log"):
            prefix_log = event_log[:i+1]
            log_complexity_scores = calculate_log_complexity_scores(prefix_log, log_measures)
            model_complexity_scores = calculate_model_complexity_scores(prefix_log, mining_algorithm, model_measures)
            # if some log complexity score increased, update the relation table
            for log_complexity_index in range(len(log_column_names)):
                if previous_log_complexity_scores[log_complexity_index] < log_complexity_scores[log_complexity_index]:
                    # go through all model complexity measures and add new information to the relation table
                    for model_complexity_index in range(len(model_column_names)):
                        pre = previous_model_complexity_scores[model_complexity_index]
                        now = model_complexity_scores[model_complexity_index]
                        update_relation_table(found_relations, log_complexity_index + 1, model_complexity_index + 1, pre, now)
            previous_log_complexity_scores = log_complexity_scores
            previous_model_complexity_scores = model_complexity_scores
        print("I found the following relations of model complexity in your event log if log complexity increases:")
        print(tabulate(found_relations, headers='firstrow', tablefmt='fancy_grid'))
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected!")
        print("Up until now, I found the following relaitons of model complexity in your event log if log complexity increases:")
        print(tabulate(found_relations, headers='firstrow', tablefmt='fancy_grid'))
    return found_relations
