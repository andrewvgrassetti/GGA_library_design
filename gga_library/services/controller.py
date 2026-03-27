"""Application controller – orchestrates designer, validator, and export.

This is the main service layer that the UI calls.  It keeps the UI thin and
allows the same logic to be re-used from a CLI or notebook.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from gga_library.config.constants import DEFAULT_CONFIG, AppConfig
from gga_library.engine.designer import FragmentDesigner
from gga_library.export.exporter import ExportService
from gga_library.models.components import FillerSequence
from gga_library.models.fragment import FragmentTemplate
from gga_library.models.library import FragmentLibrary
from gga_library.validation.validator import SequenceValidator, ValidationResult


class AppController:
    """Top-level orchestrator for the GGA Library Designer.

    Holds the designer, validator, filler pool, and export service so
    the UI only needs to interact with a single object.
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.validator = SequenceValidator()
        self.designer = FragmentDesigner(config=self.config, validator=self.validator)
        self.exporter = ExportService()
        self.filler_pool: List[FillerSequence] = []

    # -- Convenience proxies ----------------------------------------------- #

    @property
    def library(self) -> FragmentLibrary:
        return self.designer.library

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
        return self.designer.create_fragment(
            name=name,
            adapter_5p_seq=adapter_5p_seq,
            overhang_5p_seq=overhang_5p_seq,
            variable_domains=variable_domains,
            overhang_3p_seq=overhang_3p_seq,
            adapter_3p_seq=adapter_3p_seq,
            notes=notes,
        )

    def remove_fragment(self, fragment_id: str) -> None:
        self.designer.remove_fragment(fragment_id)

    def clone_fragment(self, fragment_id: str) -> Optional[FragmentTemplate]:
        return self.designer.clone_fragment(fragment_id)

    def update_fragment(self, fragment: FragmentTemplate) -> None:
        self.library.update(fragment)

    # -- Filler management ------------------------------------------------- #

    def add_filler(self, sequence: str, name: str = "") -> FillerSequence:
        fs = FillerSequence(sequence, name=name or f"Filler-{len(self.filler_pool)+1}")
        self.filler_pool.append(fs)
        return fs

    def remove_filler(self, index: int) -> None:
        if 0 <= index < len(self.filler_pool):
            self.filler_pool.pop(index)

    def assign_fillers(self) -> ValidationResult:
        # Clear existing fillers first
        for frag in self.library.fragments:
            frag.filler = None
        return self.designer.assign_fillers(list(self.filler_pool))

    # -- Validation -------------------------------------------------------- #

    def validate(self) -> ValidationResult:
        return self.designer.validate_all()

    # -- Export ------------------------------------------------------------ #

    def export_csv(self) -> str:
        return self.exporter.to_csv(self.library.fragments)

    def export_fasta(self) -> str:
        return self.exporter.to_fasta(self.library.fragments)

    def export_json(self) -> str:
        return self.exporter.to_json(self.library.fragments)
