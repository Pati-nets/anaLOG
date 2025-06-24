import questionary # for pretty command-line selections

import Constants # (internal) strings representing the supported mining algorithms and complexity measures
from logcomplexity import LogComplexityMeasures
from modelcomplexity import ModelComplexityMeasures
from discovery import DiscoveryAlgorithms
from analysis import EventLogHandler, ModelHandler, PaperResults, RealLiveLogs

from pm4py.objects.log.importer.xes import importer as xes_importer


def example_selector(miner: str, measure: str):
    print() # add an empty line for better readability
    PaperResults.show_analysis_for(measure, miner)

def enter_paper_mode():
    miners = [questionary.Choice(title=str(miner), value=miner) for miner in DiscoveryAlgorithms.all_discovery_algorithms]
    miner = questionary.select("Which mining algorithm are you interested in?", choices=miners).ask()
    complexity_question = "Alright! Which model-complexity measure do you wish to analyze?"
    measures = []
    if type(miner) == DiscoveryAlgorithms.DirectlyFollowsGraphMiner:
        measures += [questionary.Choice(title=str(measure), value=measure) for measure in ModelComplexityMeasures.dfg_model_complexity_measures]
    else:
        measures += [questionary.Choice(title=str(measure), value=measure) for measure in ModelComplexityMeasures.all_model_complexity_measures]
    measure = questionary.select(complexity_question, choices=measures).ask()
    example_selector(miner, measure)

def enter_real_log_analysis_mode():
    # Ask for the event log
    file_question = "Please specify where the event log in XES format can be found."
    selected_filepath = questionary.path(file_question).ask()
    pm4py_log = xes_importer.apply(selected_filepath)
    log_info = "Your event log contains " + str(len(pm4py_log)) + " traces."
    print(log_info)
    threshold_question = "How many traces would you like to include in the analysis?"
    threshold_parseable = False
    chosen_threshold = str(len(pm4py_log))
    while not threshold_parseable:
        chosen_threshold = questionary.text(threshold_question).ask()
        if chosen_threshold.isdigit() and 0 < int(chosen_threshold) <= len(pm4py_log):
            threshold_parseable = True
        else:
            print("Sorry, I cannot interpret your input as a number between 0 (exclusive) and " + str(len(pm4py_log)) + " (inclusive).")
            print("Please try again.")
    threshold = int(chosen_threshold)
    # Ask for the mining algorithm
    miners = [questionary.Choice(title=str(miner), value=miner) for miner in DiscoveryAlgorithms.all_discovery_algorithms]
    miner_question = "Which mining algorithm should be used to find process models?"
    selected_miner = questionary.select(miner_question, choices=miners).ask()
    # Ask for the log complexity measures
    log_complexity_question = "Which log complexity measures would you like to investigate?\n Hint: Calculating the edit distance is very runtime-heavy for real event logs."
    log_measures = [questionary.Choice(title=str(measure), value=measure) for measure in LogComplexityMeasures.all_log_complexity_measures]
    selected_log_measures = questionary.checkbox(log_complexity_question, choices=log_measures).ask()
    if len(selected_log_measures) == 0:
        print("You chose to analyze no log complexity measures, so there's nothing to do for me.")
        return
    # Ask for the model complexity measures
    model_complexity_question = "Which model complexity measures would you like to investigate?"
    model_measures = []
    if type(selected_miner) == DiscoveryAlgorithms.DirectlyFollowsGraphMiner:
        model_measures += [questionary.Choice(title=str(measure), value=measure) for measure in ModelComplexityMeasures.dfg_model_complexity_measures]
    else:
        model_measures += [questionary.Choice(title=str(measure), value=measure) for measure in ModelComplexityMeasures.all_model_complexity_measures]
    selected_model_measures = questionary.checkbox(model_complexity_question, choices=model_measures).ask()
    if len(selected_model_measures) == 0:
        print("You chose to analyze no model complexity measures, so there's nothing to do for me.")
        return
    RealLiveLogs.investigate_real_life_log(pm4py_log, threshold, selected_log_measures, selected_model_measures, selected_miner)

def ask_for_event_log(message:str):
    log_spec_question = message + "Use the structure of the following example: [abcd, acbd, abce, acbe]\n"
    raw_log = questionary.text(log_spec_question).ask()
    raw_trace_list = raw_log.split(",")
    for i in range(len(raw_trace_list)):
        if raw_trace_list[i][0] == '[' or raw_trace_list[i][0] == ' ':
            raw_trace_list[i] = raw_trace_list[i][1:]
        if raw_trace_list[i][-1] == ']' or raw_trace_list[i][-1] == ' ':
            raw_trace_list[i] = raw_trace_list[i][:-1]
    return raw_trace_list

def enter_playground_mode():
    print("In this mode, you are asked to specify three event logs, L1, L2, L3, by entering them with your keyboard.")
    print("The event logs must fulfill L1 < L2, and L2 < L3 (L1 is a proper subset of L2, and L2 is a proper subset of L3).")
    log_spec_question = "Please specify the first event log you would like to investigate.\n"
    log1 = ask_for_event_log(log_spec_question)
    log_spec_question = "Please specify the multiset of traces that should be added to L1 to construct L2.\n"
    log2 = log1 + ask_for_event_log(log_spec_question)
    log_spec_question = "Please specify the multiset of traces that should be added to L2 to construct L3.\n"
    log3 = log2 + ask_for_event_log(log_spec_question)
    miner_question = "Next, please specify which discovery algorithm you would like to use to construct models."
    miners = [questionary.Choice(title=str(miner), value=miner) for miner in DiscoveryAlgorithms.all_discovery_algorithms]
    selected_miner = questionary.select(miner_question, choices=miners).ask()
    pm4py_logs = EventLogHandler.show_event_log_comparison([log1, log2, log3], LogComplexityMeasures.all_log_complexity_measures)
    model_complexity_measures = []
    if str(selected_miner) == str(DiscoveryAlgorithms.DirectlyFollowsGraphMiner()):
        model_complexity_measures += ModelComplexityMeasures.dfg_model_complexity_measures
    else:
        model_complexity_measures += ModelComplexityMeasures.all_model_complexity_measures
    ModelHandler.show_model_comparison(selected_miner, model_complexity_measures, pm4py_logs)
    print("This concludes the analysis of your event log. Hope this helped!")

if __name__ == "__main__":
    print("Welcome to anaLOG: The friendly log and model analyzer.")
    print("With this tool, you can reproduce the results of the paper ")
    print("\"Mind the Gap: A Formal Investigation of the Relationship Between Log and Model Complexity\"")
    print("or analyse your own event logs.")
    print()
    paper_mode = "Reproduce the results of the paper"
    real_log_analysis_mode = "Check what relations can be found in my event log"
    playground_mode = "Input and analyze an event log via keyboard"
    mode = questionary.select("What would you like to do?", choices=[paper_mode, real_log_analysis_mode, playground_mode]).ask()
    if mode == paper_mode:
        enter_paper_mode()
    elif mode == real_log_analysis_mode:
        enter_real_log_analysis_mode()
    elif mode == playground_mode:
        enter_playground_mode()
    else:
        raise Exception("Unexpected user-choice: " + mode)
