from collections import defaultdict
import numpy as np


def _aggregated_vote(all_classes):
    agg_vote = defaultdict(lambda: 0)
    for leaf in all_classes:
        for key in leaf[0]:
            agg_vote[key] += leaf[0][key] * leaf[1]
    return agg_vote


def _maximum_matching(all_classes):
    max_match = defaultdict(lambda: 0)
    for leaf in all_classes:
        for key in leaf[0]:
            max_match[key] = np.maximum(max_match[key], (leaf[0][key] * leaf[1]))
    return max_match