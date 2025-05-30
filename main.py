import questionary # for pretty command-line selections

import Constants # (internal) strings representing the supported mining algorithms and complexity measures
import examples # (internal) examples showing which log-complexity measures are unrelated to model-complexity


def example_selector(miner: str, measure: str):
    print() # add an empty line for better readability
    examples.show_analysis_for(measure, miner)

def enter_paper_mode():
    miners = [Constants.flower, Constants.trace, Constants.alpha, Constants.dfg, Constants.dfm]
    miner = questionary.select("Which mining algorithm are you interested in?", choices=miners).ask()
    complexity_question = "Alright! What model-complexity measure do you wish to analyse?"
    measures = []
    if miner == Constants.dfg:
        measures += [Constants.size, Constants.mismatch, Constants.crossconn]
        measures += [Constants.controlflow, Constants.separability, Constants.avgconn, Constants.maxconn]
        measures += [Constants.sequentiality, Constants.depth, Constants.diameter, Constants.cyclicity]
        measures += [Constants.netconn, Constants.density]
    else:
        measures += [Constants.size, Constants.mismatch, Constants.connhet, Constants.crossconn, Constants.tokensplit]
        measures += [Constants.controlflow, Constants.separability, Constants.avgconn, Constants.maxconn]
        measures += [Constants.sequentiality, Constants.depth, Constants.diameter, Constants.cyclicity]
        measures += [Constants.netconn, Constants.density, Constants.duplicate, Constants.emptyseq]
    measure = questionary.select(complexity_question, choices=measures).ask()
    example_selector(miner, measure)

def enter_playground_mode():
    print("Playground mode is not implemented yet. Sorry!")

if __name__ == "__main__":
    print("Welcome to anaLOG: The friendly log and model analyzer.")
    print("With this tool, you can reproduce the results of the paper ")
    print("\"Mind the Gap: A Formal Investigation of the Relationship Between Log and Model Complexity\"")
    print("or analyse your own event logs.")
    print()
    paper_mode = "Reproduce the results of the paper"
    playground_mode = "Analyse my own event log"
    mode = questionary.select("What would you like to do?", choices=[paper_mode, playground_mode]).ask()
    if mode == paper_mode:
        enter_paper_mode()
    elif mode == playground_mode:
        enter_playground_mode()
    else:
        raise Exception("Unexpected user-choice: " + mode)
