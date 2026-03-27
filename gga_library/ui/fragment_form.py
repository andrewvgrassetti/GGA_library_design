"""Fragment design form – main area for creating / editing fragments."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from gga_library.services.controller import AppController


def render_fragment_form(ctrl: "AppController") -> None:
    """Render the fragment design form."""
    st.subheader("🧬 Design a New Fragment")

    with st.form("fragment_form", clear_on_submit=True):
        name = st.text_input("Fragment name *", placeholder="e.g. Fragment-1")

        col1, col2 = st.columns(2)
        adapter_5p = col1.text_input(
            "5' Adapter sequence",
            value=st.session_state.get("default_5p", ctrl.config.default_5p_adapter),
        )
        adapter_3p = col2.text_input(
            "3' Adapter sequence",
            value=st.session_state.get("default_3p", ctrl.config.default_3p_adapter),
        )

        col3, col4 = st.columns(2)
        overhang_5p = col3.text_input("5' Overhang (e.g. 4 bp)", placeholder="AATG")
        overhang_3p = col4.text_input("3' Overhang (e.g. 4 bp)", placeholder="GCTT")

        st.markdown("**Variable Domains**")
        st.caption("Enter one or more variable domains (comma-separated names and sequences).")

        num_domains = st.number_input(
            "Number of variable domains", min_value=1, max_value=10, value=1, step=1
        )

        domains = []
        for i in range(int(num_domains)):
            dc1, dc2 = st.columns([1, 3])
            d_name = dc1.text_input(f"Domain {i+1} name", value=f"VD-{i+1}", key=f"vd_name_{i}")
            d_seq = dc2.text_input(f"Domain {i+1} sequence", key=f"vd_seq_{i}")
            domains.append({"name": d_name, "sequence": d_seq})

        notes = st.text_area("Notes (optional)", height=68)

        submitted = st.form_submit_button("➕ Add Fragment", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Fragment name is required.")
            return
        if not any(d["sequence"].strip() for d in domains):
            st.error("At least one variable domain sequence is required.")
            return

        # Filter empty domains
        valid_domains = [d for d in domains if d["sequence"].strip()]

        ctrl.create_fragment(
            name=name.strip(),
            adapter_5p_seq=adapter_5p.strip(),
            overhang_5p_seq=overhang_5p.strip(),
            variable_domains=valid_domains,
            overhang_3p_seq=overhang_3p.strip(),
            adapter_3p_seq=adapter_3p.strip(),
            notes=notes.strip(),
        )
        st.success(f"Fragment **{name}** added!")
        st.rerun()
