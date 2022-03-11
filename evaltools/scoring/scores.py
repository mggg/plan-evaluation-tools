from .splits import _splits, _pieces
from .demographics import (
    _pop_shares,
    _tally_pop,
    _gingles_districts,
    _max_deviation,
)
from .partisan import (
    _competitive_contests,
    _swing_districts,
    _party_districts,
    _opp_party_districts,
    _party_wins_by_district,
    _seats,
    _efficiency_gap,
    _simplified_efficiency_gap,
    _mean_median,
    _partisan_bias,
    _partisan_gini,
    _eguia,
    _absolute_proportionality,
    _signed_proportionality,
)
from functools import partial
from gerrychain import Partition, Graph
from typing import Iterable, List, Mapping, Dict, Union, Any
import gzip
import json
from .score_types import *

"""
    Functionality for scoring plans/chains
"""

def summarize(part: Partition, scores: Iterable[Score]) -> Dict[str, ScoreValue]:
    """
    Summarize the given partition by the passed scores.

    Args:
        part (Partition): The plan to summarize.
        scores (Iterable[Score]): Which scores to include in the summary.

    Returns:
        A dictionary that maps score names to the corresponding ScoreValues of the score functions
        applied to the plan.

        ie.
        `{"cut_edges": 4050, "num_party_seats": 3, ... }`
    """
    summary = {}
    for score in scores:
        summary[score.name] = score.apply(part)
    return summary

def summarize_many(parts: Iterable[Partition], scores: Iterable[Score], plan_names: List[str] = [],
                   output_file: str = None, compress: bool = False) -> Union[List[Dict[str, ScoreValue]], None]:
    """
    Summarize the given partitions by the passed scores.

    Args:
        parts (Iterable[Partition]): The plans to summarize.
        scores (Iterable[Score]): Which scores to include in the summaries.
        plan_names (Iterable[str], optional): Plan identifiers, corresponding to plan by index.  If
            no plan name exist for a given plan's index the plan's index is used as the identifier.
            Default is `[]`, plans identified by index.
        output_file (str, optional): Name of file to save the results jsonl encoding of the scores.
            If None, returns a list of the dictionary summary of each plan.  Defaults to None.
        compress (bool, optional): Whether to compress the output file with gzip.  Default is False.

    Returns:
        A list dictionaries that maps score names to the corresponding ScoreValues of the score
        functions applied to each plan, if NO output file is passed.

        If an output file IS specified, the plan summaries are written to file and the function
        is void.
    """
    if output_file is None:
        return [summarize(part, scores=scores) for part in parts]
    else:
        with gzip.open(f"{output_file}.gz", "wt") if compress else open(output_file, "w") as fout:
            for i, part in enumerate(parts):
                plan_details = summarize(part, scores=scores)
                try:
                    plan_details["id"] = plan_names[i]
                except:
                    plan_details["id"] = i
                fout.write(json.dumps(plan_details) + "\n")

"""
    Commonly used score definitions
"""

def splits(
        unit:str, names:bool=False, popcol:str=None, how:str="pandas",
        alias:str=None
    ) -> Score:
    """
    Score representing the number of units split by the districting plan.
    
    Bear in mind that this calculates the number of *unit splits*, not the number
    of *units split*: for example, if a district divides a county into three
    pieces, the former reports two splits (as a unit divided into three pieces is
    cut twice), while the latter would report one split (as there is one county 
    being split).

    Args:
        unit (str): Data column; each assigns a vertex to a unit.
            Generally, these units are counties, VTDs, precincts, etc.
        popcol (str, optional): The population column on the `Partition`'s dual
            graph. If this is passed, then a unit is only considered "split" if
            the _populated_ base units end up in different districts.
        how (str, optional): How do we perform these calculations on the back
            end? Acceptable values are `"pandas"` and `"gerrychain"`; defaults to
            `"pandas"`.
        names (bool, optional): Whether we return the identifiers of the things
            being split.
    
    Returns:
        A score object with the name `"{alias}_splits"` and associated function that takes a
        partition and returns a PlanWideScoreValue for the number of splits.
    """
    if alias is None: alias = unit
    
    return Score(
        f"{alias}_splits",
        partial(_splits, unit=unit, how=how, popcol=popcol, names=names)
    )

