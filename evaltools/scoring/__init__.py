
"""
Basic functionality for evaluating districting plans.
"""

# from .splits import splits, pieces
from .scores import *
from .population import deviations, unassigned_population
from .contiguity import unassigned_units, contiguous
from .demographics import demographic_updaters

__all__ = [
    "splits",
    "pieces",
    "traversals",
    "competitive_contests",
    "swing_districts",
    "party_districts",
    "opp_party_districts",
    "party_wins_by_district",
    "seats",
    "signed_proportionality",
    "absolute_proportionality",
    "efficiency_gap",
    "simplified_efficiency_gap",
    "mean_median",
    "partisan_bias",
    "partisan_gini",
    "summarize",
    "summarize_many",
    "deviations",
    "unassigned_population",
    "unassigned_units",
    "contiguous",
    "reock",
    "polsby_popper",
    "cut_edges",
    "demographic_updaters",
    "demographic_tallies",
    "demographic_shares",
    "gingles_districts",
    "eguia",
]
