import pandas
import questionary # to ask the user for measures and discovery algorithms
from tabulate import tabulate # for pretty printing of tables

import complexity_analysis # to calculate complexity scores and normalized distances
import complexity_conditioning # to calculate the conditioning of a discovery algorithm
import complexity_stability # to calculate the stability of a discovery algorithm
import regression_analysis # to perform a regression analysis of complexity measures

log_measures = ['n_events', # magnitude C_{mag}
                'n_unique_activities', # variety C_{var}
                'n_traces', # length C_{len}
                'trace_len_mean', # average trace length C_{TL-avg}
                'trace_len_max', # maximum trace length C_{TL-max}
                'number_of_ties', # number of ties C_{t-comp}
                'lempel_ziv_complexity', # Lempel-Ziv complexity C_{LZ}
                'n_variants', # number of distinct traces C_{DT-#}
                'ratio_variants_per_number_of_traces', # percentage of distinct traces C_{DT-%}
                'distinct_activities_mean', # structure C_{struct}
                'deviation_from_random', # deviation from random C_{dev-R}
                'epa_variant_entropy', # variant entropy C_{var-e}
                'epa_normalized_variant_entropy', # normalized variant entropy C_{nvar-e}
                'epa_sequence_entropy', # sequence entropy C_{seq-e}
                'epa_normalized_sequence_entropy' # normalized sequence entropy C_{nseq-e}
                ]

mod_measures = ['size', # size C_{size}
                'connector_mismatch', # connector mismatch C_{MM}
                'connector_heterogeneity', # connector heterogeneity C_{CH}
                'token_split', # token split C_{ts}
                'separability', # separability C_{sep}
                'control_flow_complexity', # control flow complexity C_{CFC}
                'average_connector_degree', # average connector degree C_{acd}
                'maximum_connector_degree', # maximum connector degree C_{mcd}
                'sequentiality', # sequentiality C_{seq}
                'cyclicity', # cyclicity C_{cyc}
                'density', # density C_{dens}
                'coefficient_of_network_connectivity', # coefficient of network connectivity C_{CNC}
                'number_of_duplicate_tasks', # number of duplicate tasks C_{dup}
                'empty_sequence_flows' # number of empty sequence flows C_{\emptyset}
                ]

short_name = {'n_events': 'mag',
              'n_unique_activities': 'var',
              'n_traces': 'len',
              'trace_len_mean': 'TL-avg',
              'trace_len_max': 'TL-max',
              'number_of_ties': 't-comp',
              'lempel_ziv_complexity': 'LZ',
              'n_variants': 'DT-#',
              'ratio_variants_per_number_of_traces': 'DT-%',
              'distinct_activities_mean': 'struct',
              'deviation_from_random': 'dev-R',
              'epa_variant_entropy': 'var-e',
              'epa_normalized_variant_entropy': 'nvar-e',
              'epa_sequence_entropy': 'seq-e',
              'epa_normalized_sequence_entropy': 'nseq-e',
              'size': 'size',
              'connector_mismatch': 'MM',
              'connector_heterogeneity': 'CH',
              'token_split': 'ts',
              'separability': 'sep',
              'control_flow_complexity': 'CFC',
              'average_connector_degree': 'acd',
              'maximum_connector_degree': 'mcd',
              'sequentiality': 'seq',
              'cyclicity': 'cyc',
              'density': 'dens',
              'coefficient_of_network_connectivity': 'CNC',
              'number_of_duplicate_tasks': 'dup',
              'empty_sequence_flows': '∅'
              }

discovery_algo = ['alpha', # Alpha Miner
                  'inductive', # Inductive Miner
                  'inductive_inf', # Inductive Miner Infrequent
                  'heuristics' # Heuristics Miner
                  ]

noise_types = ['ABSENCE',
               'INSERTION',
               'ORDERING',
               'SUBSTITUTION',
               'MIXED'
               ]

