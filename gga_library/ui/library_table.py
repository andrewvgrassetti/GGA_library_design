"""Library table view – displays all fragments in a grid with actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from gga_library.services.controller import AppController


def render_library_table(ctrl: "AppController") -> None:
    """Render the current library as an interactive table."""
    st.subheader("📋 Fragment Library")

    fragments = ctrl.library.fragments
    if not fragments:
        st.info("No fragments designed yet. Use the form above to add one.")
        return

    # Summary bar
    st.caption(f"{ctrl.library.size} fragment(s) in library")

    for frag in fragments:
        with st.expander(f"**{frag.name}** — {frag.total_length} bp", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("Core length", f"{frag.core_length} bp")
            c2.metric("Total length", f"{frag.total_length} bp")
            c3.metric("Needs filler", "Yes" if frag.needs_filler else "No")

            st.markdown("**Component breakdown:**")
            comp_data = []
            for comp in frag.components:
                comp_data.append({
                    "Component": comp.name,
                    "Type": comp.component_type.value,
                    "Length": comp.length,
                    "Sequence": comp.sequence[:50] + ("…" if len(comp.sequence) > 50 else ""),
                })
            st.table(comp_data)

            st.markdown("**Full sequence preview:**")
            st.code(frag.full_sequence[:200] + ("…" if len(frag.full_sequence) > 200 else ""), language=None)

            if frag.filler:
                st.info(f"Filler: **{frag.filler.name}** ({frag.filler.length} bp)")
            if frag.notes:
                st.caption(f"Notes: {frag.notes}")

            # Actions
            act1, act2 = st.columns(2)
            if act1.button("📋 Clone", key=f"clone_{frag.id}"):
                ctrl.clone_fragment(frag.id)
                st.rerun()
            if act2.button("🗑️ Delete", key=f"del_{frag.id}"):
                ctrl.remove_fragment(frag.id)
                st.rerun()
