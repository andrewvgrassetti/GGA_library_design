# GGA Library Designer

A production-quality Python application for designing **Golden Gate Assembly (GGA)** library fragments with fixed sequence adapters, overhangs, and user-defined variable domains.

## Features

- **Modular fragment design** — compose fragments from 5′ adapter, overhangs, variable domains, and 3′ adapter
- **Live validation** — nucleotide alphabet, GC content, forbidden restriction sites, overhang length, duplicate names
- **Filler sequence management** — automatically pad short fragments (< 300 bp) with unique user-provided fillers
- **Multi-format export** — CSV, FASTA, and JSON
- **Clone / edit / delete** fragments in-session
- **Clean Streamlit UI** with sidebar settings, tabbed design workflow, and library overview

## Architecture

```
gga_library/
├── config/       # AppConfig and constants
├── models/       # Domain models: SequenceComponent, Adapter, Overhang, VariableDomain, FillerSequence, FragmentTemplate, FragmentLibrary
├── validation/   # SequenceValidator, AssemblyRuleSet
├── engine/       # FragmentDesigner – assembly logic
├── services/     # AppController – orchestration layer
├── export/       # ExportService – CSV / FASTA / JSON
└── ui/           # Streamlit UI components (sidebar, fragment form, library table, validation panel)
```

All business logic is separated from the UI. The `AppController` service layer is the single entry-point the UI talks to, making it easy to add a CLI or API later.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Example Workflow

1. **Configure adapters** in the sidebar (defaults to BsaI Golden Gate adapters).
2. **Add filler sequences** in the sidebar for padding short fragments.
3. **Design fragments** in the Design tab — enter a name, overhangs, and variable domain sequences.
4. **Review** fragments in the Library tab — view component breakdowns, clone, or delete.
5. **Validate & Export** in the Validate & Export tab — run validation, assign fillers, and download CSV / FASTA / JSON.

## Extension Points

| Future feature | Where to extend |
|---|---|
| New cloning methods (BsmBI, etc.) | Add a new `AssemblyRuleSet` preset in `validation/rules.py` |
| Combinatorial library generation | Add a `CombinatorialDesigner` in `engine/` that yields multiple `FragmentTemplate` objects |
| Primer design hooks | Add a `primer_design` module under `gga_library/` |
| Plasmid backbone support | Add a `Backbone` component type and include it in `FragmentTemplate.components` |
| Enzyme-specific scar rules | Extend `AssemblyRuleSet` with scar-sequence constraints |
| Protocol-aware filtering | Add filter predicates to the `SequenceValidator` |

## Object-Oriented Design

- **SequenceComponent** is the base class for all DNA building blocks (Adapter, Overhang, VariableDomain, FillerSequence).
- **FragmentTemplate** composes components into a single designed fragment.
- **FragmentLibrary** manages a collection of templates.
- **SequenceValidator** applies configurable **AssemblyRuleSet** rules.
- **FragmentDesigner** orchestrates fragment creation and filler assignment.
- **AppController** ties everything together for the UI.
- **ExportService** handles serialization to multiple output formats.