def pieces(
        unit:str, names:bool=False, popcol:str=None, how:str="pandas",
        alias:str=None
    ) -> Score:
    """
    Score representing the number of "unit pieces" produced by the plan. For example,
    consider a state with 100 counties. Suppose that one county is split twice,
    and another once. Then, there are 3 + 2 = 5 "pieces," disregarding the
    counties kept whole.
    
    Bear in mind that this calculates the number of _unit splits_, not the number
    of _units split_: for example, if a district divides a county into three
    pieces, the former reports two splits (as a unit divided into three pieces is
    cut twice), while the latter would report one split (as there is one county 
    being split).

    Args:
        unit (str): Data column; each assigns a vertex to a unit.
            Generally, these units are counties, VTDs, precincts, etc.
        popcol (str, optional): The population column on the `Partition`'s dual
            graph. If this is passed, then a unit is only considered "split" if
            the _populated_ base units end up in different districts.
        how (str, optional): How do we perform these calculations on the back
            end? Acceptable values are `"pandas"` and `"gerrychain"`; defaults to
            `"pandas"`.
        names (bool, optional): Whether we return the identifiers of the things
            being split.
    
    Returns:
        A score object with the name `"{alias}_pieces"` and associated function that takes a
        partition and returns a PlanWideScoreValue for the number of pieces.
    """
    if alias is None: alias = unit
    
    return Score(
        f"{alias}_pieces",
        partial(_pieces, unit=unit, how=how, popcol=popcol, names=names)
    )

def competitive_contests(election_cols: Iterable[str], party: str, points_within: float = 0.03) -> Score:
    """
    Score representing the number of competitive contests in a plan.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        points_within (float, optional): The margin from 0.5 that is considered competitive.
            Default is 0.03, corresponding to a competitive range of 47%-53%.
    
    Returns:
        A score object with name `"competitive_contests_0.03"` and associated function that takes a
        partition and returns a PlanWideScoreValue for the number of competitive districts.
    """
    if alias is None:
        alias = f"competitive_contests_{points_within}"
    return Score(alias, partial(_competitive_contests, election_cols=election_cols,
                                                  party=party, points_within=points_within))

def swing_districts(election_cols: Iterable[str], party: str) -> Score:
    """
    Score representing the number of swing districts in a plan.  A swing districts is one that is
    not solely won by a single party over a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.

    Returns:
        A score object with name `"swing_districts"` and associated function that takes a partition
        and returns a PlanWideScoreValue for the number of swing districts.
    """
    return Score("swing_districts", partial(_swing_districts, election_cols=election_cols, party=party))

def party_districts(election_cols: Iterable[str], party: str) -> Score:
    """
    Score representing the number of districts in a plan that are always won by the POV party over
    a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.

    Returns:
        A score object with name `"party_districts"` and associated function that takes a partition
        and returns a PlanWideScoreValue for the number of safe POV party districts.
    """
    return Score("party_districts", partial(_party_districts, election_cols=election_cols, party=party))

def opp_party_districts(election_cols: Iterable[str], party: str) -> Score:
    """
    Score representing the number of districts in a plan that are always won by the opposition party
    over a set of elections.
    Note that this assumes that all elections are two-party races.  In the case where elections have
    more than two parties running this score represents the number of districts that are never won
    by the POV party.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.

    Returns:
        A score object with name `"opp_party_districts"` and associated function that takes a
        partition and returns a PlanWideScoreValue for the number of safe opposition party districts.
    """
    return Score("opp_party_districts", partial(_opp_party_districts, election_cols=election_cols, party=party))

def party_wins_by_district(election_cols: Iterable[str], party: str) -> Score:
    """
    Score representing how many elections the POV party won in each district in a given plan.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.

    Returns:
        A score object with name `"party_wins_by_district"` and associated function that takes a
        partition and returns a DistrictWideScoreValue for the number of elections won by the POV
        party in each district.
    """
    return Score("party_wins_by_district", partial(_party_wins_by_district, election_cols=election_cols, party=party))