noise_ratios = ['0.1', '0.2', '0.4', '1.0']

well = "\033[92m" + '✓' + "\x1b[0m"
moderately = "\033[93m" + '~' + "\x1b[0m"
ill = "\033[91m" + 'X' + "\x1b[0m"

def ask_user_for_log_measure():
    question = "Please specify the log complexity measure you wish to analyze."
    response = questionary.select(question, choices=log_measures).ask()
    return response

def ask_user_for_model_measure():
    question = "Please specify the model complexity measure you wish to analyze."
    response = questionary.select(question, choices=mod_measures).ask()
    return response

def ask_user_for_discovery_algorithm():
    question = "Please specify the discovery algorithm you wish to analyze."
    response = questionary.select(question, choices=discovery_algo).ask()
    return response

def ask_user_for_noise_type():
    question = "Please specify the type of noise you wish to inject into the event logs."
    response = questionary.select(question, choices=noise_types).ask()
    return response

def ask_user_for_noise_ratio():
    question = "Please specify which ratio of noisy traces you would like to inspect."
    response = questionary.select(question, choices=noise_ratios).ask()
    return response

def perform_specialized_analysis():
    log_csv = "log_complexity_scores.csv"
    mod_csv = "model_complexity_scores.csv"
    print("Welcome to the analysis tool for conditioning and stability of ", end='')
    print("Complexity measures with respect do process discovery algorithms.\n")
    print("To begin, you first need to specify a log complexity measure.")
    log_measure = ask_user_for_log_measure()
    print("Now, we need a model complexity measure to evaluate the discovered Petri nets.")
    mod_measure = ask_user_for_model_measure()
    print("Okay! Now, please specify the discovery algorithm you want to analyze.")
    miner = ask_user_for_discovery_algorithm()
    print("Finally, please specify the type of noise you want to analyze.")
    noise_type = ask_user_for_noise_type()
    print("I will now calculate the log and model distances based on ", end='')
    print("the data provided in " + log_csv + " and " + mod_csv + ".")
    print("This calculation might need some time.")
    distance_data = complexity_analysis.prepare_data_for_analysis(log_csv, mod_csv, log_measure, mod_measure, miner, noise_type)
    print("Next, I will compute the conditioning of the provided data.")
    results = None
    try:
        results = complexity_conditioning.assess_conditioning(distance_data)
    except ValueError:
        print("Whoops, apparently, all log distances are 0, so I cannot calculate conditioning.")
    print("Next up is computing the stability of the provided data.")
    stability = complexity_stability.stability(list(distance_data['dm'].values))
    print("Done! Here are the results of your analysis:")
    if results != None:
        complexity_conditioning.print_conditioning_report(results)
    print("Stability:", stability)
    print("This means the algorithm is ", end='')
    if stability > 0.66:
        print("SEVERELY UNSTABLE.")
    elif stability > 0.33:
        print("MODERATELY STABLE.")
    else:
        print("PERFECTLY STABLE.")

def pretty_print_two_dimensional_results(result_dict: dict):
    row_names = [str(key) for key in result_dict.keys()]
    if len(row_names) == 0:
        return
    column_names = [str(key) for key in result_dict[row_names[0]].keys()]
    result_table = [[""] + [short_name[column] for column in column_names]]
    for row in row_names:
        entries_for_row = [short_name[row]]
        for column in column_names:
            entries_for_row += [result_dict[row][column]]
        result_table += [entries_for_row]
    print(tabulate(result_table, headers='firstrow', tablefmt='fancy_grid'))

def pretty_print_one_dimensional_results(result_dict: dict):
    column_names = [str(key) for key in result_dict.keys()]
    result_table = [[short_name[column] for column in column_names]]
    row = []
    for column in column_names:
        row += [result_dict[column]]
    result_table += [row]
    print(tabulate(result_table, headers='firstrow', tablefmt='fancy_grid'))

