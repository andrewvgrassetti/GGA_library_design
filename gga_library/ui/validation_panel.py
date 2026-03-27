"""Validation and export panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from gga_library.services.controller import AppController


def render_validation_panel(ctrl: "AppController") -> None:
    """Render validation results and export controls."""
    st.subheader("✅ Validation & Export")

    if ctrl.library.size == 0:
        st.info("Add fragments to see validation results and export options.")
        return

    col_v, col_f = st.columns(2)

    # --- Validate ---
    with col_v:
        if st.button("🔍 Validate Library", use_container_width=True):
            result = ctrl.validate()
            st.session_state["validation_result"] = result

    # --- Assign fillers ---
    with col_f:
        if st.button("🧩 Assign Fillers", use_container_width=True):
            filler_result = ctrl.assign_fillers()
            st.session_state["filler_result"] = filler_result
            st.rerun()

    # Show filler assignment result
    filler_result = st.session_state.get("filler_result")
    if filler_result:
        for msg in filler_result.messages:
            if msg.level == "error":
                st.error(msg.message)
            elif msg.level == "warning":
                st.warning(msg.message)
            else:
                st.info(msg.message)

    # Show validation results
    result = st.session_state.get("validation_result")
    if result:
        if result.is_valid:
            st.success("Library passed all validation checks.")
        for msg in result.errors:
            st.error(f"❌ {msg.message}")
        for msg in result.warnings:
            st.warning(f"⚠️ {msg.message}")

    st.divider()

    # --- Export ---
    st.markdown("**Export**")
    fmt = st.radio("Format", ["CSV", "FASTA", "JSON"], horizontal=True)

    if st.button("📥 Generate Export", use_container_width=True):
        if fmt == "CSV":
            data = ctrl.export_csv()
            st.download_button("Download CSV", data, "gga_library.csv", "text/csv")
        elif fmt == "FASTA":
            data = ctrl.export_fasta()
            st.download_button("Download FASTA", data, "gga_library.fasta", "text/plain")
        else:
            data = ctrl.export_json()
            st.download_button("Download JSON", data, "gga_library.json", "application/json")

        st.text_area("Preview", data, height=200)
