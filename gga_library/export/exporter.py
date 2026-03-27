"""Export service – CSV, FASTA, JSON."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from gga_library.models.fragment import FragmentTemplate


class ExportService:
    """Generates downloadable export data from a list of fragment templates."""

    @staticmethod
    def to_csv(fragments: List[FragmentTemplate]) -> str:
        """Return CSV string of the fragment library."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Name", "ID", "5' Adapter", "5' Overhang",
            "Variable Domains", "3' Overhang", "3' Adapter",
            "Filler", "Full Sequence", "Length (bp)", "Notes",
        ])
        for f in fragments:
            vd_str = "; ".join(
                f"{vd.name}={vd.sequence}" for vd in f.variable_domains
            )
            writer.writerow([
                f.name, f.id,
                f.adapter_5p.sequence, f.overhang_5p.sequence,
                vd_str,
                f.overhang_3p.sequence, f.adapter_3p.sequence,
                f.filler.sequence if f.filler else "",
                f.full_sequence, f.total_length, f.notes,
            ])
        return buf.getvalue()

    @staticmethod
    def to_fasta(fragments: List[FragmentTemplate]) -> str:
        """Return multi-FASTA string."""
        lines: List[str] = []
        for f in fragments:
            header = f">{f.name} | {f.total_length}bp | id={f.id}"
            lines.append(header)
            # Wrap sequence at 80 chars
            seq = f.full_sequence
            for i in range(0, len(seq), 80):
                lines.append(seq[i : i + 80])
        return "\n".join(lines) + "\n"

    @staticmethod
    def to_json(fragments: List[FragmentTemplate], indent: int = 2) -> str:
        """Return pretty-printed JSON string."""
        data = [f.to_dict() for f in fragments]
        return json.dumps(data, indent=indent)