def get_zero_columns(distance_data: dict, min_num_zero = 0):
    columns = list(distance_data)
    non_zeros_in_column = dict()
    for column in columns:
        non_zeros_in_column[column] = 0
    for row in distance_data.itertuples():
        for column in columns:
            if distance_data.loc[row.Index][column] != 0:
                non_zeros_in_column[column] += 1
    return [column for column in columns if non_zeros_in_column[column] <= min_num_zero]

def perform_analysis_for_discovery_algorithm_and_noise_type(miner: str, noise_type: str, error_tolerance = 0.5, decimals = 2):
    log_csv = "log_complexity_scores.csv"
    mod_csv = "model_complexity_scores.csv"
    ignore_log_measures = []
    ignore_mod_measures = []
    conditioning_results = dict()
    stability_results = dict()
    stability_computed = False
    # CONDITIONING ANALYSIS
    for log_measure in log_measures:
        # calculate and store the distances of the log complexity scores to the scores for the base log
        log_distance_data = complexity_analysis.calculate_log_distances(log_csv, log_measure, noise_type)
        # ignore a log measure if all its distances are 0, i.e., all log complexity scores are equal
        zero_columns = get_zero_columns(log_distance_data)
        if len(zero_columns) > 0:
            ignore_log_measures += [log_measure]
            print("\033[93m" + "INFO: The log complexity measure", log_measure, "contains only 0-distances and will be excluded from the analysis." + "\x1b[0m")
        # only proceed if the current measure is not in the list of measures to be ignored
        if log_measure not in ignore_log_measures:
            conditioning_results[log_measure] = dict()
            for mod_measure in mod_measures:
                # check if the current model complexity measure should not be ignored
                if mod_measure not in ignore_mod_measures:
                    # calculate and store the distances of the model complexity scores to the scores for the base model
                    mod_distance_data = complexity_analysis.calculate_model_distances(mod_csv, mod_measure, miner, noise_type)
                    # ignore a model complexity measure if all its distances are 0, i.e., all model complexity scores are equal
                    zero_columns = get_zero_columns(mod_distance_data)
                    if len(zero_columns) > 0:
                        ignore_mod_measures += [mod_measure]
                        print("\033[93m" + "INFO: The model complexity measure", mod_measure, "contains only 0-distances and will be excluded from the analysis." + "\x1b[0m")
                        continue
                    # if log and model complexity should not be ignored, proceed with the analysis
                    print("Analyzing measures", log_measure, "and", mod_measure + "...")
                    # join the information about log distance and model distance into a single table
                    distance_data = log_distance_data.join(mod_distance_data).dropna()
                    # check whether there are more than 2 entries that are not 0
                    if 'dl' in get_zero_columns(distance_data, 1):
                        # there is too little training data for the calculation, so we omit the entry
                        print("\033[93m" + "INFO: There is at most one non-zero log distance. This is too low to perform an analysis, so I will omit the entry for", log_measure, "and", mod_measure + "." + "\x1b[0m")
                        conditioning_results[log_measure][mod_measure] = ""
                    else:
                        # calculate conditioning of the current log and model complexity measure
                        conditioning = complexity_conditioning.assess_conditioning(distance_data)
                        # check if the error is below the passed error tolerance
                        if conditioning['relative_error'] > error_tolerance:
                            # print the error instead of an interpretation if the error is too high
                            conditioning_results[log_measure][mod_measure] = "\033[94m" + "(error: " + str(round(conditioning['relative_error'], decimals)) + ")" + "\x1b[0m"
                        else:
                            # store the interpretation of the conditioning analysis
                            if conditioning['interpretation'] == "well-conditioned":
                                conditioning_results[log_measure][mod_measure] = well + " (κ̂ = " + str(round(conditioning['kappa_hat'], decimals)) + ")"
                            elif conditioning['interpretation'] == "moderately conditioned":
                                conditioning_results[log_measure][mod_measure] = moderately + " (κ̂ = " + str(round(conditioning['kappa_hat'], decimals)) + ")"
                            else:
                                conditioning_results[log_measure][mod_measure] = ill + " (κ̂ = " + str(round(conditioning['kappa_hat'], decimals)) + ")"
                    # STABILITY ANALYSIS
                    # analyze stability only if the analysis was not performed already
                    if mod_measure not in ignore_mod_measures and not stability_computed:
                        stability = complexity_stability.stability(list(distance_data['dm'].values))
                        if stability > 0.66:
                            stability_results[mod_measure] = ill + " (ϵ = " + str(round(stability, decimals)) + ")"
                        elif stability > 0.33:
                            stability_results[mod_measure] = moderately + " (ϵ = " + str(round(stability, decimals)) + ")"
                        else:
                            stability_results[mod_measure] = well + " (ϵ = " + str(round(stability, decimals)) + ")"
            stability_computed = True
            print()
    return conditioning_results, stability_results

