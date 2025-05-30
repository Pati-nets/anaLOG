# constants for storing output files
OUTPUT_PATH = "./output/"

# constants for handling event logs
case_specifier = 'case:concept:name'
activity_specifier = 'concept:name'
timestamp_specifier = 'time:timestamp'

# constants for printing on command line with color
SUCCESS_COLOR = "\033[92m"
FAILURE_COLOR = "\033[91m"
RESET_COLOR = "\x1b[0m"

# constants for possible mining algorithms
flower = "Flower model miner"
trace = "Trace net miner"
alpha = "Alpha miner"
dfg = "Directly follows graph miner"
dfm = "Directly follows miner"

# constants for possible model-complexity measures
size = "Size"
mismatch = "Connector Mismatch"
connhet = "Connector Heterogeneity"
crossconn = "Cross connectivity"
tokensplit = "Token split"
controlflow = "Control flow complexity"
separability = "Separability"
avgconn = "Average connector degree"
maxconn = "Maximum connector degree"
sequentiality = "Sequentiality"
depth = "Depth"
diameter = "Diameter"
cyclicity = "Cyclicity"
netconn = "Coefficient of network connectivity"
density = "Density"
duplicate = "Number of duplicate tasks"
emptyseq = "Number of empty sequence flows"

# constant for links to the paper
arxive_link = "https://doi.org/10.48550/arXiv.2505.23233"