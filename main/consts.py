class Consts(object):
    svo_descriptors_set = ("amod", "acomp", "aux", "auxpass", "neg", "prep")
    participant_descriptors_set = ("amod", "acomp", "aux", "auxpass", "compound", "det", "neg", "poss")
    conditional_keywords = ["if", "whether", "whenever"]
    default_flow_keywords = ["otherwise"]
    parallel_keywords = ["while"]
    gateways_keywords = conditional_keywords + default_flow_keywords + parallel_keywords
