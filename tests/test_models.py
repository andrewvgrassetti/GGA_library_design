"""Unit tests for domain models."""

from gga_library.models.components import (
    Adapter,
    ComponentType,
    FillerSequence,
    Overhang,
    VariableDomain,
)
from gga_library.models.fragment import FragmentTemplate
from gga_library.models.library import FragmentLibrary


class TestSequenceComponents:
    def test_adapter_creation(self) -> None:
        a = Adapter("GGTCTCN", is_5_prime=True)
        assert a.sequence == "GGTCTCN"
        assert a.component_type == ComponentType.ADAPTER_5P
        assert a.length == 7

    def test_adapter_3p(self) -> None:
        a = Adapter("NGAGACC", is_5_prime=False)
        assert a.component_type == ComponentType.ADAPTER_3P

    def test_overhang(self) -> None:
        o = Overhang("AATG", position="5'")
        assert o.sequence == "AATG"
        assert o.length == 4
        assert o.position == "5'"

    def test_variable_domain(self) -> None:
        vd = VariableDomain("ATCGATCG", name="Test Domain", description="desc")
        assert vd.length == 8
        assert vd.description == "desc"

    def test_filler(self) -> None:
        f = FillerSequence("AAAA", name="F1")
        assert f.component_type == ComponentType.FILLER

    def test_sequence_uppercased(self) -> None:
        a = Adapter("ggtctcn", is_5_prime=True)
        assert a.sequence == "GGTCTCN"


class TestFragmentTemplate:
    def _make_fragment(self, vd_seq: str = "ATCGATCGATCG") -> FragmentTemplate:
        return FragmentTemplate(
            name="Test-Fragment",
            adapter_5p=Adapter("GGTCTCN", is_5_prime=True),
            overhang_5p=Overhang("AATG", position="5'"),
            variable_domains=[VariableDomain(vd_seq, name="VD1")],
            overhang_3p=Overhang("GCTT", position="3'"),
            adapter_3p=Adapter("NGAGACC", is_5_prime=False),
        )

    def test_full_sequence(self) -> None:
        f = self._make_fragment()
        expected = "GGTCTCN" + "AATG" + "ATCGATCGATCG" + "GCTT" + "NGAGACC"
        assert f.full_sequence == expected

    def test_core_length(self) -> None:
        f = self._make_fragment()
        assert f.core_length == 7 + 4 + 12 + 4 + 7  # 34

    def test_needs_filler(self) -> None:
        f = self._make_fragment()
        assert f.needs_filler is True  # 34 < 300

    def test_no_filler_needed_for_long(self) -> None:
        f = self._make_fragment("A" * 300)
        assert f.needs_filler is False

    def test_filler_included_in_sequence(self) -> None:
        f = self._make_fragment()
        f.filler = FillerSequence("CCCC", name="pad")
        assert "CCCC" in f.full_sequence

    def test_clone(self) -> None:
        f = self._make_fragment()
        c = f.clone("Copy-1")
        assert c.name == "Copy-1"
        assert c.id != f.id
        assert c.full_sequence == f.full_sequence

    def test_to_dict(self) -> None:
        f = self._make_fragment()
        d = f.to_dict()
        assert d["name"] == "Test-Fragment"
        assert d["total_length"] == f.total_length
        assert isinstance(d["variable_domains"], list)


class TestFragmentLibrary:
    def test_add_and_get(self) -> None:
        lib = FragmentLibrary()
        f = FragmentTemplate(
            name="F1",
            adapter_5p=Adapter("A", is_5_prime=True),
            overhang_5p=Overhang("AATG"),
            variable_domains=[VariableDomain("ATCG")],
        )
        lib.add(f)
        assert lib.size == 1
        assert lib.get(f.id) is f

    def test_remove(self) -> None:
        lib = FragmentLibrary()
        f = FragmentTemplate(
            name="F1",
            adapter_5p=Adapter("A", is_5_prime=True),
            overhang_5p=Overhang("AATG"),
            variable_domains=[VariableDomain("ATCG")],
        )
        lib.add(f)
        lib.remove(f.id)
        assert lib.size == 0

    def test_duplicate_names(self) -> None:
        lib = FragmentLibrary()
        for _ in range(2):
            lib.add(
                FragmentTemplate(
                    name="Same",
                    adapter_5p=Adapter("A", is_5_prime=True),
                    overhang_5p=Overhang("AATG"),
                    variable_domains=[VariableDomain("ATCG")],
                )
            )
        assert "Same" in lib.has_duplicate_names()
