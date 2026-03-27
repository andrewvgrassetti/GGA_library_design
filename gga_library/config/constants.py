"""Application-wide configuration and constants."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration.

    Centralizes all tuneable parameters so they can be changed in one place
    without touching business logic or UI code.
    """

    # --- Sequence alphabet ---------------------------------------------------
    valid_nucleotides: FrozenSet[str] = frozenset("ACGTRYSWKMBDHVN")
    valid_strict_nucleotides: FrozenSet[str] = frozenset("ACGT")

    # --- Overhang constraints ------------------------------------------------
    overhang_length: int = 4
    min_overhang_length: int = 3
    max_overhang_length: int = 6

    # --- Fragment constraints ------------------------------------------------
    min_fragment_length: int = 300
    max_fragment_length: int = 5000

    # --- GC content ----------------------------------------------------------
    gc_min: float = 0.20
    gc_max: float = 0.80

    # --- Restriction enzyme sites to flag ------------------------------------
    forbidden_sites: tuple[str, ...] = ("GGTCTC", "GAGACC", "CGTCTC", "GAGACG")

    # --- Export defaults -----------------------------------------------------
    default_export_formats: tuple[str, ...] = ("CSV", "FASTA", "JSON")

    # --- Default adapter sequences (BsaI Golden Gate) ------------------------
    default_5p_adapter: str = "GGTCTCN"
    default_3p_adapter: str = "NGAGACC"

    # --- UI ------------------------------------------------------------------
    app_title: str = "GGA Library Designer"
    page_icon: str = "🧬"


# Singleton-style default config
DEFAULT_CONFIG = AppConfig()
