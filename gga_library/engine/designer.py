"""Fragment design engine.

Responsible for assembling FragmentTemplate objects from user inputs and
assigning filler sequences when needed.  Keeps all construction logic out
of the UI layer.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from gga_library.config.constants import DEFAULT_CONFIG, AppConfig
from gga_library.models.components import (
    Adapter,
    FillerSequence,
    Overhang,
    VariableDomain,
)
from gga_library.models.fragment import FragmentTemplate
from gga_library.models.library import FragmentLibrary
from gga_library.validation.validator import SequenceValidator, ValidationResult


class FragmentDesigner:
    """Builds and manages fragment templates.

    The designer is the main entry-point for programmatic fragment
    construction.  It delegates validation to :class:`SequenceValidator`
    and keeps a running :class:`FragmentLibrary`.
    """

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        validator: Optional[SequenceValidator] = None,
    ) -> None:
        self.config = config or DEFAULT_CONFIG
        self.validator = validator or SequenceValidator()
        self.library = FragmentLibrary()

    # ------------------------------------------------------------------ #
    # Fragment creation
    # ------------------------------------------------------------------ #

    def create_fragment(
        self,
        name: str,
        adapter_5p_seq: str,
        overhang_5p_seq: str,
        variable_domains: List[Dict[str, str]],
        overhang_3p_seq: str,
        adapter_3p_seq: str,
        notes: str = "",
    ) -> FragmentTemplate:
        """Build a new fragment template from raw sequences.

        Parameters
        ----------
        variable_domains:
            List of dicts each having ``name`` and ``sequence`` keys.
        """
        vds = [
            VariableDomain(
                sequence=vd["sequence"],
                name=vd.get("name", "Variable Domain"),
                description=vd.get("description", ""),
            )
            for vd in variable_domains
        ]
        fragment = FragmentTemplate(
            name=name,
            adapter_5p=Adapter(adapter_5p_seq, is_5_prime=True),
            overhang_5p=Overhang(overhang_5p_seq, position="5'"),
            variable_domains=vds,
            overhang_3p=Overhang(overhang_3p_seq, position="3'"),
            adapter_3p=Adapter(adapter_3p_seq, is_5_prime=False),
            notes=notes,
        )
        self.library.add(fragment)
        return fragment

    # ------------------------------------------------------------------ #
    # Filler assignment
    # ------------------------------------------------------------------ #

    def assign_fillers(
        self,
        filler_pool: List[FillerSequence],
    ) -> ValidationResult:
        """Assign unique fillers to fragments that need padding.

        Returns validation result with any warnings/errors.
        """
        result = ValidationResult()
        needy = [f for f in self.library.fragments if f.needs_filler]

        # Validate pool
        pool_result = self.validator.validate_filler_pool(filler_pool, len(needy))
        result.messages.extend(pool_result.messages)

        available = list(filler_pool)  # copy so we can pop
        for frag in needy:
            if not available:
                result.add(
                    "error",
                    f"[{frag.name}] No unique filler available.",
                    frag.id,
                )
                continue

            needed_bp = frag.filler_needed_bp
            # Pick first filler whose length is >= needed_bp
            chosen: Optional[FillerSequence] = None
            chosen_idx: Optional[int] = None
            for i, fs in enumerate(available):
                if fs.length >= needed_bp:
                    chosen = fs
                    chosen_idx = i
                    break

            if chosen is None or chosen_idx is None:
                # Pick the longest remaining if none is long enough
                if available:
                    best_idx = max(range(len(available)), key=lambda i: available[i].length)
                    chosen = available[best_idx]
                    chosen_idx = best_idx
                    trimmed_seq = chosen.sequence[:needed_bp] if needed_bp else ""
                    result.add(
                        "warning",
                        f"[{frag.name}] Longest available filler ({chosen.length} bp) "
                        f"is shorter than needed ({needed_bp} bp). Using it anyway.",
                        frag.id,
                    )
                    frag.filler = FillerSequence(trimmed_seq, name=chosen.name)
                    available.pop(chosen_idx)
                    continue
                else:
                    result.add("error", f"[{frag.name}] No filler available.", frag.id)
                    continue

            # Trim filler to exactly the needed length
            trimmed = chosen.sequence[:needed_bp]
            frag.filler = FillerSequence(trimmed, name=chosen.name)
            available.pop(chosen_idx)

        return result

    # ------------------------------------------------------------------ #
    # Library convenience
    # ------------------------------------------------------------------ #

    def remove_fragment(self, fragment_id: str) -> None:
        self.library.remove(fragment_id)

    def clone_fragment(self, fragment_id: str) -> Optional[FragmentTemplate]:
        original = self.library.get(fragment_id)
        if original is None:
            return None
        copy = original.clone()
        self.library.add(copy)
        return copy

    def validate_all(self) -> ValidationResult:
        return self.validator.validate_library(self.library)
