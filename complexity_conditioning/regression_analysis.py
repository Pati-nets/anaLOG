import matplotlib.pyplot as plt
import numpy as np
import pandas
from sklearn.linear_model import LinearRegression

def get_complexity_scores_for_files_with_substrings(csv_to_complexity: str, measure:str, substrings: list):
    complexity_collection = pandas.read_csv(csv_to_complexity, index_col=0)
    rows_with_substrings = [row.Index for row in complexity_collection.itertuples()]
    for substring in substrings:
        rows_with_substrings = [entry for entry in rows_with_substrings if substring in entry]
    complexity_scores = dict()
    for row in rows_with_substrings:
        complexity_scores[row] = complexity_collection.loc[row][measure]
    return complexity_scores

def perform_regression_analysis(csv_to_log_complexity: str, csv_to_model_complexity: str, log_measure: str, model_measure: str, miner: str, noise_type = ""):
    if noise_type == "":
        log_complexity_scores = get_complexity_scores_for_files_with_substrings(csv_to_log_complexity, log_measure, ["000.xes"])
        mod_complexity_scores = get_complexity_scores_for_files_with_substrings(csv_to_model_complexity, model_measure, ["000_" + miner])
    else:
        log_complexity_scores = get_complexity_scores_for_files_with_substrings(csv_to_log_complexity, log_measure, ["000_" + noise_type])
        mod_complexity_scores = get_complexity_scores_for_files_with_substrings(csv_to_model_complexity, model_measure, ["000_" + noise_type, miner])
    population = []
    regressors = []
    responses = []
    for log_name in log_complexity_scores.keys():
        model_name = log_name.removesuffix(".xes") + "_" + miner + ".pnml"
        if model_name in mod_complexity_scores.keys():
            population += [log_name.removesuffix(".xes")]
            regressors += [log_complexity_scores[log_name]]
            responses += [mod_complexity_scores[model_name]]
    regressors = np.array(regressors).reshape(-1, 1) # reshape to transpose horizontal vector to vertical orientated one
    responses = np.array(responses)
    linear_regression_model = LinearRegression().fit(regressors, responses)
    coefficient = linear_regression_model.coef_[0]
    intercept = linear_regression_model.intercept_
    R_squared = linear_regression_model.score(regressors, responses)
    report = {'population-size': len(population), 'R-squared': R_squared, 'coefficient': coefficient, 'intercept': intercept}
    return report

def noisify_log_name(log_name: str, noise_type: str, noise_ratio: str):
    return log_name.removesuffix(".xes") + "_" + str(noise_type) + "_" + str(noise_ratio)

def model_name_for_log(log_name: str, miner: str):
    return log_name.removesuffix(".xes") + "_" + miner + ".pnml"

def get_noisy_log_names_with_model(log_complexity_scores, mod_complexity_scores, miner: str, noise_type: str, noise_ratio: str):
    all_log_names = [row.Index for row in log_complexity_scores.itertuples()]
    all_mod_names = [row.Index for row in mod_complexity_scores.itertuples()]
    noisy_log_names = dict()
    for log_name in all_log_names:
        noisy_log_name_prefix = noisify_log_name(log_name, noise_type, noise_ratio)
        # find the first suffix for which a noisy log and a corresponding model exists
        for round in [1,2,3,4,5]:
            noisy_log_name = noisy_log_name_prefix + "_" + str(round) + ".xes"
            if noisy_log_name in all_log_names and model_name_for_log(noisy_log_name, miner) in all_mod_names:
                noisy_log_names[log_name] = noisy_log_name
                break
    return noisy_log_names

def compare_linear_regression_with_noise(csv_to_log_complexity: str, csv_to_model_complexity: str, log_measure: str, model_measure: str, miner: str, noise_type: str, noise_ratio: str, print_full_detail=False):
    log_complexity_scores = pandas.read_csv(csv_to_log_complexity, index_col=0)
    mod_complexity_scores = pandas.read_csv(csv_to_model_complexity, index_col=0)
    noisy_log_names = get_noisy_log_names_with_model(log_complexity_scores, mod_complexity_scores, miner, noise_type, noise_ratio)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    # 1. create a linear regression model for the event logs without any noise.
    population_no_noise = []
    regressors_no_noise = []
    responses_no_noise = []
    for log_name in noisy_log_names.keys():
        # generate the model name from the name of the event log
        model_name = model_name_for_log(log_name, miner)
        population_no_noise += [log_name.removesuffix(".xes")]
        regressors_no_noise += [log_complexity_scores.loc[log_name][log_measure]]
        responses_no_noise += [mod_complexity_scores.loc[model_name][model_measure]]
    regressors = np.array(regressors_no_noise).reshape(-1,1)
    responses = np.array(responses_no_noise)
    linear_regression_model = LinearRegression().fit(regressors, responses)
    predictions = linear_regression_model.predict(regressors)
    axis = axes.flat[0]
    axis.set_title("Without noise")
    axis.scatter(regressors, responses, label="data points")
    axis.plot(regressors, predictions, color="red", label="regression line")
    axis.set_xlabel("log complexity: " + str(log_measure))
    axis.set_ylabel("model complexity: " + str(model_measure))
    axis.legend()
    print("Linear regression line without noise: ")
    R_squared = linear_regression_model.score(regressors, responses)
    m = linear_regression_model.coef_[0]
    b = linear_regression_model.intercept_
    print(str(m) + " * x + " + str(b))
    print("R squared: " + str(R_squared))
    print()

    population_with_noise = []
    regressors_with_noise = []
    responses_with_noise = []
    for log_name in noisy_log_names.keys():
        noisy_log_name = noisy_log_names[log_name]
        noisy_model_name = model_name_for_log(noisy_log_name, miner)
        population_with_noise += [noisy_log_name.removesuffix(".xes")]
        regressors_with_noise += [log_complexity_scores.loc[noisy_log_name][log_measure]]
        responses_with_noise += [mod_complexity_scores.loc[noisy_model_name][model_measure]]
    regressors = np.array(regressors_with_noise).reshape(-1, 1)
    responses = np.array(responses_with_noise)
    linear_regression_model = LinearRegression().fit(regressors, responses)
    predictions = linear_regression_model.predict(regressors)
    axis = axes.flat[1]
    axis.set_title("With noise type " + str(noise_type) + " and noise ratio " + str(noise_ratio))
    axis.scatter(regressors, responses, label="data points")
    axis.plot(regressors, predictions, color="red", label="regression line")
    axis.set_xlabel("log complexity: " + str(log_measure))
    axis.set_ylabel("model complexity: " + str(model_measure))
    axis.legend()
    print("Linear regression line with noise: ")
    m = linear_regression_model.coef_[0]
    b = linear_regression_model.intercept_
    R_squared = linear_regression_model.score(regressors, responses)
    print(str(m) + " * x + " + str(b))
    print("R squared: " + str(R_squared))

    if print_full_detail:
        for log_name in noisy_log_names.keys():
            model_name = model_name_for_log(log_name, miner)
            data_point = (log_complexity_scores.loc[log_name][log_measure].item(), mod_complexity_scores.loc[model_name][model_measure].item())
            noisy_log_name = noisy_log_names[log_name]
            noisy_model_name = model_name_for_log(noisy_log_name, miner)
            noisy_data_point = (log_complexity_scores.loc[noisy_log_name][log_measure].item(), mod_complexity_scores.loc[noisy_model_name][model_measure].item())
            print(str(log_name) + ": ")
            print("Point prior to noise injection: " + str(data_point))
            print("Point after the noise injection: " + str(noisy_data_point))
            print()

    plt.tight_layout()
    plt.show()
