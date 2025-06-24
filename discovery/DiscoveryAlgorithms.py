import pm4py
from discovery import BaselineMiners, DirectlyFollowsMiner, DirectlyFollowsGraph

class FlowerModelMiner:
    name = "Flower model"

    def __str__(self):
        return self.name

    def discover_for(self, event_log):
        net, im, fm = BaselineMiners.flower_miner(event_log)
        return net, im, fm

class TraceNetMiner:
    name = "Trace net"

    def __str__(self):
        return self.name

    def discover_for(self, event_log):
        net, im, fm = BaselineMiners.trace_net_miner(event_log)
        return net, im, fm

class AlphaMiner:
    name = "Alpha miner"

    def __str__(self):
        return self.name

    def discover_for(self, event_log):
        net, im, fm = pm4py.discover_petri_net_alpha(event_log)
        return net, im, fm

class DirectlyFollowsGraphMiner:
    name = "Directly follows graph"

    def __str__(self):
        return self.name

    def discover_for(self, event_log):
        graph = DirectlyFollowsGraph.DirectlyFollowsGraph(event_log)
        return graph, None, None

class DirectlyFollowsModelMiner:
    name = "Directly follows miner"

    def __str__(self):
        return self.name

    def discover_for(self, event_log):
        net, im, fm = DirectlyFollowsMiner.directly_follows_miner(event_log)
        return net, im, fm

# To add more discovery algorithms:
# 1. Create a class like the ones above. Its attributes should include "name", which is a descriptive name of
#    the discovery algorithm, shown when the user can choose the discovery algorithm they want to investigate.
#    Furthermore, your class must implement the functions __str__ (returning the name of the discovery algorithm)
#    and discover_for, which takes an event log and returns the model discovered by the discovery algorithm.
#    The result must consist of a net, an initial marking, and a final marking. If the latter two do not exist,
#    set them to None.
# 2. Add an instance of your new class to the following list of all discovery algorithms

all_discovery_algorithms = [FlowerModelMiner(), TraceNetMiner(), AlphaMiner(), DirectlyFollowsGraphMiner(), DirectlyFollowsModelMiner()]