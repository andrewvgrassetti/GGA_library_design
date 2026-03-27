"""Fragment library model – a collection of FragmentTemplate objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gga_library.models.fragment import FragmentTemplate


@dataclass
class FragmentLibrary:
    """Container for all fragment designs in one session.

    Provides lookup by id, duplicate-name detection, and bulk operations.
    """

    name: str = "Untitled Library"
    _fragments: Dict[str, FragmentTemplate] = field(default_factory=dict)

    # -- CRUD -------------------------------------------------------------- #

    def add(self, fragment: FragmentTemplate) -> None:
        """Add a fragment to the library."""
        self._fragments[fragment.id] = fragment

    def remove(self, fragment_id: str) -> None:
        """Remove a fragment by its ID."""
        self._fragments.pop(fragment_id, None)

    def get(self, fragment_id: str) -> Optional[FragmentTemplate]:
        """Retrieve a single fragment by ID."""
        return self._fragments.get(fragment_id)

    def update(self, fragment: FragmentTemplate) -> None:
        """Replace an existing fragment (matched by id)."""
        self._fragments[fragment.id] = fragment

    # -- Queries ----------------------------------------------------------- #

    @property
    def fragments(self) -> List[FragmentTemplate]:
        """All fragments in insertion order."""
        return list(self._fragments.values())

    @property
    def size(self) -> int:
        return len(self._fragments)

    @property
    def names(self) -> List[str]:
        return [f.name for f in self._fragments.values()]

    def has_duplicate_names(self) -> List[str]:
        """Return list of names that appear more than once."""
        seen: Dict[str, int] = {}
        for n in self.names:
            seen[n] = seen.get(n, 0) + 1
        return [n for n, count in seen.items() if count > 1]

    def clear(self) -> None:
        self._fragments.clear()

    def to_list_of_dicts(self) -> List[dict]:
        return [f.to_dict() for f in self.fragments]
