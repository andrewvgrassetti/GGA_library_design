"""Sidebar UI component – settings and configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from gga_library.services.controller import AppController


def render_sidebar(ctrl: "AppController") -> None:
    """Render the sidebar with global settings and filler management."""
    st.sidebar.header("⚙️ Settings")

    st.sidebar.subheader("Default Adapters")
    new_5p = st.sidebar.text_input(
        "5' Adapter (default)",
        value=st.session_state.get("default_5p", ctrl.config.default_5p_adapter),
        key="sidebar_5p_adapter",
    )
    new_3p = st.sidebar.text_input(
        "3' Adapter (default)",
        value=st.session_state.get("default_3p", ctrl.config.default_3p_adapter),
        key="sidebar_3p_adapter",
    )
    st.session_state["default_5p"] = new_5p
    st.session_state["default_3p"] = new_3p

    st.sidebar.divider()

    # ------ Validation toggles ------
    st.sidebar.subheader("Validation")
    st.session_state["check_gc"] = st.sidebar.checkbox(
        "Check GC content", value=st.session_state.get("check_gc", True)
    )
    st.session_state["check_sites"] = st.sidebar.checkbox(
        "Check forbidden restriction sites",
        value=st.session_state.get("check_sites", True),
    )
    ctrl.validator.rules.check_gc = st.session_state["check_gc"]
    ctrl.validator.rules.check_forbidden_sites = st.session_state["check_sites"]

    st.sidebar.divider()

    # ------ Filler pool management ------
    st.sidebar.subheader("🧩 Filler Sequences")
    st.sidebar.caption(
        "Add filler sequences to pad short fragments to ≥300 bp. "
        "Each filler is used at most once across the library."
    )

    with st.sidebar.form("add_filler_form", clear_on_submit=True):
        filler_name = st.text_input("Filler name", placeholder="e.g. Filler-A")
        filler_seq = st.text_area(
            "Filler sequence",
            placeholder="ACGT…",
            height=68,
        )
        submitted = st.form_submit_button("Add filler")
        if submitted and filler_seq.strip():
            ctrl.add_filler(filler_seq.strip(), filler_name.strip())
            st.rerun()

    # List current pool
    if ctrl.filler_pool:
        for i, fs in enumerate(ctrl.filler_pool):
            col1, col2 = st.sidebar.columns([3, 1])
            col1.markdown(f"**{fs.name}** ({fs.length} bp)")
            if col2.button("🗑️", key=f"del_filler_{i}"):
                ctrl.remove_filler(i)
                st.rerun()
    else:
        st.sidebar.info("No fillers added yet.")
