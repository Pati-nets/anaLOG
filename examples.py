import pm4py # for event log handling and an implementation of the alpha miner

import DirectlyFollowsGraph as dfg # (internal) for mining directly follows graphs
from discovery import DirectlyFollowsMiner as dfm # (internal) for mining directly follows (Petri net) models
from discovery import BaselineMiners # (internal) for mining the flower model and the trace net
import Compare # (internal) for printing and thus comparing log- and model-complexity scores of multiple inputs
import Constants # (internal) strings representing the supported mining algorithms and complexity measures
from ModelWrapper import ModelWrapper # (internal) a wrapper class for maintaining a net, its initial and final marking


def handle_event_logs(event_logs: list, logname_prefix=""):
    print("Consider the following event logs:")
    for i in range(len(event_logs)):
        log = event_logs[i]
        Compare.print_event_log(log, "L" + str(i + 1))
    print("I will store them for you in the output folder, so you can look at them later.")
    print()
    print("I will also convert these event logs into pm4py format, so we can start the analysis.")
    filename_prefix = Constants.OUTPUT_PATH + logname_prefix + "L"
    for i in range(len(event_logs)):
        filename = filename_prefix + str(i + 1) + ".xes"
        pm4py.write_xes(Compare.convert_language_to_dataframe(event_logs[i]), filename)
    print("Done!")
    print()
    pm4py_logs = []
    for i in range(len(event_logs)):
        pm4py_logs += [Compare.import_pm4py_log(filename_prefix + str(i + 1) + ".xes")]
    return pm4py_logs

def show_event_log_comparison(event_logs: list, logname_prefix=""):
    pm4py_logs = handle_event_logs(event_logs, logname_prefix)
    print("Next, let me calculate the log complexity scores of these event logs.")
    Compare.print_log_complexities(pm4py_logs, True)
    return pm4py_logs

def calculate_models(miner: str, pm4py_logs, filename_prefix="", silent=False):
    if not silent:
        print("I will now use the " + miner.lower() + " to find models for these event logs.")
    models = []
    for i in range(len(pm4py_logs)):
        if miner == Constants.dfg:
            graph = dfg.DirectlyFollowsGraph(pm4py_logs[i])
            models += [graph]
            graph.visualize(Constants.OUTPUT_PATH + filename_prefix + "DFG" + str(i + 1))
        else:
            if miner == Constants.flower:
                net, im, fm = BaselineMiners.flower_miner(pm4py_logs[i])
            elif miner == Constants.trace:
                net, im, fm = BaselineMiners.trace_net_miner(pm4py_logs[i])
            elif miner == Constants.alpha:
                net, im, fm = pm4py.discover_petri_net_alpha(pm4py_logs[i])
            elif miner == Constants.dfm:
                net, im, fm = dfm.directly_follows_miner(pm4py_logs[i])
            else:
                raise Exception("Unexpected mining algorithm: " + str(miner))
            marked_petri_net = ModelWrapper(net, im, fm)
            models += [marked_petri_net]
            pm4py.save_vis_petri_net(marked_petri_net.net, marked_petri_net.initial_marking, marked_petri_net.final_marking, file_path=Constants.OUTPUT_PATH+filename_prefix+"M" + str(i) + ".png")
    if not silent:
        print("Done!")
    return models

def show_model_comparison(miner: str, pm4py_logs, filename_prefix="", colored=True, just_table=False):
    models = calculate_models(miner, pm4py_logs, filename_prefix, just_table)
    if not just_table:
        print("Next, let me calculate the model complexity scores of these models.")
    if miner == Constants.dfg:
        Compare.print_graph_complexities(models, colored)
    else:
        Compare.print_model_complexities(models, colored)
    return models