def seats(election_cols: Iterable[str], party: str, mean: bool = False) -> Score:
    """
    Score representing how many seats (districts) within a given plan the POV party won in each
    election 

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"{party}_seats"` and associated function that takes a partition and
        returns an ElectionWideScoreValue for the number of seats won by the POV party for each
        election.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}{party}_seats", partial(_seats, election_cols=election_cols, party=party, mean=mean))

def signed_proportionality(election_cols: Iterable[str], party: str, mean: bool = False) -> Score:
    """
    Score representing how many the responsive proportionality across a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"signed_proportionality"` and associated function that takes a
        partition and returns an PlanWideScoreValue for the responsive proportionality across the
        elections.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}signed_proportionality", partial(_signed_proportionality, election_cols=election_cols, party=party, mean=mean))

def absolute_proportionality(election_cols: Iterable[str], party: str, mean: bool = False) -> Score:
    """
    Score representing how many the stable proportionality across a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"absolute_proportionality"` and associated function that takes a
        partition and returns an PlanWideScoreValue for the stable proportionality across the
        elections.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}absolute_proportionality", partial(_absolute_proportionality, election_cols=election_cols, party=party, mean=mean))

def efficiency_gap(election_cols: Iterable[str], mean: bool = False) -> Score:
    """
    Score representing the efficiency gap metric of a plan with respect to a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"efficiency_gap"`  and associated function that takes a partition
        and returns a PlanWideScoreValue for efficiency gap metric.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}efficiency_gap", partial(_efficiency_gap, election_cols=election_cols, mean=mean))

def simplified_efficiency_gap(election_cols: Iterable[str], party: str, mean: bool = False) -> Score:
    """
    Score representing the simplified efficiency gap metric of a plan with respect to a set of elections.
    The original formulation of efficiency gap quantifies the difference in "wasted" votes for the two
    parties across the state, as a share of votes cast. This is sensitive to turnout effects. The 
    simplified score is equal to standard efficiency gap when the districts have equal turnout.
    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.
    Returns:
        A score object with name `"efficiency_gap"`  and associated function that takes a partition
        and returns a PlanWideScoreValue for efficiency gap metric.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}simplified_efficiency_gap", partial(_simplified_efficiency_gap, election_cols=election_cols, party=party, mean=mean))

def mean_median(election_cols: Iterable[str], mean: bool = False) -> Score:
    """
    Score representing the mean median metric of a plan with respect to a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"mean_median"` and associated function that takes a partition and
        returns a PlanWideScoreValue for the mean median metric.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}mean_median", partial(_mean_median, election_cols=election_cols, mean=mean))

def partisan_bias(election_cols: Iterable[str], mean: bool = False) -> Score:
    """
    Score representing the partitisan bias metric of a plan with respect to a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.
    Returns:
        A score object with name `"partisan_bias"` and associated function that takes a partition and
        returns a PlanWideScoreValue for partisan bias metric.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}partisan_bias", partial(_partisan_bias, election_cols=election_cols, mean=mean))

def partisan_gini(election_cols: Iterable[str], mean: bool = False) -> Score:
    """
    Score representing the partisan gini metric of a plan with respect to a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"partisan_gini"` and associated function that takes a partition and
        returns a PlanWideScoreValue for the partisan gini metric.
    """
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}partisan_gini", partial(_partisan_gini, election_cols=election_cols, mean=mean))

