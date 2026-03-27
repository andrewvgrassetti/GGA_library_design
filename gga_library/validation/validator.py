"""Sequence and fragment validation engine.

All validation logic lives here so it can be unit-tested independently of
the UI and reused across different entry-points (CLI, API, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from gga_library.models.components import FillerSequence, SequenceComponent
from gga_library.models.fragment import FragmentTemplate
from gga_library.models.library import FragmentLibrary
from gga_library.validation.rules import AssemblyRuleSet


@dataclass
class ValidationMessage:
    """A single validation finding."""

    level: str  # "error" | "warning" | "info"
    message: str
    fragment_id: Optional[str] = None


@dataclass
class ValidationResult:
    """Aggregated validation output."""

    messages: List[ValidationMessage] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(m.level == "error" for m in self.messages)

    @property
    def errors(self) -> List[ValidationMessage]:
        return [m for m in self.messages if m.level == "error"]

    @property
    def warnings(self) -> List[ValidationMessage]:
        return [m for m in self.messages if m.level == "warning"]

    def add(self, level: str, message: str, fragment_id: Optional[str] = None) -> None:
        self.messages.append(ValidationMessage(level, message, fragment_id))


class SequenceValidator:
    """Stateless validator that checks components, fragments, and libraries."""

    def __init__(self, rules: Optional[AssemblyRuleSet] = None) -> None:
        self.rules = rules or AssemblyRuleSet()

    # ------------------------------------------------------------------ #
    # Low-level sequence checks
    # ------------------------------------------------------------------ #

    def _check_alphabet(
        self,
        seq: str,
        result: ValidationResult,
        context: str = "",
        fragment_id: Optional[str] = None,
    ) -> None:
        invalid = set(seq.upper()) - self.rules.valid_nucleotides
        if invalid:
            result.add(
                "error",
                f"{context}Invalid nucleotide(s): {', '.join(sorted(invalid))}",
                fragment_id,
            )

    def _check_not_empty(
        self,
        seq: str,
        result: ValidationResult,
        context: str = "",
        fragment_id: Optional[str] = None,
    ) -> None:
        if not seq.strip():
            result.add("error", f"{context}Sequence is empty.", fragment_id)

    def _gc_content(self, seq: str) -> float:
        if not seq:
            return 0.0
        gc = sum(1 for c in seq.upper() if c in "GC")
        return gc / len(seq)

    def _check_gc(
        self,
        seq: str,
        result: ValidationResult,
        context: str = "",
        fragment_id: Optional[str] = None,
    ) -> None:
        if not self.rules.check_gc or self.rules.gc_range is None:
            return
        gc = self._gc_content(seq)
        lo, hi = self.rules.gc_range
        if gc < lo or gc > hi:
            result.add(
                "warning",
                f"{context}GC content {gc:.1%} outside range [{lo:.0%}–{hi:.0%}].",
                fragment_id,
            )

    def _check_forbidden_sites(
        self,
        seq: str,
        result: ValidationResult,
        context: str = "",
        fragment_id: Optional[str] = None,
    ) -> None:
        if not self.rules.check_forbidden_sites:
            return
        upper = seq.upper()
        for site in self.rules.forbidden_sites_upper:
            if site in upper:
                result.add(
                    "warning",
                    f"{context}Contains forbidden site '{site}'.",
                    fragment_id,
                )

    # ------------------------------------------------------------------ #
    # Component-level
    # ------------------------------------------------------------------ #

    def validate_component(
        self,
        comp: SequenceComponent,
        result: Optional[ValidationResult] = None,
    ) -> ValidationResult:
        result = result or ValidationResult()
        ctx = f"[{comp.name}] "
        self._check_not_empty(comp.sequence, result, ctx)
        if comp.sequence.strip():
            self._check_alphabet(comp.sequence, result, ctx)
        return result

    # ------------------------------------------------------------------ #
    # Overhang-specific
    # ------------------------------------------------------------------ #

    def validate_overhang(
        self,
        seq: str,
        result: Optional[ValidationResult] = None,
        fragment_id: Optional[str] = None,
    ) -> ValidationResult:
        result = result or ValidationResult()
        lo, hi = self.rules.overhang_length_range
        if seq and (len(seq) < lo or len(seq) > hi):
            result.add(
                "error",
                f"Overhang '{seq}' length {len(seq)} not in [{lo}, {hi}].",
                fragment_id,
            )
        return result

    # ------------------------------------------------------------------ #
    # Fragment-level
    # ------------------------------------------------------------------ #

    def validate_fragment(
        self,
        fragment: FragmentTemplate,
        result: Optional[ValidationResult] = None,
    ) -> ValidationResult:
        result = result or ValidationResult()
        fid = fragment.id
        ctx_prefix = f"[{fragment.name}] "

        # Name
        if not fragment.name.strip():
            result.add("error", "Fragment name is empty.", fid)

        # Components
        for comp in [fragment.adapter_5p, fragment.overhang_5p,
                      fragment.overhang_3p, fragment.adapter_3p]:
            self.validate_component(comp, result)

        # Overhangs length
        self.validate_overhang(fragment.overhang_5p.sequence, result, fid)
        self.validate_overhang(fragment.overhang_3p.sequence, result, fid)

        # Variable domains
        if not fragment.variable_domains:
            result.add("error", f"{ctx_prefix}No variable domains defined.", fid)
        for vd in fragment.variable_domains:
            self.validate_component(vd, result)

        # Full-sequence checks
        full = fragment.full_sequence
        if full:
            self._check_gc(full, result, ctx_prefix, fid)
            self._check_forbidden_sites(full, result, ctx_prefix, fid)

        # Length check (after filler)
        if fragment.total_length > self.rules.max_fragment_length:
            result.add(
                "error",
                f"{ctx_prefix}Total length {fragment.total_length} bp exceeds "
                f"maximum {self.rules.max_fragment_length} bp.",
                fid,
            )

        return result

    # ------------------------------------------------------------------ #
    # Library-level
    # ------------------------------------------------------------------ #

    def validate_library(self, library: FragmentLibrary) -> ValidationResult:
        result = ValidationResult()
        if library.size == 0:
            result.add("warning", "Library is empty.")
            return result

        # Per-fragment
        for frag in library.fragments:
            self.validate_fragment(frag, result)

        # Duplicate names
        dupes = library.has_duplicate_names()
        if dupes:
            result.add("error", f"Duplicate fragment names: {', '.join(dupes)}")

        return result

    # ------------------------------------------------------------------ #
    # Filler validation
    # ------------------------------------------------------------------ #

    def validate_filler_pool(
        self,
        fillers: List[FillerSequence],
        needed_count: int,
    ) -> ValidationResult:
        """Validate a pool of user-provided filler sequences."""
        result = ValidationResult()

        for f in fillers:
            self.validate_component(f, result)

        # Uniqueness within pool
        seqs = [f.sequence.upper() for f in fillers]
        if len(seqs) != len(set(seqs)):
            result.add("error", "Filler pool contains duplicate sequences.")

        if len(fillers) < needed_count:
            result.add(
                "warning",
                f"Only {len(fillers)} unique fillers available but {needed_count} "
                f"fragments need padding. Some fragments cannot get unique fillers.",
            )

        return result
