import pm4py # for exporting pictures of Petri nets
from tabulate import tabulate # for pretty printing tables

import Constants # (internal) for the path of the output folder and color codes on command line
from discovery import DiscoveryAlgorithms # (internal) for executing discovery algorithms
from modelcomplexity import ModelComplexityMeasures # (internal) for calculating the complexity of models

def calculate_models(miner, pm4py_logs, filename_prefix="", silent=False):
    """
    Calculates the models for the passed event logs by using the specified mining algorithm
    :param miner: the mining algorithm that should be used to find models for the event logs
    :param pm4py_logs: the event logs for which models should be calculated
    :param filename_prefix: a prefix for the filename of the resulting picture of the model
    :param silent: a boolean indicating whether only the tables should be printed, or also explanations
    :return: a list of triples (net, im, fm), where net is the mined model, im its initial marking, and fm its final marking
    """
    if not silent:
        print("I will now use the " + str(miner).lower() + " to find models for these event logs.")
    models = []
    for i in range(len(pm4py_logs)):
        (net, im, fm) = miner.discover_for(pm4py_logs[i])
        models += [(net, im, fm)]
        # store the pictures of the mining results in the output folder
        if type(miner) == DiscoveryAlgorithms.DirectlyFollowsGraphMiner:
            net.visualize(Constants.OUTPUT_PATH + filename_prefix + "DFG" + str(i + 1))
        else:
            pm4py.save_vis_petri_net(net, im, fm, file_path=Constants.OUTPUT_PATH+filename_prefix+"M" + str(i) + ".png")
    if not silent:
        print("Done!")
    return models

def calculate_model_complexity_scores(model, measures: list):
    """
    Calculates the complexity scores of the passed model by using the specified complexity measures.
    :param model: the model whose complexity scores should be calculated
    :param measures: the measures that should be used to calculate the complexity scores
    :return: the list of complexity scores for the model, where the i-th entry is the score received by evaluating measure[i]
    """
    complexity_scores = []
    net, im, fm = model
    for measure in measures:
        if type(measure) in [ModelComplexityMeasures.Depth, ModelComplexityMeasures.Diameter]:
            complexity_scores += [measure.calculate_for(net, im, fm)]
        else:
            complexity_scores += [measure.calculate_for(net)]
    return complexity_scores

def highlight_norel_scores(complexity_scores: list):
    """
    Takes a matrix of complexity scores and highlights all columns in green where complexity increases and decreases.
    All other columns are colored in red.
    :param complexity_scores: a matrix of complexity scores
    :return: the passed matrix, where all entries are strings and either highlighted in green or in red
    """
    # do nothing if there are 0 or 1 list(s) of complexity scores
    if len(complexity_scores) < 2:
        return complexity_scores
    # go through all columns and check if the scores can increase and decrease
    max_column_index = min([len(scores) for scores in complexity_scores])
    for i in range(max_column_index):
        strictly_decreasing = False
        strictly_increasing = False
        incomparable = False
        for j in range(1, len(complexity_scores)):
            # check if the scores are all floats or ints (happens if a score is None or NaN)
            if type(complexity_scores[j-1][i]) not in [int, float] or type(complexity_scores[j][i]) not in [int, float]:
                incomparable = True
                break
            # check if the last two scores are strictly increasing
            if complexity_scores[j-1][i] < complexity_scores[j][i]:
                strictly_increasing = True
            # check if the last two scores are strictly decreasing
            if complexity_scores[j-1][i] > complexity_scores[j][i]:
                strictly_decreasing = True
        # color the columns in green if all conditions are met, or red otherwise
        for j in range(len(complexity_scores)):
            if strictly_increasing and strictly_decreasing and not incomparable:
                complexity_scores[j][i] = Constants.SUCCESS_COLOR + str(complexity_scores[j][i]) + Constants.RESET_COLOR
            else:
                complexity_scores[j][i] = Constants.FAILURE_COLOR + str(complexity_scores[j][i]) + Constants.RESET_COLOR
    return complexity_scores

def print_model_complexity_scores(models: list, measures: list, highlight_norel=False):
    """
    Prints the complexity scores of the passed models, where the passed complexity measures are used to calculate the scores.
    :param models: a list of triples (net, im, fm), where net is a discovered model, im its initial and fm its final marking
    :param measures: a list of complexity measures for models
    :param highlight_norel: a boolean indicating whether columns should be colored in green when complexity increases and decreases
    :return: None
    """
    # collect the complexity scores
    complexity_scores = []
    for model in models:
        complexity_scores += [calculate_model_complexity_scores(model, measures)]
    # color the entries if desired
    if highlight_norel:
        complexity_scores = highlight_norel_scores(complexity_scores)
    # add descriptors for rows
    header = [""]
    for measure in measures:
        header += [measure.abbreviation]
    # add descriptors for columns
    for i in range(len(complexity_scores)):
        complexity_scores[i] = ["model " + str(i+1)] + complexity_scores[i]
    complexity_scores = [header] + complexity_scores
    # print the table in a pretty way
    print(tabulate(complexity_scores, headers='firstrow', tablefmt='fancy_grid'))

def show_model_comparison(miner, measures: list, pm4py_logs, filename_prefix="", colored=True, just_table=False):
    """
    Shows the complexity of the models found by the passed miner, for the passed event logs.
    To calculate complexity scores, this method uses the passed measures.
    :param miner: the process discovery algorithm that should be used to discover models
    :param measures: the list of measures that should be used to calculate the complexity scoers of models
    :param pm4py_logs: the list of event logs for which models should be found
    :param filename_prefix: a prefix for the name of the file storing the found models
    :param colored: a boolean indicating whether the resulting table should be colored if scores increase and decrease
    :param just_table: a boolean indicating whether explanatory text should be shown or not
    :return: a list of the models found by the specified mining algorithm for the event logs
    """
    models = calculate_models(miner, pm4py_logs, filename_prefix, just_table)
    if not just_table:
        print("Next, let me calculate the model complexity scores of these models.")
    print_model_complexity_scores(models, measures, colored)
    return models