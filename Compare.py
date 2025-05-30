import pandas # for converting lists of strings into pm4py-like event logs
from datetime import datetime # for creating timestamps for pm4py-like event logs
from tabulate import tabulate # for pretty printing of tables

from logcomplexity import Complexity as LogComplexity # (internal) for calculating complexity scores of event logs
from logcomplexity import MoreLogComplexity # (internal) providing more event log complexity measures
from modelcomplexity import ModelComplexity # (internal) for calculating complexity scores of process models
import Constants # (internal) for picking attributes in event logs and printing in color


def convert_language_to_dataframe(language):
    """
    Converts a language into a DataFrame that can be interpreted as an event log.
    This method interprets every letter as a distinct event in the event log.
    As timestamps, it takes the time of event creation with this program.
    The names of the cases are 1, 2, 3, ... respectively.
    :param language: A list of strings, where each letter corresponds to an event in the event log
    :return: A pandas DataFrame object where each word is a trace in an event log and every letter is an activity of a trace
    """
    data = []
    current_case = 1
    for word in language:
        for symbol in word:
            data += [(symbol, datetime.now(), str(current_case))]
        current_case += 1
    column_names = [Constants.activity_specifier, Constants.timestamp_specifier, Constants.case_specifier]
    result = pandas.DataFrame(data, columns=column_names)
    return result

def import_pm4py_log(filename: str):
    return LogComplexity.generate_pm4py_log(filename)

def print_log_complexities(event_logs: list, colored=False, decimals=4):
    plain_logs = [LogComplexity.generate_log(L) for L in event_logs]
    row_names = ["log " + str(i + 1) for i in range(len(event_logs))]
    column_names = ["", "mag", "var", "supp", "TL-avg", "TL-max", "LOD"]
    column_names += ["t-comp", "LZ", "DT-#", "DT-%", "struct", "affinity", "dev-rand"]
    column_names += ["avg-dist", "var-e", "nvar-e", "seq-e", "nseq-e"]
    data = [column_names]
    for i in range(len(event_logs)):
        complexity = [row_names[i]]
        complexity += [LogComplexity.measure_magnitude(plain_logs[i], quiet=True)]
        complexity += [LogComplexity.measure_variety(event_logs[i], quiet=True)]
        support = LogComplexity.measure_support(event_logs[i], quiet=True)
        complexity += [support]
        trace_length = LogComplexity.measure_trace_length(event_logs[i], quiet=True)
        complexity += [round(trace_length["avg"], decimals)]
        complexity += [trace_length["max"]]
        complexity += [MoreLogComplexity.measure_number_of_transition_paths(event_logs[i])]
        complexity += [round(MoreLogComplexity.measure_number_of_ties(event_logs[i]), decimals)]
        complexity += [LogComplexity.measure_lempel_ziv(plain_logs[i], quiet=True)]
        distinct_trace_percentage = LogComplexity.measure_distinct_traces(event_logs[i], quiet=True) / 100
        complexity += [round(distinct_trace_percentage * support)]
        complexity += [round(distinct_trace_percentage, decimals)]
        complexity += [round(LogComplexity.measure_level_of_detail(event_logs[i], quiet=True), decimals)] # in the program, LOD is struct and struct is weird
        complexity += [round(LogComplexity.measure_affinity(event_logs[i], quiet=True), decimals)]
        deviation_from_random = LogComplexity.measure_deviation_from_random(plain_logs[i], event_logs[i], quiet=True)
        if deviation_from_random is None:
            complexity += [deviation_from_random]
        else:
            complexity += [round(deviation_from_random, decimals)]
        complexity += [round(MoreLogComplexity.measure_average_edit_distance(event_logs[i]), decimals)]
        epa = LogComplexity.build_graph(plain_logs[i])
        variant_entropy = LogComplexity.graph_complexity(epa)
        complexity += [round(variant_entropy[0], decimals)]
        complexity += [round(variant_entropy[1], decimals)]
        sequence_entropy = LogComplexity.log_complexity(epa)
        complexity += [round(sequence_entropy[0], decimals)]
        complexity += [round(sequence_entropy[1], decimals)]
        data += [complexity]
    # post-processing for coloring
    if colored:
        for i in range(1, len(column_names)):
            strictly_increasing = True
            incomparable = False
            for j in range(2, len(data)):
                if data[j][i] is None or data[j-1][i] is None or (type(data[j][i]) is not float and type(data[j][i]) is not int):
                    incomparable = True
                    break
                if data[j][i] <= data[j-1][i]:
                    strictly_increasing = False
                    break
            for j in range(1, len(data)):
                if not incomparable:
                    if strictly_increasing:
                        data[j][i] = Constants.SUCCESS_COLOR + str(data[j][i]) + Constants.RESET_COLOR
                    else:
                        data[j][i] = Constants.FAILURE_COLOR + str(data[j][i]) + Constants.RESET_COLOR
    print(tabulate(data, headers='firstrow', tablefmt='fancy_grid'))

