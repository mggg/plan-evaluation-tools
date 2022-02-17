from gerrychain.updaters import Tally
from gerrychain import Partition
from typing import Iterable
from .score_types import *

def demographic_updaters(demographic_keys: Iterable[str], aliases: Iterable[str] = None):
    updaters = {}
    aliases = aliases if aliases else demographic_keys
    for (key, alias) in zip(demographic_keys, aliases):
        updaters[alias] = Tally(key, alias=alias)
    return updaters

def _tally_pop(part: Partition, pop_col: str) -> DistrictWideScoreValue:
    return part[pop_col]

def _pop_shares(part: Partition, subpop_col: str, totpop_col: str) -> DistrictWideScoreValue:
    total_pops = part[totpop_col]
    return {d: part[subpop_col][d] / pop for d, pop in total_pops.items()}

def _gingles_districts(part: Partition, subpop_col: str, totpop_col: str, threshold: float = 0.5) -> PlanWideScoreValue:
    subpop_shares = _pop_shares(part, subpop_col, totpop_col)
    return sum([share >= threshold for share in subpop_shares.values()])