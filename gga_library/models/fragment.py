"""Fragment template model.

A *FragmentTemplate* is the central design object – it holds an ordered list
of SequenceComponent objects that together define a single Golden Gate
fragment.  The template can assemble its full sequence, report its length,
and carry metadata such as a user-friendly name and optional notes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from gga_library.models.components import (
    Adapter,
    FillerSequence,
    Overhang,
    SequenceComponent,
    VariableDomain,
)


@dataclass
class FragmentTemplate:
    """Represents a single designed Golden Gate fragment.

    Attributes:
        name: Human-readable fragment name.
        adapter_5p: 5-prime fixed adapter.
        overhang_5p: 5-prime overhang.
        variable_domains: One or more user-variable regions.
        overhang_3p: 3-prime overhang.
        adapter_3p: 3-prime fixed adapter.
        filler: Optional filler added during design to meet minimum length.
        notes: Free-text notes.
        id: Unique identifier.
    """

    name: str
    adapter_5p: Adapter
    overhang_5p: Overhang
    variable_domains: List[VariableDomain] = field(default_factory=list)
    overhang_3p: Overhang = field(default_factory=lambda: Overhang("", position="3'"))
    adapter_3p: Adapter = field(default_factory=lambda: Adapter("", is_5_prime=False))
    filler: Optional[FillerSequence] = None
    notes: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # --------------------------------------------------------------------- #
    # Computed properties
    # --------------------------------------------------------------------- #

    @property
    def components(self) -> List[SequenceComponent]:
        """Return ordered component list (excluding filler if not set)."""
        parts: List[SequenceComponent] = [self.adapter_5p, self.overhang_5p]
        parts.extend(self.variable_domains)
        parts.append(self.overhang_3p)
        if self.filler is not None:
            parts.append(self.filler)
        parts.append(self.adapter_3p)
        return parts

    @property
    def core_length(self) -> int:
        """Length without filler."""
        return sum(
            c.length
            for c in [
                self.adapter_5p,
                self.overhang_5p,
                *self.variable_domains,
                self.overhang_3p,
                self.adapter_3p,
            ]
        )

    @property
    def full_sequence(self) -> str:
        """Concatenated sequence of all components in order."""
        return "".join(c.sequence for c in self.components)

    @property
    def total_length(self) -> int:
        return len(self.full_sequence)

    @property
    def needs_filler(self) -> bool:
        """True if the core construct is shorter than 300 bp."""
        from gga_library.config.constants import DEFAULT_CONFIG

        return self.core_length < DEFAULT_CONFIG.min_fragment_length

    @property
    def filler_needed_bp(self) -> int:
        """Number of filler bp required to reach minimum length."""
        from gga_library.config.constants import DEFAULT_CONFIG

        deficit = DEFAULT_CONFIG.min_fragment_length - self.core_length
        return max(0, deficit)

    def clone(self, new_name: Optional[str] = None) -> "FragmentTemplate":
        """Return a deep-ish copy with a new id."""
        return FragmentTemplate(
            name=new_name or f"{self.name} (copy)",
            adapter_5p=Adapter(
                self.adapter_5p.sequence,
                self.adapter_5p.name,
                is_5_prime=True,
            ),
            overhang_5p=Overhang(
                self.overhang_5p.sequence,
                self.overhang_5p.name,
                position="5'",
            ),
            variable_domains=[
                VariableDomain(vd.sequence, vd.name, description=vd.description)
                for vd in self.variable_domains
            ],
            overhang_3p=Overhang(
                self.overhang_3p.sequence,
                self.overhang_3p.name,
                position="3'",
            ),
            adapter_3p=Adapter(
                self.adapter_3p.sequence,
                self.adapter_3p.name,
                is_5_prime=False,
            ),
            filler=FillerSequence(self.filler.sequence, self.filler.name)
            if self.filler
            else None,
            notes=self.notes,
        )

    def to_dict(self) -> dict:
        """Serializable dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "adapter_5p": self.adapter_5p.sequence,
            "overhang_5p": self.overhang_5p.sequence,
            "variable_domains": [
                {"name": vd.name, "sequence": vd.sequence}
                for vd in self.variable_domains
            ],
            "overhang_3p": self.overhang_3p.sequence,
            "adapter_3p": self.adapter_3p.sequence,
            "filler": self.filler.sequence if self.filler else "",
            "full_sequence": self.full_sequence,
            "total_length": self.total_length,
            "notes": self.notes,
        }
