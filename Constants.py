from pathlib import Path

# constants for storing output files
OUTPUT_PATH = "./output/"
prom4py_script_path = Path('/home/schalk/ProM/prom4py/ProM4Py/ProM4Py.sh')

# constants for measure calculation timeouts and abort behavior
timeout_seconds = 5
abort_key = {"code": '\x18', "label": 'Ctrl+X'}

# constants for handling event logs
case_specifier = 'case:concept:name'
activity_specifier = 'concept:name'
timestamp_specifier = 'time:timestamp'

# constants for printing on command line with color
SUCCESS_COLOR = "\033[92m"
FAILURE_COLOR = "\033[91m"
RESET_COLOR = "\x1b[0m"

# constants for links to papers
arxive_link = "https://doi.org/10.48550/arXiv.2505.23233"
paper_hybrid_ilp_miner = "https://doi.org/10.1007/s00607-017-0582-5"
