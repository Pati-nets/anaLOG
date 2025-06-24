from logcomplexity import Complexity as LogComplexity
from logcomplexity import MoreLogComplexity

class Magnitude:
    name = "Magnitude"
    abbreviation = "mag"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        return LogComplexity.measure_magnitude(event_log, quiet=True)

class Variety:
    name = "Variety"
    abbreviation = "var"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        return LogComplexity.measure_variety(event_log, quiet=True)

class Support:
    name = "Support / Length"
    abbreviation = "supp"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        return LogComplexity.measure_support(event_log, quiet=True)

class AverageTraceLength:
    name = "Average trace length"
    abbreviation = "TL-avg"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        trace_length = LogComplexity.measure_trace_length(event_log, quiet=True)
        return round(trace_length["avg"], decimals)

class MaximumTraceLength:
    name = "Maximum trace length"
    abbreviation = "TL-max"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        trace_length = LogComplexity.measure_trace_length(event_log, quiet=True)
        return trace_length["max"]

class LevelOfDetail:
    name = "Level of detail"
    abbreviation = "LOD"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        return MoreLogComplexity.measure_number_of_transition_paths(event_log)

class NumberOfTies:
    name = "Number of ties"
    abbreviation = "t-comp"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        return round(MoreLogComplexity.measure_number_of_ties(event_log), decimals)

class LempelZiv:
    name = "Lempel-Ziv complexity"
    abbreviation = "LZ"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        plain_log = LogComplexity.generate_log(event_log)
        return LogComplexity.measure_lempel_ziv(plain_log, quiet=True)

class NumberOfDistinctTraces:
    name = "Number of distinct traces"
    abbreviation = "DT-#"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log):
        support = LogComplexity.measure_support(event_log, quiet=True)
        distinct_trace_percentage = LogComplexity.measure_distinct_traces(event_log, quiet=True) / 100
        return round(distinct_trace_percentage * support)

class PercentageOfDistinctTraces:
    name = "Percentage of distinct traces"
    abbreviation = "DT-%"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        distinct_trace_percentage = LogComplexity.measure_distinct_traces(event_log, quiet=True) / 100
        return round(distinct_trace_percentage, decimals)

class Structure:
    name = "Structure"
    abbreviation = "struct"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        # In the code of Vidgof et al., the calculation of the level of detail corresponds to the definition
        # of the structure, which is why we return the result of the level of detail.
        return round(LogComplexity.measure_level_of_detail(event_log, quiet=True), decimals)

class Affinity:
    name = "Affinity"
    abbreviation = "affinity"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        affinity = LogComplexity.measure_affinity(event_log, quiet=True)
        if affinity is None:
            # Affinity can become None if there is only a single trace in the event log.
            # In this case, rounding the result is not possible.
            return affinity
        else:
            return round(affinity, decimals)

class DeviationFromRandom:
    name = "Deviation from random"
    abbreviation = "dev-R"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        plain_log = LogComplexity.generate_log(event_log)
        deviation_from_random = LogComplexity.measure_deviation_from_random(plain_log, event_log, quiet=True)
        if deviation_from_random is None:
            # Deviation from random can become None if all traces consist of at most one event name.
            # In this case, rounding the result is not possible.
            return deviation_from_random
        else:
            return round(deviation_from_random, decimals)

class AverageEditDistance:
    name = "Average edit distance"
    abbreviation = "avg-dist"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        return round(MoreLogComplexity.measure_average_edit_distance(event_log), decimals)

class VariantEntropy:
    name = "Variant entropy"
    abbreviation = "var-e"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        plain_log = LogComplexity.generate_log(event_log)
        epa = LogComplexity.build_graph(plain_log)
        return round(LogComplexity.graph_complexity(epa)[0], decimals)

class NormalizedVariantEntropy:
    name = "Normalized variant entropy"
    abbreviation = "nvar-e"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        plain_log = LogComplexity.generate_log(event_log)
        epa = LogComplexity.build_graph(plain_log)
        return round(LogComplexity.graph_complexity(epa)[1], decimals)

class SequenceEntropy:
    name = "Sequence Entropy"
    abbreviation = "seq-e"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        plain_log = LogComplexity.generate_log(event_log)
        epa = LogComplexity.build_graph(plain_log)
        return round(LogComplexity.log_complexity(epa)[0], decimals)

class NormalizedSequenceEntropy:
    name = "Normalized sequence entropy"
    abbreviation = "nseq-e"

    def __str__(self):
        return self.name

    def calculate_for(self, event_log, decimals=8):
        plain_log = LogComplexity.generate_log(event_log)
        epa = LogComplexity.build_graph(plain_log)
        return round(LogComplexity.log_complexity(epa)[1], decimals)


# To add more log complexity measures:
# 1. Create a class like the ones above. Its attributes should include "name", which is a descriptive name of
#    the log complexity measure, shown when the user can choose log complexity measures, and "abbreviation",
#    which is a short name for the measure shown in the tables of the analysis. Furthermore, your class must
#    implement the functions __str__ (returning the name of the measure) and calculate_for, which takes an
#    event log and calculates the result of your measure for this log.
# 2. Add an instance of your new class to the following list of all log complexity measures.

all_log_complexity_measures = [Magnitude(), Variety(), Support(), AverageTraceLength(), MaximumTraceLength(),
                               LevelOfDetail(), NumberOfTies(), LempelZiv(), NumberOfDistinctTraces(),
                               PercentageOfDistinctTraces(), Structure(), Affinity(), DeviationFromRandom(),
                               AverageEditDistance(), VariantEntropy(), NormalizedVariantEntropy(),
                               SequenceEntropy(), NormalizedSequenceEntropy()]