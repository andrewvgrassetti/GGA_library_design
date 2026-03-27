"""Unit tests for the validation layer."""

from gga_library.models.components import FillerSequence, Overhang, VariableDomain
from gga_library.models.fragment import FragmentTemplate
from gga_library.models.components import Adapter
from gga_library.models.library import FragmentLibrary
from gga_library.validation.rules import AssemblyRuleSet
from gga_library.validation.validator import SequenceValidator, ValidationResult


class TestSequenceValidator:
    def _validator(self, **kwargs) -> SequenceValidator:
        return SequenceValidator(AssemblyRuleSet(**kwargs))

    def _make_fragment(self, vd_seq: str = "ATCGATCG", name: str = "F") -> FragmentTemplate:
        return FragmentTemplate(
            name=name,
            adapter_5p=Adapter("GGTCTCN", is_5_prime=True),
            overhang_5p=Overhang("AATG", position="5'"),
            variable_domains=[VariableDomain(vd_seq, name="VD1")],
            overhang_3p=Overhang("GCTT", position="3'"),
            adapter_3p=Adapter("NGAGACC", is_5_prime=False),
        )

    # --- Alphabet ---------------------------------------------------------

    def test_valid_nucleotides(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_alphabet("ACGTACGT", r)
        assert r.is_valid

    def test_invalid_nucleotides(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_alphabet("ACGTXZ", r)
        assert not r.is_valid

    # --- GC content -------------------------------------------------------

    def test_gc_in_range(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_gc("AATTCCGG", r)  # 50%
        assert len(r.warnings) == 0

    def test_gc_out_of_range(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_gc("AAAAAAAAAA", r)  # 0%
        assert len(r.warnings) == 1

    # --- Forbidden sites --------------------------------------------------

    def test_forbidden_site_detected(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_forbidden_sites("XGGTCTCX", r)
        assert len(r.warnings) == 1

    def test_no_forbidden_site(self) -> None:
        v = self._validator()
        r = ValidationResult()
        v._check_forbidden_sites("ATCGATCG", r)
        assert len(r.warnings) == 0

    # --- Overhang ---------------------------------------------------------

    def test_overhang_valid_length(self) -> None:
        v = self._validator()
        r = v.validate_overhang("AATG")
        assert r.is_valid

    def test_overhang_too_short(self) -> None:
        v = self._validator()
        r = v.validate_overhang("AT")
        assert not r.is_valid

    def test_overhang_too_long(self) -> None:
        v = self._validator()
        r = v.validate_overhang("AATGATCG")
        assert not r.is_valid

    # --- Fragment ---------------------------------------------------------

    def test_valid_fragment(self) -> None:
        v = self._validator(check_gc=False, check_forbidden_sites=False)
        f = self._make_fragment()
        r = v.validate_fragment(f)
        assert r.is_valid

    def test_empty_name_flagged(self) -> None:
        v = self._validator(check_gc=False, check_forbidden_sites=False)
        f = self._make_fragment()
        f.name = ""
        r = v.validate_fragment(f)
        assert not r.is_valid

    def test_no_variable_domains_flagged(self) -> None:
        v = self._validator(check_gc=False, check_forbidden_sites=False)
        f = self._make_fragment()
        f.variable_domains = []
        r = v.validate_fragment(f)
        assert not r.is_valid

    # --- Library ----------------------------------------------------------

    def test_library_duplicate_names(self) -> None:
        v = self._validator(check_gc=False, check_forbidden_sites=False)
        lib = FragmentLibrary()
        lib.add(self._make_fragment(name="Same"))
        lib.add(self._make_fragment(name="Same"))
        r = v.validate_library(lib)
        assert not r.is_valid

    # --- Filler pool ------------------------------------------------------

    def test_filler_pool_valid(self) -> None:
        v = self._validator()
        fillers = [FillerSequence("AAAA", name="F1"), FillerSequence("CCCC", name="F2")]
        r = v.validate_filler_pool(fillers, 2)
        assert r.is_valid

    def test_filler_pool_duplicate(self) -> None:
        v = self._validator()
        fillers = [FillerSequence("AAAA", name="F1"), FillerSequence("AAAA", name="F2")]
        r = v.validate_filler_pool(fillers, 1)
        assert not r.is_valid

    def test_filler_pool_insufficient(self) -> None:
        v = self._validator()
        fillers = [FillerSequence("AAAA", name="F1")]
        r = v.validate_filler_pool(fillers, 5)
        assert len(r.warnings) > 0
