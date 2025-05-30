from pm4py.objects.petri_net.obj import PetriNet, Marking # for creating marked Petri nets


class ModelWrapper:
    def __init__(self, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking):
        self.net = petri_net
        self.initial_marking = initial_marking
        self.final_marking = final_marking