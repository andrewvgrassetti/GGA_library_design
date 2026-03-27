"""Unit tests for the export service."""

from gga_library.export.exporter import ExportService
from gga_library.models.components import Adapter, Overhang, VariableDomain
from gga_library.models.fragment import FragmentTemplate


def _make_fragment(name: str = "TestFrag") -> FragmentTemplate:
    return FragmentTemplate(
        name=name,
        adapter_5p=Adapter("GGTCTCN", is_5_prime=True),
        overhang_5p=Overhang("AATG", position="5'"),
        variable_domains=[VariableDomain("ATCGATCG", name="VD1")],
        overhang_3p=Overhang("GCTT", position="3'"),
        adapter_3p=Adapter("NGAGACC", is_5_prime=False),
    )


class TestExportService:
    def test_csv_header(self) -> None:
        csv = ExportService.to_csv([_make_fragment()])
        assert "Name" in csv
        assert "Full Sequence" in csv

    def test_csv_contains_fragment(self) -> None:
        csv = ExportService.to_csv([_make_fragment("Frag-A")])
        assert "Frag-A" in csv

    def test_fasta_format(self) -> None:
        fasta = ExportService.to_fasta([_make_fragment("Frag-A")])
        assert fasta.startswith(">Frag-A")
        assert "GGTCTCN" in fasta

    def test_json_format(self) -> None:
        import json
        raw = ExportService.to_json([_make_fragment()])
        data = json.loads(raw)
        assert isinstance(data, list)
        assert data[0]["name"] == "TestFrag"

    def test_multiple_fragments(self) -> None:
        frags = [_make_fragment("A"), _make_fragment("B")]
        csv = ExportService.to_csv(frags)
        assert "A" in csv
        assert "B" in csv
