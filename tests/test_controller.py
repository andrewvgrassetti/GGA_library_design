"""Unit tests for the AppController service layer."""

from gga_library.services.controller import AppController


class TestAppController:
    def test_create_and_list(self) -> None:
        ctrl = AppController()
        ctrl.create_fragment(
            name="F1",
            adapter_5p_seq="AA",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="TT",
        )
        assert ctrl.library.size == 1

    def test_add_filler(self) -> None:
        ctrl = AppController()
        fs = ctrl.add_filler("AAAA", "Filler-1")
        assert len(ctrl.filler_pool) == 1
        assert fs.name == "Filler-1"

    def test_remove_filler(self) -> None:
        ctrl = AppController()
        ctrl.add_filler("AAAA", "F1")
        ctrl.add_filler("CCCC", "F2")
        ctrl.remove_filler(0)
        assert len(ctrl.filler_pool) == 1
        assert ctrl.filler_pool[0].name == "F2"

    def test_clone_fragment(self) -> None:
        ctrl = AppController()
        f = ctrl.create_fragment(
            name="F1",
            adapter_5p_seq="AA",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="TT",
        )
        clone = ctrl.clone_fragment(f.id)
        assert clone is not None
        assert ctrl.library.size == 2

    def test_export_csv(self) -> None:
        ctrl = AppController()
        ctrl.create_fragment(
            name="F1",
            adapter_5p_seq="AA",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="TT",
        )
        csv = ctrl.export_csv()
        assert "F1" in csv

    def test_validate(self) -> None:
        ctrl = AppController()
        ctrl.create_fragment(
            name="F1",
            adapter_5p_seq="AA",
            overhang_5p_seq="AATG",
            variable_domains=[{"name": "VD1", "sequence": "ATCG"}],
            overhang_3p_seq="GCTT",
            adapter_3p_seq="TT",
        )
        result = ctrl.validate()
        # Should have no errors for a well-formed fragment
        assert all(m.level != "error" for m in result.messages)
