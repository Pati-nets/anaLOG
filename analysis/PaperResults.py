import Constants
from analysis import EventLogHandler, ModelHandler
from logcomplexity.LogComplexityMeasures import all_log_complexity_measures
from modelcomplexity import ModelComplexityMeasures
from logcomplexity import LogComplexityMeasures
from discovery import DiscoveryAlgorithms
from modelcomplexity.ModelComplexityMeasures import all_model_complexity_measures


def show_measure_pair_in_leq(miner, measure, log_tuples_eq: list, log_tuples_less: list, direction="increas"):
    all_log_measures = LogComplexityMeasures.all_log_complexity_measures
    if str(miner) == str(DiscoveryAlgorithms.DirectlyFollowsGraphMiner()):
        all_model_measures = ModelComplexityMeasures.dfg_model_complexity_measures
    else:
        all_model_measures = ModelComplexityMeasures.all_model_complexity_measures
    print("Let me now show you that an increase in log complexity can mean " + str(measure).lower() + " " + direction + "es or stays unchanged.")
    print("I will start with the former.")
    filename = str(miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-" + direction + "e-possible-"
    pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_less[0], all_log_measures, filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename, False)
    print("In this table, you can see that the " + str(measure).lower() + " score of the flower model " + direction + "d.")
    print("Thus, an increase in log-complexity can mean that the " + str(measure).lower() + " score " + direction + "es.")
    for i in range(1, len(log_tuples_less)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = str(miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-" + direction + "e-possible-" + str(i+1) + "-"
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_less[i], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename, False)
        print("Thus also an increase in the newly green colored log-complexity measures can mean that the " + str(measure).lower() + " score " + direction + "es.")
    print()
    print("Now, let me show to you that it is also possible that the " + str(measure).lower() + " score stays unchanged.")
    filename = str(miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-no-change-possible-"
    pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_eq[0], all_log_measures, filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename, False)
    print("In this table, you can see that the " + str(measure).lower() + " score of the " + str(miner).lower() + " result did not change.")
    print("Thus, an increase in log-complexity can mean that the " + str(measure).lower() + " score stays unchanged.")
    for i in range(1, len(log_tuples_eq)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = str(miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-no-change-possible-" + str(i+1) + "-"
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_eq[i], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename, False)
        print("Thus also an increase in the newly green colored log-complexity measures can mean that the " + str(measure).lower() + " score stays unchanged.")

def print_counter_example(measure, miner, log_triples: list):
    all_log_measures = LogComplexityMeasures.all_log_complexity_measures
    if type(miner) == DiscoveryAlgorithms.DirectlyFollowsGraphMiner:
        all_model_measures = ModelComplexityMeasures.dfg_model_complexity_measures
    else:
        all_model_measures = ModelComplexityMeasures.all_model_complexity_measures
    print("Let me show you which log-complexity measures have no influence on the " + str(measure).lower() + " of the " + str(miner).lower() + ".")
    filename = str(miner).lower().replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-"
    pm4py_logs = EventLogHandler.show_event_log_comparison(log_triples[0], all_log_complexity_measures, filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename)
    print("Again, I highlighted the complexity measures C in green where we can see an increase and a decrease when log-complexity increases.")
    print("Since " + str(measure).lower() + " is one of these measures, we cannot predict what will happen to the " + str(measure).lower() + " of the " + str(miner).lower() + " when log-complexity increases.")
    for i in range(1,len(log_triples)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = str(miner).lower().replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-" + str(i+1) + "-"
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_triples[i], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(miner, all_model_measures, pm4py_logs, filename)
        print("This shows that also the newly green colored log-complexity measures cannot predict the " + str(measure).lower() + " of the " + str(miner).lower() + " when log-complexity increases.")


################# Flower Model Analysis #################
def flower_model_leq_entries(measure):
    print("First, observe that var(L1) < var(L2) always implies an increase in " + str(measure).lower() + ".")
    print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    print()
    log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
    log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabc"]
    log_tuples_eq = [[log1, log2]]
    log1 = ["a", "a", "abcd", "abcd", "abcd"]
    log2 = log1 + ["eabcd"]
    log_tuples_less = [[log1, log2]]
    show_measure_pair_in_leq(DiscoveryAlgorithms.FlowerModelMiner(), measure, log_tuples_eq, log_tuples_less)

def flower_model_eq_entries(measure):
    print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
    print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")

def show_flower_model_analysis(measure):
    print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their flower models.")
    if type(measure) in [ModelComplexityMeasures.Size, ModelComplexityMeasures.CrossConnectivity,
                         ModelComplexityMeasures.ControlFlowComplexity, ModelComplexityMeasures.Separability,
                         ModelComplexityMeasures.AverageConnectorDegree, ModelComplexityMeasures.MaximumConnectorDegree,
                         ModelComplexityMeasures.Sequentiality, ModelComplexityMeasures.Cyclicity,
                         ModelComplexityMeasures.CoefficientOfNetworkConnectivity]:
        flower_model_leq_entries(measure)
    else:
        flower_model_eq_entries(measure)
    print("This concludes the analysis of the " + str(measure).lower() + " measure.")
#########################################################

################### Trace Net Analysis ###################
def trace_net_most_leq_entries(measure):
    log1 = ["abc", "abcd", "abcd", "abcde", "abcde", "deab"]
    log2 = log1 + ["abcde", "abcde", "abcde", "deab", "deab", "deab"]
    log_tuples_eq = [[log1, log2]]
    log1 = ["abc", "abcd", "abcd", "abcde", "abcde", "deab"]
    log2 = log1 + ["abcdef", "aabcdef", "abcdeab"]
    log_tuples_less = [[log1, log2]]
    show_measure_pair_in_leq(DiscoveryAlgorithms.TraceNetMiner(), measure, log_tuples_eq, log_tuples_less)

def trace_net_eq_entries(measure):
    print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
    print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
    print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")

def show_trace_net_analysis(measure):
    tracenet_miner = DiscoveryAlgorithms.TraceNetMiner()
    if type(measure) in [ModelComplexityMeasures.Size, ModelComplexityMeasures.ControlFlowComplexity,
                         ModelComplexityMeasures.AverageConnectorDegree, ModelComplexityMeasures.MaximumConnectorDegree]:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
        print("First, observe that var(L1) < var(L2), TL-max(L1) < TL-max(L2), LOD(L1) < LOD(L2), t-comp(L1) < t-comp(L2)")
        print("DT-#(L1) < DT-#(L2), DT-%(L1) < DT-%(L2), var-e(L1) < var-2(L2), nvar-e(L1) < nvar-e(L2) all imply an")
        print("increase in the " + str(measure).lower() + " score from M1 to M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        trace_net_most_leq_entries(measure)
    elif type(measure) in [ModelComplexityMeasures.ConnectorMismatch, ModelComplexityMeasures.ConnectorHeterogeneity,
                           ModelComplexityMeasures.TokenSplit, ModelComplexityMeasures.Depth,
                           ModelComplexityMeasures.Separability, ModelComplexityMeasures.Cyclicity,
                           ModelComplexityMeasures.NumberOfEmptySequenceFlows]:
        trace_net_eq_entries(measure)
    elif type(measure) == ModelComplexityMeasures.Diameter:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
        print("First, observe that TL-max(L1) < TL-max(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdab"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdabc"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(tracenet_miner, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Density:
        print("First, observe that an increase in TL-max or t-comp means a decrease in density.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print("Let me now show you that an increase in log complexity can mean density decreases or stays unchanged.")
        print("I will start with the former.")
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdabc"]
        log_tuples_greater = [[log1, log2]]
        filename = str(tracenet_miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-decrease-possible-"
        all_log_measures = LogComplexityMeasures.all_log_complexity_measures
        all_model_measures = ModelComplexityMeasures.all_model_complexity_measures
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_greater[0], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(tracenet_miner, all_model_measures, pm4py_logs, filename, False)
        print("In this table, you can see that the " + str(measure).lower() + " score of the trace net decreased.")
        print("Thus, an increase in log-complexity can mean that the " + str(measure).lower() + " score decreases.")
        print()
        print("Now, let me show to you that it is also possible that the " + str(measure).lower() + " score stays unchanged.")
        log1 = ["ae", "ae", "ae", "ae", "abcde"] # for all except affinity
        log2 = log1 + ["abcde", "f"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["ae", "abcde"] # shows conjecture for affinity
        log2 = log1 + ["abcde", "f"]
        log_tuples_eq += [[log1, log2]]
        filename = str(tracenet_miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "-no-change-possible-"
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_eq[0], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(tracenet_miner, all_model_measures, pm4py_logs, filename, False)
        print("In this table, you can see that the " + str(measure).lower() + " score of the trace net did not change.")
        print()
        print("For affinity, we need a different counter example.")
        filename = str(tracenet_miner).replace(" ", "-") + "-vs-" + str(measure).lower().replace(" ", "-") + "affinity-no-change-possible-"
        pm4py_logs = EventLogHandler.show_event_log_comparison(log_tuples_eq[1], all_log_measures, filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        ModelHandler.show_model_comparison(tracenet_miner, all_model_measures, pm4py_logs, filename, False)
        print("In this table, you can see that the " + str(measure).lower() + " score of the trace net did not change.")
        print("Thus, an increase in log-complexity can mean that the " + str(measure).lower() + " score stays unchanged.")
    elif type(measure) == ModelComplexityMeasures.NumberOfDuplicateTasks:
        print()
        # DUPLICATE-EQ: example for all but DT-%
        log1 = ["a", "abcd"]
        log2 = log1 + ["uvwxyz", "uvwxyz"]
        log_tuples_eq = [[log1, log2]]
        # DUPLICATE-EQ: example for DT-%
        log1 = ["a", "a", "a", "a", "abcd"] # with DT-%
        log2 = log1 + ["uvwxyz", "uvwxyz"]
        log_tuples_eq += [[log1, log2]]
        # DUPLICATE-LESS:
        log1 = ["a", "a", "abcd", "abcd", "abcd"]
        log2 = log1 + ["eabcd", "eabcd"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(tracenet_miner, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.CrossConnectivity:
        # CROSS CONNECTIVITY: example for all but nvar-e
        log1 = ["abcd", "abcd", "acce", "acce", "aaaa", "aaaa"]
        log2 = log1 + ["aabccdef"]
        log3 = log2 + ["gaabccdefaabccdef"]
        log_triples = [[log1, log2, log3]]
        # CROSS CONNECTIVITY: example for nvar-e
        log1 = ["a", "abc"]
        log2 = log1 + ["abcde", "xyz"]
        log3 = log2 + ["fghijklmnop"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, tracenet_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.Sequentiality:
        # SEQUENTIALITY: example for all but affinity
        log1 = ["abcde", "abcde", "abcde", "edcab", "edcab", "edcab"]
        log2 = log1 + ["afedcb", "afedcb"]
        log3 = log2 + ["gacdebf", "gacdebf", "ab"]
        log_triples = [[log1, log2, log3]]
        # SEQUENTIALITY: example for affinity
        log1 = ["abcde", "abcde", "abcde", "edcab", "edcab", "edcab"]
        log2 = log1 + ["fedcab", "fedcab"]
        log3 = log2 + ["gfedcab", "gfedcab", "gfedcab", "gfedcab", "gfedcab", "ab"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, tracenet_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.CoefficientOfNetworkConnectivity:
        # COEFFICIENT OF NETWORK CONNECTIVITY: example for all but nvar-e
        log1 = ["abcd", "abcd", "acce", "acce", "aaaa", "aaaa"]
        log2 = log1 + ["aabccdef"]
        log3 = log2 + ["gaabccdefaabccdf"]
        log_triples = [[log1, log2, log3]]
        # COEFFICIENT OF NETWORK CONNECTIVITY: example for nvar-e
        log1 = ["ab", "abcd", "abce"]
        log2 = log1 + ["stuvwxyz"]
        log3 = log2 + ["bcdefghijklm"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, tracenet_miner, log_triples)
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + str(measure).lower() + " measure.")
##########################################################

################## Alpha Miner Analysis ##################
def show_alpha_miner_analysis(measure):
    alpha_miner = DiscoveryAlgorithms.AlphaMiner()
    if type(measure) in [ModelComplexityMeasures.Size, ModelComplexityMeasures.TokenSplit,
                         ModelComplexityMeasures.ControlFlowComplexity, ModelComplexityMeasures.AverageConnectorDegree,
                         ModelComplexityMeasures.MaximumConnectorDegree, ModelComplexityMeasures.Cyclicity,
                         ModelComplexityMeasures.NumberOfEmptySequenceFlows]:
        log1 = ["abcde", "abcde", "abcde", "e", "e"]
        log2 = log1 + ["abcdbcdef", "abcdbcdef"]
        log3 = log2 + ["abcdbcdbcde", "abcdbcdbcde", "abcdbcdbcdbcdde", "aabbccddeeffgghhii"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) in [ModelComplexityMeasures.ConnectorMismatch, ModelComplexityMeasures.ConnectorHeterogeneity,
                           ModelComplexityMeasures.Depth]:
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffgg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) in [ModelComplexityMeasures.CrossConnectivity, ModelComplexityMeasures.Sequentiality]:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffgg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.Separability:
        # SEPARABILITY: example for all but affinity
        log1 = ["abcde", "abcde", "abcde", "edcab", "edcab", "edcab"]
        log2 = log1 + ["afedcb", "afedcb"]
        log3 = log2 + ["gbcdefc", "gbcdefc"]
        log_triples = [[log1, log2, log3]]
        # SEPARABILITY: example for affinity
        log1 = ["abcde", "edcab"]
        log2 = log1 + ["afedcb", "afedcb"]
        log3 = log2 + ["gbcdefc", "gbcdefc", "gbcdefc", "gbcdefc"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.Diameter:
        # DIAMETER: example for all except affinity
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffgg", "hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcde", "abdce", "auvxyz"]
        log2 = log1 + ["abcdefgh"]
        log3 = log2 + ["d", "g", "ce", "abcde", "abcde", "bbcddeffgghh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.CoefficientOfNetworkConnectivity:
        # COEFFICIENT OF NETWORK CONNECTIVITY: example for all except affinity
        log1 = ["acd", "acd", "acd", "acd", "b"]
        log2 = log1 + ["acde", "bcde", "bced"]
        log3 = log2 + ["acde", "aced", "abcd", "aabbccddeeff", "c"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcde", "abdce", "auvxyz"]
        log2 = log1 + ["abcdefgh"]
        log3 = log2 + ["d", "g", "ce", "abcde", "abcde", "bbcddeffgghh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.Density:
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcd", "abcd", "abcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffggee", "aahhiijjee"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, alpha_miner, log_triples)
    elif type(measure) == ModelComplexityMeasures.NumberOfDuplicateTasks:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + str(measure).lower() + " measure.")
##########################################################

############ Directly Follows Graph Analysis ############
def show_dfg_analysis(measure):
    dfg = DiscoveryAlgorithms.DirectlyFollowsGraphMiner()
    if type(measure) == ModelComplexityMeasures.Size:
        print("First, observe that var(L1) < var(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        # SIZE-EQ:
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabc"]
        log_tuples_eq = [[log1, log2]]
        # SIZE-LESS:
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabcf"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfg, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.ConnectorMismatch:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.CrossConnectivity:
        log1 = ["ab", "ab", "ab", "ab", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "stuvwxyz"]
        log3 = log2 + ["hijklmnop"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcd", "cdef", "efg", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "abcd", "qrst", "uvwxyz"]
        log3 = log2 + ["abcd", "abcd", "abcd", "h", "i", "j"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.ControlFlowComplexity:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        # CFC-EQ: without affinity
        log1 = ["abcc", "abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq = [[log1, log2]]
        # CFC-EQ: for affinity
        log1 = ["abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq += [[log1, log2]]
        # CFC-LESS:
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabcf"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfg, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Separability:
        log1 = ["a", "abc"]
        log2 = log1 + ["abc", "ijklm"]
        log3 = log2 + ["abc", "abc", "acd", "ace", "ijxjkyklzlm"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "abc", "abc", "abc"]
        log2 = log1 + ["ijklm"]
        log3 = log2 + ["acd", "ace", "ijxjkyklzlm"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.AverageConnectorDegree:
        log1 = ["ab", "ab", "ab", "c", "d", "e"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["cx", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.MaximumConnectorDegree:
        # MAXCONN-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # MAXCONN-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfg, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Sequentiality:
        log1 = ["abde", "abde", "acde", "acde", "abcde", "e"]
        log2 = log1 + ["abdacd", "abdacd", "abcdefg"]
        log3 = log2 + ["abdabdacd", "abcdefh"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abde", "abde", "abde", "acde", "acde", "abcde", "e"]
        log2 = log1 + ["abdacd", "abdacd", "abcdefg"]
        log3 = log2 + ["abdabdacd", "abcdefh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.Cyclicity:
        log1 = ["a", "abccd", "abbcd"]
        log2 = log1 + ["aabbccdde"]
        log3 = log2 + ["abbccd", "aaabbbcccddd", "vwxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "abccd", "abbcd"]
        log2 = log1 + ["aabbccdde"]
        log3 = log2 + ["abbccd", "aaabbbcccddd", "vwxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.Depth:
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["abcx", "hi"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "ab", "ab", "ab", "ab", "ab", "ab", "cx", "dy", "ez"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["bc", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.Diameter:
        # DIAMETER-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # DIAMETER-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfg, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.CoefficientOfNetworkConnectivity:
        log1 = ["aabbccdd", "aabbccdd", "bcd", "bcd", "bcd"]
        log2 = log1 + ["bcd", "aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "uvxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["aabbccdd", "bcd"]
        log2 = log1 + ["aabbccddee"]
        log3 = log2 + ["aaabbbcccdddeee", "aaabbbcccdddeee", "aaabbbcccdddeee", "uvxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    elif type(measure) == ModelComplexityMeasures.Density:
        log1 = ["a", "abcd"]
        log2 = log1 + ["abbccddee"]
        log3 = log2 + ["ae", "abbcbcddee", "abbcbcddee", "vvxxyxyyzz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "a", "a", "abcd"]
        log2 = log1 + ["abbccddee"]
        log3 = log2 + ["ae", "abbcbcddee", "abbcbcddee", "vvxxyxyyzz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfg, log_triples)
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + str(measure).lower() + " measure.")
#########################################################

############ Directly Follows Miner Analysis ############
def show_dfm_analysis(measure):
    dfm = DiscoveryAlgorithms.DirectlyFollowsModelMiner()
    if type(measure) == ModelComplexityMeasures.Size:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        # SIZE-EQ: without affinity
        log1 = ["abcc", "abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq = [[log1, log2]]
        # SIZE-EQ: for affinity
        log1 = ["abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq += [[log1, log2]]
        # CFC-LESS:
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabcf"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.ConnectorMismatch:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.ConnectorHeterogeneity:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    elif type(measure) == ModelComplexityMeasures.CrossConnectivity:
        # CROSS CONNECTIVITY: example for all but affinity and nvar-e
        log1 = ["ab", "ab", "ab", "ab", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "stuvwxyz"]
        log3 = log2 + ["hijklmnop"]
        log_triples = [[log1, log2, log3]]
        # CROSS CONNECTIVITY: example for affinity and nvar-e
        log1 = ["abcd", "cdef", "efg", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "abcd", "qrst", "uvwxyz"]
        log3 = log2 + ["abcd", "abcd", "abcd", "h", "i", "j"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.TokenSplit:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    elif type(measure) == ModelComplexityMeasures.ControlFlowComplexity:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        # SIZE-EQ: without affinity
        log1 = ["abcc", "abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq = [[log1, log2]]
        # SIZE-EQ: for affinity
        log1 = ["abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq += [[log1, log2]]
        # CFC-LESS:
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabcf"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Separability:
        log1 = ["a", "abc"]
        log2 = log1 + ["abc", "ijjk"]
        log3 = log2 + ["abcd", "aabbcc", "iijjkk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "a", "a", "abc"]
        log2 = log1 + ["abc", "ijjk"]
        log3 = log2 + ["abcd", "aabbcc", "iijjkk"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.AverageConnectorDegree:
        log1 = ["ab", "ab", "ab", "c", "d", "e"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["cx", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.MaximumConnectorDegree:
        # MAXCONN-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # MAXCONN-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Sequentiality:
        # SEQUENTIALITY: example for all but DT-%
        log1 = ["a", "abc"]
        log2 = log1 + ["aabbccdd"]
        log3 = log2 + ["aabbccdd", "fghijklmnopq"]
        log_triples = [[log1, log2, log3]]
        # SEQUENTIALITY: example for DT-%
        log1 = ["a", "abc", "abc", "abc", "abc", "abc"]
        log2 = log1 + ["aabbccdd"]
        log3 = log2 + ["aabbccdd", "fghijklmnopq"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.Diameter:
        # DIAMETER-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # DIAMETER-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.Cyclicity:
        # CYCLICITY: example for all but DT-%
        log1 = ["a", "abcc"]
        log2 = log1 + ["abbcde"]
        log3 = log2 + ["abbbcdde", "abbbcdde", "vwxyz"]
        log_triples = [[log1, log2, log3]]
        # CYCLICITY: example for DT-%
        log1 = ["a", "a", "a", "abcc"]
        log2 = log1 + ["abbcde"]
        log3 = log2 + ["abbbcdde", "abbbcdde", "vwxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.Depth:
        # DEPTH: example for all but affinity
        log1 = ["ab", "ab", "cx", "cx", "dy", "dy", "ez"]
        log2 = log1 + ["ab", "agb", "aggb"]
        log3 = log2 + ["agggb", "agggb", "bc", "hi"]
        log_triples = [[log1, log2, log3]]
        # DEPTH: example for affinity
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "aggb"]
        log3 = log2 + ["agggb", "agggb", "agggb", "bc", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.CoefficientOfNetworkConnectivity:
        log1 = ["aabbccdd", "bcd", "bcd", "bcd"]
        log2 = log1 + ["bcd", "aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "uvxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["aabbccdd", "bcd"]
        log2 = log1 + ["aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "aaabbbcccdddeee", "aaabbbcccdddeee", "uvxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, dfm, log_triples)
    elif type(measure) == ModelComplexityMeasures.Density:
        print("First, observe that var(L1) < var(L2) always implies a decrease in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abcc", "abcc", "ccde"]
        log2 = log1 + ["abcde", "abde"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["abcc", "ccde"]
        log2 = log1 + ["abcde", "abde"]
        log_tuples_eq += [[log1, log2]]
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabcf"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less, "decreas")
    elif type(measure) == ModelComplexityMeasures.NumberOfDuplicateTasks:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + str(measure).lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abcc", "abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["abcc", "ccde"]
        log2 = log1 + ["abcde"]
        log_tuples_eq += [[log1, log2]]
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(dfm, measure, log_tuples_eq, log_tuples_less)
    elif type(measure) == ModelComplexityMeasures.NumberOfEmptySequenceFlows:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + str(measure).lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + str(measure).lower() + " measure.")
#########################################################

def show_analysis_for(measure: str, miner: str):
    if type(miner) == DiscoveryAlgorithms.FlowerModelMiner:
        show_flower_model_analysis(measure)
    elif type(miner) == DiscoveryAlgorithms.TraceNetMiner:
        show_trace_net_analysis(measure)
    elif type(miner) == DiscoveryAlgorithms.AlphaMiner:
        show_alpha_miner_analysis(measure)
    elif type(miner) == DiscoveryAlgorithms.DirectlyFollowsGraphMiner:
        show_dfg_analysis(measure)
    elif type(miner) == DiscoveryAlgorithms.DirectlyFollowsModelMiner:
        show_dfm_analysis(measure)
    else:
        raise Exception("Unexpected mining algorithm: " + str(miner))
