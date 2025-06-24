import pm4py # for exporting the event log as an .xes file
import pandas # for internal representations of event logs
from datetime import datetime # for including artificial timestamps
from tabulate import tabulate # for pretty printing tables

import Constants # (internal) for color-codes and event log specifier names
from logcomplexity import Complexity as LogComplexity # (internal) for generating event logs in pm4py format


def convert_language_to_dataframe(language):
    """
    Converts a list of words into a panda dataframe, adding a timestamp and a case identifier to each letter.
    :param language: a list of strings
    :return: a panda dataframe resembling an event log for the input language
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
    """
    Uses the builtin function by Maxim Vidgof to generate an event log in pm4py format.
    :param filename: the file-path to the .xes-file
    :return: a panda dataframe containing the information of the .xes-file
    """
    return LogComplexity.generate_pm4py_log(filename)

def print_language(language: list, name="L"):
    """
    Prints a list of strings as a multiset of traces, where each letter corresponds to an activity.
    For example, the language ["abcd", "abcd", "acbd"] gets printed as "L = [<a,b,c,d>^{2}, <a,c,b,d>^{1}]".
    :param language: the list of strings to be printed
    :param name: a name for the language
    :return: None
    """
    distinct_words = []
    for trace in language:
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
        trace_string += ">^{" + str(language.count(distinct_trace)) + "}"
        print(trace_string, end='')
        if i != len(distinct_words) - 1:
            print(", ", end='')
    print("]")

def handle_event_logs(event_logs: list, logname_prefix=""):
    """
    Handles a list of event logs by:
    1. Printing the event logs on the command line,
    2. Storing the event logs as .xes-files in the output folder,
    3. Converting them to EventLog format of pm4py.
    :param event_logs: a list of languages, for example ["abcd", "abcd", "acbd"]
    :param logname_prefix: a prefix that should appear in front of the L in the filename
    :return: a list of pm4py-EventLogs with the same data as in the languages passed
    """
    # print the event logs on the command line
    print("Consider the following event logs:")
    for i in range(len(event_logs)):
        log = event_logs[i]
        print_language(log, "L" + str(i + 1))
    # store the event logs as .xes-files in the output folder
    print("I will store them for you in the output folder, so you can look at them later.")
    print()
    print("I will also convert these event logs into pm4py format, so we can start the analysis.")
    filename_prefix = Constants.OUTPUT_PATH + logname_prefix + "L"
    for i in range(len(event_logs)):
        filename = filename_prefix + str(i + 1) + ".xes"
        pm4py.write_xes(convert_language_to_dataframe(event_logs[i]), filename)
    print("Done!")
    print()
    # import the .xes files to receive pm4py-typed event logs
    pm4py_logs = []
    for i in range(len(event_logs)):
        pm4py_logs += [import_pm4py_log(filename_prefix + str(i + 1) + ".xes")]
    return pm4py_logs

def calculate_log_complexity_scores(event_log, measures: list):
    """
    Calculates the complexity scores of an event log.
    :param event_log: the event log whose complexity scores we want to calculate
    :param measures: the measures used to calculate the complexity scores
    :return: a list of complexity scores, where the i-th entry is the score received by evaluating measure[i]
    """
    complexity_scores = []
    for measure in measures:
        complexity_scores += [measure.calculate_for(event_log)]
    return complexity_scores

def highlight_strictly_increasing_scores(complexity_scores: list):
    """
    Highlights the columns of the passed tables in green if the scores are strictly increasing, and red otherwise.
    :param complexity_scores: A list of complexity-score lists
    :return: the passed list, where all entries are strings and either highlighted in green or in red
    """
    # do nothing if there are 0 or 1 list(s) of complexity scores
    if len(complexity_scores) < 2:
        return complexity_scores
    # go through all columns and check if the scores are strictly increasing
    max_column_index = min([len(scores) for scores in complexity_scores])
    for i in range(max_column_index):
        strictly_increasing = True
        incomparable = False
        for j in range(1, len(complexity_scores)):
            # check if the scores are all floats or ints (happens if a score is None or NaN)
            if type(complexity_scores[j-1][i]) not in [int, float] or type(complexity_scores[j][i]) not in [int, float]:
                incomparable = True
                break
            # check if the scores are not strictly increasing
            if complexity_scores[j-1][i] >= complexity_scores[j][i]:
                strictly_increasing = False
                break
        # color the columns in green if all conditions are met, or red otherwise
        for j in range(len(complexity_scores)):
            if strictly_increasing and not incomparable:
                complexity_scores[j][i] = Constants.SUCCESS_COLOR + str(complexity_scores[j][i]) + Constants.RESET_COLOR
            else:
                complexity_scores[j][i] = Constants.FAILURE_COLOR + str(complexity_scores[j][i]) + Constants.RESET_COLOR
    return complexity_scores

def print_log_complexity_scores(pm4py_logs: list, measures: list, highlight_increasing=False):
    """
    Prints the complexity scores of the passed event logs, calculated by the passed measures, and prints the resulting
    table on command line.
    :param pm4py_logs: a list of event logs in pm4py-format
    :param measures: a list of measures with which the complexity scores should be calculated
    :param highlight_increasing: a boolean indicating whether strictly increasing columns should be highlighted
    :return: None
    """
    # collect the complexity scores
    complexity_scores = []
    for event_log in pm4py_logs:
        complexity_scores += [calculate_log_complexity_scores(event_log, measures)]
    # color the entries if desired
    if highlight_increasing:
        complexity_scores = highlight_strictly_increasing_scores(complexity_scores)
    # add descriptors for rows
    header = [""]
    for measure in measures:
        header += [measure.abbreviation]
    # add descriptors for columns
    for i in range(len(complexity_scores)):
        complexity_scores[i] = ["log " + str(i+1)] + complexity_scores[i]
    complexity_scores = [header] + complexity_scores
    # print the table in a pretty way
    print(tabulate(complexity_scores, headers='firstrow', tablefmt='fancy_grid'))

def show_event_log_comparison(event_logs: list, measures: list, logname_prefix=""):
    """
    Takes a list of languages, converts them into pm4py event logs, and prints their complexity scores in a pretty
    table on command line.
    :param event_logs: a list of languages, where a language is a list of strings
    :param measures: a list of complexity measures for event logs, whose scores should be calculated
    :param logname_prefix: a prefix for the stored .xes-files
    :return: the list of languages, in form of pm4py-EventLogs
    """
    pm4py_logs = handle_event_logs(event_logs, logname_prefix)
    print("Next, let me calculate the log complexity scores of these event logs.")
    print_log_complexity_scores(pm4py_logs, measures,True)
    return pm4py_logs