"""Domain models for individual sequence components.

Every piece of a Golden Gate fragment is represented as a *SequenceComponent*
subclass so the assembly engine can treat them uniformly while the validation
layer can apply type-specific rules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ComponentType(str, Enum):
    """Enumeration of sequence component roles."""

    ADAPTER_5P = "5' Adapter"
    ADAPTER_3P = "3' Adapter"
    OVERHANG = "Overhang"
    VARIABLE_DOMAIN = "Variable Domain"
    FILLER = "Filler"


@dataclass
class SequenceComponent:
    """Base class for all sequence building-blocks.

    Attributes:
        sequence: The nucleotide sequence (uppercase).
        name: Human-readable label.
        component_type: Role inside the fragment.
        id: Unique identifier (auto-generated).
    """

    sequence: str
    name: str
    component_type: ComponentType
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        self.sequence = self.sequence.upper().strip()

    def __len__(self) -> int:
        return len(self.sequence)

    @property
    def length(self) -> int:
        return len(self.sequence)


@dataclass
class Adapter(SequenceComponent):
    """Fixed adapter flanking a fragment (5' or 3')."""

    def __init__(
        self,
        sequence: str,
        name: str = "",
        *,
        is_5_prime: bool = True,
        id: Optional[str] = None,
    ) -> None:
        comp_type = ComponentType.ADAPTER_5P if is_5_prime else ComponentType.ADAPTER_3P
        super().__init__(
            sequence=sequence,
            name=name or comp_type.value,
            component_type=comp_type,
            id=id or uuid.uuid4().hex[:12],
        )


@dataclass
class Overhang(SequenceComponent):
    """Golden Gate overhang (typically 4 bp)."""

    position: str = "5'"  # "5'" or "3'" relative to the variable domain

    def __init__(
        self,
        sequence: str,
        name: str = "",
        *,
        position: str = "5'",
        id: Optional[str] = None,
    ) -> None:
        super().__init__(
            sequence=sequence,
            name=name or f"Overhang ({position})",
            component_type=ComponentType.OVERHANG,
            id=id or uuid.uuid4().hex[:12],
        )
        self.position = position


@dataclass
class VariableDomain(SequenceComponent):
    """User-defined variable region of a fragment."""

    description: str = ""

    def __init__(
        self,
        sequence: str,
        name: str = "Variable Domain",
        *,
        description: str = "",
        id: Optional[str] = None,
    ) -> None:
        super().__init__(
            sequence=sequence,
            name=name,
            component_type=ComponentType.VARIABLE_DOMAIN,
            id=id or uuid.uuid4().hex[:12],
        )
        self.description = description


@dataclass
class FillerSequence(SequenceComponent):
    """Padding sequence used to bring short fragments up to minimum length."""

    def __init__(
        self,
        sequence: str,
        name: str = "Filler",
        *,
        id: Optional[str] = None,
    ) -> None:
        super().__init__(
            sequence=sequence,
            name=name,
            component_type=ComponentType.FILLER,
            id=id or uuid.uuid4().hex[:12],
        )