def print_counter_example(measure: str, miner: str, log_triples: list):
    print("Let me show you which log-complexity measures have no influence on the " + measure.lower() + " of the " + miner.lower() + ".")
    filename = miner.lower().replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-"
    pm4py_logs = show_event_log_comparison(log_triples[0], filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    show_model_comparison(miner, pm4py_logs, filename)
    print("Again, I highlighted the complexity measures C in green where we can see an increase and a decrease when log-complexity increases.")
    print("Since " + measure.lower() + " is one of these measures, we cannot predict what will happen to the " + measure.lower() + " of the " + miner.lower() + " when log-complexity increases.")
    for i in range(1,len(log_triples)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = miner.lower().replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-" + str(i+1) + "-"
        pm4py_logs = show_event_log_comparison(log_triples[i], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(miner, pm4py_logs, filename)
        print("This shows that also the newly green colored log-complexity measures cannot predict the " + measure.lower() + " of the " + miner.lower() + " when log-complexity increases.")


def show_measure_pair_in_leq(miner: str, measure: str, log_tuples_eq: list, log_tuples_less: list, direction="increas"):
    print("Let me now show you that an increase in log complexity can mean " + measure.lower() + " " + direction + "es or stays unchanged.")
    print("I will start with the former.")
    filename = miner.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-" + direction + "e-possible-"
    pm4py_logs = show_event_log_comparison(log_tuples_less[0], filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    show_model_comparison(miner, pm4py_logs, filename)
    print("In this table, you can see that the " + measure.lower() + " score of the flower model " + direction + "d.")
    print("Thus, an increase in log-complexity can mean that the " + measure.lower() + " score " + direction + "es.")
    for i in range(1,len(log_tuples_less)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = miner.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-" + direction + "e-possible-" + str(i+1) + "-"
        pm4py_logs = show_event_log_comparison(log_tuples_less[i], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(miner, pm4py_logs, filename)
        print("Thus also an increase in the newly green colored log-complexity measures can mean that the " + measure.lower() + " score " + direction + "es.")

    print()
    print("Now, let me show to you that it is also possible that the " + measure.lower() + " score stays unchanged.")
    filename = miner.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-no-change-possible-"
    pm4py_logs = show_event_log_comparison(log_tuples_eq[0], filename)
    print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
    show_model_comparison(miner, pm4py_logs, filename)
    print("In this table, you can see that the " + measure.lower() + " score of the " + miner.lower() + " result did not change.")
    print("Thus, an increase in log-complexity can mean that the " + measure.lower() + " score stays unchanged.")
    for i in range(1,len(log_tuples_eq)):
        print()
        print("For the log complexity measures that remained red in the previous example, we need a different example.")
        filename = miner.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-no-change-possible-" + str(i+1) + "-"
        pm4py_logs = show_event_log_comparison(log_tuples_eq[i], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(miner, pm4py_logs, filename)
        print("Thus also an increase in the newly green colored log-complexity measures can mean that the " + measure.lower() + " score stays unchanged.")


def show_flower_model_analysis(measure: str):
    print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their flower models.")
    leq_entries = [Constants.size, Constants.crossconn, Constants.controlflow, Constants.separability, Constants.avgconn]
    leq_entries += [Constants.maxconn, Constants.sequentiality, Constants.cyclicity, Constants.netconn]
    eq_entries = [Constants.mismatch, Constants.connhet, Constants.tokensplit, Constants.depth, Constants.diameter]
    eq_entries += [Constants.density, Constants.duplicate, Constants.emptyseq]
    if measure in leq_entries:
        print("First, observe that var(L1) < var(L2) always implies an increase in " + measure.lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "ecdabc"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["a", "a", "abcd", "abcd", "abcd"]
        log2 = log1 + ["eabcd"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.flower, measure, log_tuples_eq, log_tuples_less)
    elif measure in eq_entries:
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + measure.lower() + " measure.")


def show_trace_net_analysis(measure: str):
    leq_entries = [Constants.size, Constants.controlflow, Constants.avgconn, Constants.maxconn]
    eq_entries = [Constants.mismatch, Constants.connhet, Constants.tokensplit, Constants.depth]
    eq_entries += [Constants.separability, Constants.cyclicity, Constants.emptyseq]
    if measure in leq_entries:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
        print("First, observe that var(L1) < var(L2), TL-max(L1) < TL-max(L2), LOD(L1) < LOD(L2), t-comp(L1) < t-comp(L2)")
        print("DT-#(L1) < DT-#(L2), DT-%(L1) < DT-%(L2), var-e(L1) < var-2(L2), nvar-e(L1) < nvar-e(L2) all imply an")
        print("increase in the " + measure + " score from M1 to M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abc", "abcd", "abcd", "abcde", "abcde", "deab"]
        log2 = log1 + ["abcde", "abcde", "abcde", "deab", "deab", "deab"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["abc", "abcd", "abcd", "abcde", "abcde", "deab"]
        log2 = log1 + ["abcdef", "aabcdef", "abcdeab"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.trace, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.diameter:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
        print("First, observe that TL-max(L1) < TL-max(L2) always implies an increase in " + measure.lower() + ".")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print()
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdab"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdabc"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.trace, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.density:
        print("First, observe that an increase in TL-max or t-comp means a decrease in density.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
        print("Let me now show you that an increase in log complexity can mean density decreases or stays unchanged.")
        print("I will start with the former.")
        log1 = ["abcd", "abcd", "abcde", "abcde", "deab", "deab"]
        log2 = log1 + ["abcde", "abcde", "deabc", "cdeab", "fcdabc"]
        log_tuples_greater = [[log1, log2]]
        filename = Constants.trace.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-decrease-possible-"
        pm4py_logs = show_event_log_comparison(log_tuples_greater[0], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(Constants.trace, pm4py_logs, filename)
        print("In this table, you can see that the " + measure.lower() + " score of the trace net decreased.")
        print("Thus, an increase in log-complexity can mean that the " + measure.lower() + " score decreases.")
        print()
        print("Now, let me show to you that it is also possible that the " + measure.lower() + " score stays unchanged.")
        log1 = ["ae", "ae", "ae", "ae", "abcde"] # doesn't show conjecture for affinity
        log2 = log1 + ["abcde", "f"]
        log_tuples_eq = [[log1, log2]]
        log1 = ["ae", "abcde"] # shows conjecture for affinity
        log2 = log1 + ["abcde", "f"]
        log_tuples_eq += [[log1, log2]]
        filename = Constants.trace.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "-no-change-possible-"
        pm4py_logs = show_event_log_comparison(log_tuples_eq[0], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(Constants.trace, pm4py_logs, filename)
        print("In this table, you can see that the " + measure.lower() + " score of the trace net did not change.")
        print()
        print("For affinity, we need a different counter example.")
        filename = Constants.trace.replace(" ", "-") + "-vs-" + measure.lower().replace(" ", "-") + "affinity-no-change-possible-"
        pm4py_logs = show_event_log_comparison(log_tuples_eq[1], filename)
        print("For your convenience, I highlighted the entries of this table that are strictly increasing in green.")
        show_model_comparison(Constants.trace, pm4py_logs, filename)
        print("In this table, you can see that the " + measure.lower() + " score of the trace net did not change.")
        print("Thus, an increase in log-complexity can mean that the " + measure.lower() + " score stays unchanged.")
    elif measure == Constants.duplicate:
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
        show_measure_pair_in_leq(Constants.trace, measure, log_tuples_eq, log_tuples_less)
    elif measure in eq_entries:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are their trace nets.")
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    elif measure == Constants.crossconn:
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
        print_counter_example(measure, Constants.trace, log_triples)
    elif measure == Constants.sequentiality:
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
        print_counter_example(measure, Constants.trace, log_triples)
    elif measure == Constants.netconn:
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
        print_counter_example(measure, Constants.trace, log_triples)
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + measure.lower() + " measure.")


def show_alpha_miner_analysis(measure):
    if measure in [Constants.size, Constants.tokensplit, Constants.controlflow, Constants.avgconn, Constants.maxconn, Constants.cyclicity, Constants.emptyseq]:
        log1 = ["abcde", "abcde", "abcde", "e", "e"]
        log2 = log1 + ["abcdbcdef", "abcdbcdef"]
        log3 = log2 + ["abcdbcdbcde", "abcdbcdbcde", "abcdbcdbcdbcdde", "aabbccddeeffgghhii"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure in [Constants.mismatch, Constants.connhet, Constants.depth]:
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffgg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure in [Constants.crossconn, Constants.sequentiality]:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffgg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure == Constants.separability:
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
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure == Constants.diameter:
        # DIAMETER: example for all except affinity
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffgg", "hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcde", "abdce", "auvxyz"]
        log2 = log1 + ["abcdefgh"]
        log3 = log2 + ["d", "g", "ce", "abcde", "abcde", "bbcddeffgghh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure == Constants.netconn:
        # COEFFICIENT OF NETWORK CONNECTIVITY: example for all except affinity
        log1 = ["acd", "acd", "acd", "acd", "b"]
        log2 = log1 + ["acde", "bcde", "bced"]
        log3 = log2 + ["acde", "aced", "abcd", "aabbccddeeff", "c"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcde", "abdce", "auvxyz"]
        log2 = log1 + ["abcdefgh"]
        log3 = log2 + ["d", "g", "ce", "abcde", "abcde", "bbcddeffgghh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure == Constants.density:
        log1 = ["abcd", "abcd", "abcd", "e", "e"]
        log2 = log1 + ["acbd", "abcd", "abcd", "abcd", "abcbcd", "abcbcd", "abcbcd", "bcbcbcd", "abcfefe"]
        log3 = log2 + ["abcd", "abcd", "abcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcd", "abcbcbcbcbcd", "aabbccdd", "eeffggee", "aahhiijjee"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.alpha, log_triples)
    elif measure == Constants.duplicate:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + measure.lower() + " measure.")


def show_dfg_analysis(measure: str):
    if measure == Constants.size:
        print("First, observe that var(L1) < var(L2) always implies an increase in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfg, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.mismatch:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.crossconn:
        log1 = ["ab", "ab", "ab", "ab", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "stuvwxyz"]
        log3 = log2 + ["hijklmnop"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abcd", "cdef", "efg", "ab", "cd", "ef", "g"]
        log2 = log1 + ["abcd", "abcd", "qrst", "uvwxyz"]
        log3 = log2 + ["abcd", "abcd", "abcd", "h", "i", "j"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.controlflow:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfg, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.separability:
        log1 = ["a", "abc"]
        log2 = log1 + ["abc", "ijklm"]
        log3 = log2 + ["abc", "abc", "acd", "ace", "ijxjkyklzlm"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "abc", "abc", "abc"]
        log2 = log1 + ["ijklm"]
        log3 = log2 + ["acd", "ace", "ijxjkyklzlm"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.avgconn:
        log1 = ["ab", "ab", "ab", "c", "d", "e"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["cx", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.maxconn:
        # MAXCONN-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # MAXCONN-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.dfg, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.sequentiality:
        log1 = ["abde", "abde", "acde", "acde", "abcde", "e"]
        log2 = log1 + ["abdacd", "abdacd", "abcdefg"]
        log3 = log2 + ["abdabdacd", "abcdefh"]
        log_triples = [[log1, log2, log3]]
        log1 = ["abde", "abde", "abde", "acde", "acde", "abcde", "e"]
        log2 = log1 + ["abdacd", "abdacd", "abcdefg"]
        log3 = log2 + ["abdabdacd", "abcdefh"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.cyclicity:
        log1 = ["a", "abccd", "abbcd"]
        log2 = log1 + ["aabbccdde"]
        log3 = log2 + ["abbccd", "aaabbbcccddd", "vwxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "abccd", "abbcd"]
        log2 = log1 + ["aabbccdde"]
        log3 = log2 + ["abbccd", "aaabbbcccddd", "vwxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.depth:
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["abcx", "hi"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "ab", "ab", "ab", "ab", "ab", "ab", "cx", "dy", "ez"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["bc", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.diameter:
        # DIAMETER-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # DIAMETER-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.dfg, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.netconn:
        log1 = ["aabbccdd", "aabbccdd", "bcd", "bcd", "bcd"]
        log2 = log1 + ["bcd", "aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "uvxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["aabbccdd", "bcd"]
        log2 = log1 + ["aabbccddee"]
        log3 = log2 + ["aaabbbcccdddeee", "aaabbbcccdddeee", "aaabbbcccdddeee", "uvxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    elif measure == Constants.density:
        log1 = ["a", "abcd"]
        log2 = log1 + ["abbccddee"]
        log3 = log2 + ["ae", "abbcbcddee", "abbcbcddee", "vvxxyxyyzz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "a", "a", "abcd"]
        log2 = log1 + ["abbccddee"]
        log3 = log2 + ["ae", "abbcbcddee", "abbcbcddee", "vvxxyxyyzz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfg, log_triples)
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + measure.lower() + " measure.")


def show_dfm_analysis(measure: str):
    if measure == Constants.size:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.mismatch:
        log1 = ["abd", "abd", "acd", "acd", "e"]
        log2 = log1 + ["abde", "acde", "abcd", "abcbdef", "abcbcbdef"]
        log3 = log2 + ["acbd", "acbcbde", "abcbcbcd", "abcbcbcbcd", "aabbccddeeffg"]
        log_triples = [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.connhet:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    elif measure == Constants.crossconn:
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
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.tokensplit:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    elif measure == Constants.controlflow:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.separability:
        log1 = ["a", "abc"]
        log2 = log1 + ["abc", "ijjk"]
        log3 = log2 + ["abcd", "aabbcc", "iijjkk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["a", "a", "a", "a", "abc"]
        log2 = log1 + ["abc", "ijjk"]
        log3 = log2 + ["abcd", "aabbcc", "iijjkk"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.avgconn:
        log1 = ["ab", "ab", "ab", "c", "d", "e"]
        log2 = log1 + ["agb"]
        log3 = log2 + ["hijk"]
        log_triples = [[log1, log2, log3]]
        log1 = ["ab", "cx", "dy", "ez"]
        log2 = log1 + ["ab", "agb"]
        log3 = log2 + ["cx", "hi"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.maxconn:
        # MAXCONN-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # MAXCONN-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.sequentiality:
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
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.diameter:
        # DIAMETER-EQ
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde"]
        log_tuples_eq = [[log1, log2]]
        # DIAMETER-LESS
        log1 = ["abcc", "c", "c", "ccde"]
        log2 = log1 + ["abcde", "abffde", "abfffde", "abffffde", "abffffde", "accdeg"]
        log_tuples_less = [[log1, log2]]
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.cyclicity:
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
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.depth:
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
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.netconn:
        log1 = ["aabbccdd", "bcd", "bcd", "bcd"]
        log2 = log1 + ["bcd", "aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "uvxxyz"]
        log_triples = [[log1, log2, log3]]
        log1 = ["aabbccdd", "bcd"]
        log2 = log1 + ["aabbccddee", "abcde"]
        log3 = log2 + ["aaabbbcccdddeee", "aaabbbcccdddeee", "aaabbbcccdddeee", "uvxxyz"]
        log_triples += [[log1, log2, log3]]
        print_counter_example(measure, Constants.dfm, log_triples)
    elif measure == Constants.density:
        print("First, observe that var(L1) < var(L2) always implies a decrease in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less, "decreas")
    elif measure == Constants.duplicate:
        print("First, observe that var(L1) < var(L2), LOD(L1) < LOD(L2), and t-comp(L1) < t-comp(L2) always implies an increase in " + measure.lower() + ".")
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
        show_measure_pair_in_leq(Constants.dfm, measure, log_tuples_eq, log_tuples_less)
    elif measure == Constants.emptyseq:
        print("Suppose L1 and L2 are event logs, where L1 is a subset of L2, and M1 and M2 are the models found by the alpha miner for L1 and L2.")
        print("Then, the " + measure.lower() + " score is always the same for M1 and M2.")
        print("You can find the proof for this conjecture in " + Constants.arxive_link + ".")
    else:
        raise Exception("Unexpected complexity measure " + str(measure))
    print("This concludes the analysis of the " + measure.lower() + " measure.")


def show_analysis_for(measure: str, miner: str):
    if miner == Constants.flower:
        show_flower_model_analysis(measure)
    elif miner == Constants.trace:
        show_trace_net_analysis(measure)
    elif miner == Constants.alpha:
        show_alpha_miner_analysis(measure)
    elif miner == Constants.dfg:
        show_dfg_analysis(measure)
    elif miner == Constants.dfm:
        show_dfm_analysis(measure)
    else:
        raise Exception("Unexpected mining algorithm: " + str(miner))