def perform_bulk_analysis():
    miner = ask_user_for_discovery_algorithm()
    noise_type = ask_user_for_noise_type()
    print("Results for discovery algorithm", miner, "and noise type", noise_type + ":")
    c_results, s_results = perform_analysis_for_discovery_algorithm_and_noise_type(miner, noise_type)
    print("Conditioning for " + miner + " miner with noise type " + noise_type + ":")
    pretty_print_two_dimensional_results(c_results)
    print("Stability for " + miner + " miner with noise type " + noise_type + ":")
    pretty_print_one_dimensional_results(s_results)

def perform_regression_analysis():
    log_csv = "log_complexity_scores.csv"
    mod_csv = "model_complexity_scores.csv"
    log_measure = ask_user_for_log_measure()
    mod_measure = ask_user_for_model_measure()
    miner = ask_user_for_discovery_algorithm()
    print("Result of a linear regression analysis for event logs without noise:")
    report = regression_analysis.perform_regression_analysis(log_csv, mod_csv, log_measure, mod_measure, miner)
    for info in report.keys():
        print(info + ": " + str(report[info]))
    for noise_type in noise_types:
        print("Result of a linear regression analysis for event logs with noise type " + str(noise_type) + ":")
        report = regression_analysis.perform_regression_analysis(log_csv, mod_csv, log_measure, mod_measure, miner, noise_type)
        for info in report.keys():
            print(info + ": " + str(report[info]))

def compare_regression_analysis():
    log_csv = "log_complexity_scores.csv"
    mod_csv = "model_complexity_scores.csv"
    log_measure = ask_user_for_log_measure()
    mod_measure = ask_user_for_model_measure()
    miner = ask_user_for_discovery_algorithm()
    noise_type = ask_user_for_noise_type()
    noise_ratio = ask_user_for_noise_ratio()
    regression_analysis.compare_linear_regression_with_noise(log_csv, mod_csv, log_measure, mod_measure, miner, noise_type, noise_ratio)

if __name__ == "__main__":
    print("Welcome to the complexity conditioning part of anaLOG.")
    print("Use this program to find statistical relations between log and model complexity.")
    single_complexity_conditioning = "Calculate the complexity conditioning of a discovery algorithm for a log and model complexity measure."
    bulk_complexity_conditioning = "Calculate the complexity conditioning of a discovery algorithm for all log and model complexity measures."
    do_regression_analysis = "Compare regression analyses on noisy and non-noisy event logs."

    mode = questionary.select("Please select what you want to do.", choices=[single_complexity_conditioning, bulk_complexity_conditioning, do_regression_analysis]).ask()
    if mode == single_complexity_conditioning:
        perform_specialized_analysis()
    elif mode == bulk_complexity_conditioning:
        perform_bulk_analysis()
    elif mode == do_regression_analysis:
        compare_regression_analysis()
    else:
        raise Exception("Unexpected user-choice: " + mode)
