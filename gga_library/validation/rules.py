"""Assembly rules that can be applied to fragments and libraries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Optional, Tuple

from gga_library.config.constants import DEFAULT_CONFIG


@dataclass
class AssemblyRuleSet:
    """Configurable set of rules governing valid fragment design.

    The rule-set is separated from the validator so that different protocols
    (BsaI, BsmBI, custom) can each supply their own rules without touching
    the validation engine.
    """

    valid_nucleotides: FrozenSet[str] = field(
        default_factory=lambda: DEFAULT_CONFIG.valid_nucleotides
    )
    overhang_length_range: Tuple[int, int] = field(
        default_factory=lambda: (
            DEFAULT_CONFIG.min_overhang_length,
            DEFAULT_CONFIG.max_overhang_length,
        )
    )
    min_fragment_length: int = DEFAULT_CONFIG.min_fragment_length
    max_fragment_length: int = DEFAULT_CONFIG.max_fragment_length
    gc_range: Optional[Tuple[float, float]] = field(
        default_factory=lambda: (DEFAULT_CONFIG.gc_min, DEFAULT_CONFIG.gc_max)
    )
    forbidden_sites: Tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_CONFIG.forbidden_sites
    )
    check_gc: bool = True
    check_forbidden_sites: bool = True

    @property
    def forbidden_sites_upper(self) -> List[str]:
        return [s.upper() for s in self.forbidden_sites]