def print_model_complexities(models: list, colored=False, decimals=4):
    row_names = ["model " + str(i + 1) for i in range(len(models))]
    column_names = ["", "size", "mismatch", "conn-het", "cross-conn", "token-split", "CFC", "sep", "acd", "mcd"]
    column_names += ["seq", "depth", "diam", "cyc", "CNC", "dens", "dup", "empty"]
    data = [column_names]
    for i in range(len(models)):
        complexity = [row_names[i]]
        complexity += [ModelComplexity.measure_size(models[i].net)]
        complexity += [ModelComplexity.measure_connector_mismatch(models[i].net)]
        complexity += [ModelComplexity.measure_connector_heterogeneity(models[i].net)]
        complexity += [round(ModelComplexity.measure_cross_connectivity(models[i].net), decimals)]
        complexity += [ModelComplexity.measure_token_split(models[i].net)]
        complexity += [ModelComplexity.measure_control_flow_complexity(models[i].net)]
        complexity += [round(ModelComplexity.measure_separability(models[i].net), decimals)]
        avg_connector_degree = ModelComplexity.measure_average_connector_degree(models[i].net)
        if avg_connector_degree is not None:
            complexity += [round(ModelComplexity.measure_average_connector_degree(models[i].net), decimals)]
        else:
            complexity += [avg_connector_degree]
        complexity += [ModelComplexity.measure_maximum_connector_degree(models[i].net)]
        complexity += [round(ModelComplexity.measure_sequentiality(models[i].net), decimals)]
        complexity += [ModelComplexity.measure_depth(models[i].net, models[i].initial_marking, models[i].final_marking)]
        complexity += [ModelComplexity.measure_diameter(models[i].net, models[i].initial_marking, models[i].final_marking)]
        complexity += [round(ModelComplexity.measure_cyclicity(models[i].net), decimals)]
        complexity += [round(ModelComplexity.measure_coefficient_of_network_connectivity(models[i].net), decimals)]
        complexity += [round(ModelComplexity.measure_density(models[i].net), decimals)]
        complexity += [ModelComplexity.measure_number_of_duplicate_tasks(models[i].net)]
        complexity += [ModelComplexity.measure_empty_sequence_flows(models[i].net)]
        data += [complexity]
    # post-processing for coloring
    if colored and len(data) == 4:
        for i in range(1, len(column_names)):
            if type(data[1][i]) in [float, int] and type(data[2][i]) in [float, int] and type(data[3][i]) in [float, int]:
                color = Constants.FAILURE_COLOR
                if data[1][i] < data[2][i] and data[2][i] > data[3][i]:
                    color = Constants.SUCCESS_COLOR
                if data[1][i] > data[2][i] and data[2][i] < data[3][i]:
                    color = Constants.SUCCESS_COLOR
                data[1][i] = color + str(data[1][i]) + Constants.RESET_COLOR
                data[2][i] = color + str(data[2][i]) + Constants.RESET_COLOR
                data[3][i] = color + str(data[3][i]) + Constants.RESET_COLOR
    print(tabulate(data, headers='firstrow', tablefmt='fancy_grid'))

def print_graph_complexities(graphs: list, colored=False, decimals=4):
    row_names = ["graph " + str(i + 1) for i in range(len(graphs))]
    column_names = ["", "size", "mismatch", "cross-conn", "CFC", "sep", "acd", "mcd"]
    column_names += ["seq", "depth", "diam", "cyc", "CNC", "dens"]
    data = [column_names]
    for i in range(len(graphs)):
        complexity = [row_names[i]]
        complexity += [graphs[i].size()]
        complexity += [graphs[i].mismatch()]
        complexity += [round(graphs[i].cross_connectivity(), decimals)]
        complexity += [graphs[i].control_flow_complexity()]
        complexity += [round(graphs[i].separability(), decimals)]
        mcd = graphs[i].average_connector_degree()
        if mcd is not None:
            complexity += [round(mcd, decimals)]
        else:
            complexity += [mcd]
        complexity += [graphs[i].maximum_connector_degree()]
        complexity += [round(graphs[i].sequentiality(), decimals)]
        complexity += [graphs[i].depth()]
        complexity += [graphs[i].diameter()]
        complexity += [round(graphs[i].cyclicity(), decimals)]
        complexity += [round(graphs[i].coefficient_of_network_connectivity(), decimals)]
        complexity += [round(graphs[i].density(), decimals)]
        data += [complexity]
    # post-processing for coloring
    if colored and len(data) == 4:
        for i in range(1, len(column_names)):
            if type(data[1][i]) in [float, int] and type(data[2][i]) in [float, int] and type(data[3][i]) in [float, int]:
                color = Constants.FAILURE_COLOR
                if data[1][i] < data[2][i] and data[2][i] > data[3][i]:
                    color = Constants.SUCCESS_COLOR
                if data[1][i] > data[2][i] and data[2][i] < data[3][i]:
                    color = Constants.SUCCESS_COLOR
                data[1][i] = color + str(data[1][i]) + Constants.RESET_COLOR
                data[2][i] = color + str(data[2][i]) + Constants.RESET_COLOR
                data[3][i] = color + str(data[3][i]) + Constants.RESET_COLOR
    print(tabulate(data, headers='firstrow', tablefmt='fancy_grid'))

def print_event_log(simple_log: list, name="L"):
    distinct_words = []
    for trace in simple_log:
        if trace not in distinct_words:
            distinct_words += [trace]
    print(name + " = [", end='')
    for i in range(len(distinct_words)):
        distinct_trace = distinct_words[i]
        trace_string = "<"
        for j in range(len(distinct_trace)):
            trace_string += distinct_trace[j]
            if j != len(distinct_trace) - 1:
                trace_string += ","
        trace_string += ">^{" + str(simple_log.count(distinct_trace)) + "}"
        print(trace_string, end='')
        if i != len(distinct_words) - 1:
            print(", ", end='')
    print("]")
