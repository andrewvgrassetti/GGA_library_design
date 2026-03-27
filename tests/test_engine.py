"""Unit tests for the fragment designer / assembly engine."""

from gga_library.engine.designer import FragmentDesigner
from gga_library.models.components import FillerSequence


class TestFragmentDesigner:
    def _designer(self) -> FragmentDesigner:
        return FragmentDesigner()

    def test_create_fragment(self) -> None:
        d = self._designer()
        f = d.create_fragment(
            name="F1",
            adapter_5p_seq="GGTCTCN",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCGATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="NGAGACC",
        )
        assert f.name == "F1"
        assert d.library.size == 1
        assert f.full_sequence == "GGTCTCNAATGATCGATCGGCTTNGAGACC"

    def test_remove_fragment(self) -> None:
        d = self._designer()
        f = d.create_fragment(
            name="F1",
            adapter_5p_seq="A",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="T",
        )
        d.remove_fragment(f.id)
        assert d.library.size == 0

    def test_clone_fragment(self) -> None:
        d = self._designer()
        f = d.create_fragment(
            name="F1",
            adapter_5p_seq="A",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="T",
        )
        clone = d.clone_fragment(f.id)
        assert clone is not None
        assert clone.id != f.id
        assert d.library.size == 2

    def test_assign_fillers(self) -> None:
        d = self._designer()
        # Create a short fragment (needs filler)
        d.create_fragment(
            name="Short",
            adapter_5p_seq="AA",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="TT",
        )
        pool = [FillerSequence("A" * 300, name="Filler-A")]
        result = d.assign_fillers(pool)
        frag = d.library.fragments[0]
        assert frag.filler is not None
        assert frag.total_length >= 300

    def test_assign_fillers_unique(self) -> None:
        d = self._designer()
        for i in range(2):
            d.create_fragment(
                name=f"Short-{i}",
                adapter_5p_seq="AA",
                overhang_5p_seq="AATG",
                variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
                overhang_3p_seq="GCTT",
                adapter_3p_seq="TT",
            )
        pool = [
            FillerSequence("A" * 300, name="Filler-A"),
            FillerSequence("C" * 300, name="Filler-C"),
        ]
        d.assign_fillers(pool)
        fillers_used = [f.filler.sequence for f in d.library.fragments if f.filler]
        assert len(fillers_used) == len(set(fillers_used))

    def test_validate_all(self) -> None:
        d = self._designer()
        d.create_fragment(
            name="F1",
            adapter_5p_seq="GGTCTCN",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCGATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="NGAGACC",
        )
        result = d.validate_all()
        # Should have no errors (maybe warnings for GC/sites)
        assert all(m.level != "error" for m in result.messages)
