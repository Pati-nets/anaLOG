import networkx
from logcomplexity import Complexity as LogComplexity

case_specifier = 'case:concept:name'
activity_specifier = 'concept:name'
timestamp_specifier = 'time:timestamp'

def measure_number_of_ties(pm4py_log):
    """
    Counts the amount of directly follows relations in the transition matrix.
    For example, for the event log [<a,b,c,d>, <a,c,b,d>], we obtain the transition matrix:
      | a  | b  | c  | d
    ----------------------
    a | #  | -> | -> | #
    b | <- | #  | || | ->
    c | <- | || | #  | ->
    d | #  | <- | <- | #
    This transition matrix contains the directly follows relation "->" exactly 4 times,
    so the number of ties is 4.
    :param pm4py_log: An event log in pm4py-format
    :return: The number of directly follows relations in the event log
    """
    # define symbols for the causal footprint relations
    follows = '->' # e1 is followed by e2 in some trace, but e2 is never followed by e1 in a trace
    precedes = '<-' # e2 is followed by e1 in some trace, but e1 is never followed by e2 in a trace
    parallel = '||' # e1 is followed by e2 in some trace, and e2 is followed by e1 in some trace
    incomparable = '#' # e1 is never followed by e2 in a trace, and e2 is never followed by e1 in a trace
    # calculate the set of events
    events = set()
    events_per_case = LogComplexity.aux_event_classes(pm4py_log)
    for case in events_per_case.keys():
        events = events.union(events_per_case[case])
    # initialize the causal footprint with only 'incomparable'-entries
    causal_footprint = {}
    for event in events:
        causal_footprint[event] = {}
        for other_event in events:
            causal_footprint[event][other_event] = incomparable
    # enrich the causal footprint with the correct relations between events
    for trace in pm4py_log:
        for i in range(len(trace)-1):
            e1 = trace[i][activity_specifier]
            e2 = trace[i+1][activity_specifier]
            if e1 == e2:
                causal_footprint[e1][e2] = parallel
            elif causal_footprint[e1][e2] == precedes:
                causal_footprint[e1][e2] = parallel
                causal_footprint[e2][e1] = parallel
            elif causal_footprint[e1][e2] == incomparable:
                causal_footprint[e1][e2] = follows
                causal_footprint[e2][e1] = precedes
    # count the number of follows relations in the causal footprint
    number_of_ties = 0
    for event1 in events:
        for event2 in events:
            if causal_footprint[event1][event2] == follows:
                number_of_ties += 1
    return number_of_ties

def measure_number_of_transition_paths(pm4py_log):
    """
    Calculates the amount of acyclic paths in the directly follows
    graph induced by this event log. To do so, this method creates
    a networkx with a node for each event and two special nodes that
    mark the start and the end of the traces. It adds edges between
    two nodes e1 and e2, if e1 is ever followed by e2 in the event log.
    Then, this method calls a function provided by networkx to calculate
    all simple paths in the network and returns the amount of solutions.
    :param pm4py_log: An event log in pm4py-format
    :return: The number of acyclic paths in the directly follows graph of the event log
    """
    directly_follows_graph = networkx.DiGraph()
    # create two special nodes marking the start and the end of the traces
    start = "START"
    end = "END"
    directly_follows_graph.add_node(start)
    directly_follows_graph.add_node(end)
    # calculate the set of events
    events = set()
    events_per_case = LogComplexity.aux_event_classes(pm4py_log)
    for case in events_per_case.keys():
        events = events.union(events_per_case[case])
    # create a node for each event
    for event in events:
        directly_follows_graph.add_node(event)
    # add edges between nodes if the respective events are direct neighbors in some trace
    for trace in pm4py_log:
        # add an edge from the start node to the start event of this trace
        directly_follows_graph.add_edge(start, trace[0][activity_specifier])
        for i in range(len(trace)-1):
            directly_follows_graph.add_edge(trace[i][activity_specifier], trace[i+1][activity_specifier])
        # add an edge from the end event of this trace to the end node
        directly_follows_graph.add_edge(trace[-1][activity_specifier], end)
    # calculate all simple paths from the start node to the end node and return the amount of paths found this way
    return len(list(networkx.all_simple_paths(directly_follows_graph, start, end)))

def measure_average_edit_distance(pm4py_log):
    """
    Calculates the average edit distance between two traces of the event log.
    The edit distance of two words u and v is the amount of insert- and delete-operations
    needed to transform u into v. For example, to transform u = abcd into v = acbd, we would need
    to delete the first 'b' of u and insert a 'b' after the symbol 'c' of u, leading to 2 operations.
    :param pm4py_log: An event log in pm4py-format
    :return: The average edit distance between two traces in the event log
    """
    def edit_distance(trace1, trace2):
        if len(trace1) == 0:
            return len(trace2)
        elif len(trace2) == 0:
            return len(trace1)
        else:
            if trace1[0][activity_specifier] == trace2[0][activity_specifier]:
                return edit_distance(trace1[1:], trace2[1:])
            else:
                delete = edit_distance(trace1[1:], trace2)
                insert = edit_distance(trace1, trace2[1:])
                return 1 + min(delete, insert)
    edit_distance_sum = 0
    total_entries = 0
    for first_trace in pm4py_log:
        for second_trace in pm4py_log:
            if first_trace != second_trace:
                edit_distance_sum += edit_distance(first_trace, second_trace)
                total_entries += 1
    if total_entries == 0:
        return 0
    return edit_distance_sum / total_entries