def eguia(election_cols: Iterable[str], party: str, graph: Graph, updaters: Mapping[str, Callable[[Partition], ScoreValue]],
          county_col: str, totpop_col: str = "population", mean: bool = False) -> Score:
    """
    Score representing the Equia metric of a plan with respect to a set of elections.

    Args:
        election_cols (Iterable[str]): The names of the election updaters over which to compute
            results for.
        party (str): The "point of view" political party.
        graph (gerrychain.Graph): The underlying dual graph of a partition.  Used to generated a
            plan of the counties.
        updaters (Mapping[str, Callable[[gerrychain.Partition], ScoreValue]]):  A set of updaters
            that contains a tally for the total population by district and the election updaters
            whose names are listed in election_cols.
        county_col (str): The column name in the dual graph that encodes the county assignment of
            each unit.
        totpop_col (str, optional): The name of the updater that computes total population by
            district.
        mean (bool): Whether to return the mean of the score over all elections, or a dictionary
                     of the score for each election.

    Returns:
        A score object with name `"eguia"` and associated function that takes a partition and returns
        a PlanWideScoreValue for the eguia metric. 
    """
    county_part = Partition(graph, county_col, updaters=updaters)
    prefix = "mean_" if mean else ""
    return Score(f"{prefix}eguia", partial(_eguia, election_cols=election_cols, party=party, 
                                  county_part=county_part, totpop_col=totpop_col, mean=mean))


def demographic_tallies(population_cols: Iterable[str]) -> List[Score]:
    """
    A list of scores representing population tallies.

    Args:
        population_cols (Iterable[str]): The population column to create tallies for.

    Returns:
        A list of score objects named by `"{column}"` and with associated functions that take a partition
        and return a DistrictWideScoreValue for the demographic totals of each district.
    """
    return [
            Score(col, partial(_tally_pop, pop_col=col))
            for col in population_cols
        ]

def demographic_shares(population_cols: Mapping[str, Iterable[str]]) -> List[Score]:
    """
    A list of scores representing subgroup population shares.

    Args:
        population_cols (Mapping[str, Iterable[str]]): A mapping encoding the total population group
            divisor as well as the subgroups to create shares for.  The mapping has the format:
            { \(P\) : [ \(P_1\), \(P_2\), ..., \(P_k\)], ...} where \(P\) is the population and 
            \( P_i \subseteq P \) forall subgroups \(P_i\).

    Returns:
        A list of score objects named with the pattern `"{column}_share"` and with associated
        functions that take a partition and return a DistrictWideScoreValue for the demographic 
        share of each district.
    """
    scores = []

    for totalpop_col, subpop_cols in population_cols.items():
        scores.extend([
            Score(f"{col}_share", partial(_pop_shares, subpop_col=col, totpop_col=totalpop_col))
            for col in subpop_cols
        ])
    return scores

def gingles_districts(population_cols: Mapping[str, Iterable[str]], threshold: float = 0.5) -> List[Score]:
    """
    A list of scores representing the number of districts where a sub-population share is above
    a given threshold.  When the threshold is 50% these are commonly called Gingles' Districts.

    Args:
        population_cols (Mapping[str, Iterable[str]]): A mapping encoding the total population group
            divisor as well as the subgroups to create gingles district counters for.  The mapping
            has the format: `{ \(P\) : [ \(P_1\), \(P_2\), ..., \(P_k\)], ...}` where \(P\) is the
            population and \( P_i \subseteq P \) forall subgroups \(P_i\).

    Returns:
        A list of score objects named with the pattern `"{column}_gingles_districts"` and with
        associated functions that take a partition and return a PlanWideScoreValue for the number of
        districts above the population share threshold.
    """
    scores = []

    for totalpop_col, subpop_cols in population_cols.items():
        scores.extend([
            Score(f"{col}_gingles_districts", partial(_gingles_districts, subpop_col=col, 
                                                      totpop_col=totalpop_col, threshold=threshold))
            for col in subpop_cols
        ])
    return scores

def max_deviation(totpop_col: str, pct: bool = False) -> Score:
    """
    Returns the maximum deviation from ideal population size among all the districts.
    If `pct`, return the deviation as a percentage of ideal population size.

    Args:
        totpop_col (str, optional): The name of the updater that computes total population by
            district.
        pct (bool): Whether to return the maximum deviation as a count or as a percentage of 
                    ideal district size.
    """
    return Score(f"{totpop_col}_max_deviation", partial(_max_deviation, totpop_col=totpop_col, pct=pct))