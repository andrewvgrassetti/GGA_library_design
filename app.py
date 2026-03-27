"""GGA Library Designer – Streamlit entry-point.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from gga_library.services.controller import AppController
from gga_library.ui.fragment_form import render_fragment_form
from gga_library.ui.library_table import render_library_table
from gga_library.ui.sidebar import render_sidebar
from gga_library.ui.validation_panel import render_validation_panel


def _get_controller() -> AppController:
    """Return (or create) the session-scoped AppController."""
    if "controller" not in st.session_state:
        st.session_state["controller"] = AppController()
    return st.session_state["controller"]


def main() -> None:
    st.set_page_config(
        page_title="GGA Library Designer",
        page_icon="🧬",
        layout="wide",
    )

    ctrl = _get_controller()

    # --- Sidebar ---
    render_sidebar(ctrl)

    # --- Main area ---
    st.title("🧬 GGA Library Designer")
    st.caption(
        "Design modular Golden Gate Assembly fragment libraries with fixed adapters, "
        "overhangs, and user-defined variable domains."
    )

    tab_design, tab_library, tab_export = st.tabs(
        ["🛠️ Design", "📋 Library", "📥 Validate & Export"]
    )

    with tab_design:
        render_fragment_form(ctrl)

    with tab_library:
        render_library_table(ctrl)

    with tab_export:
        render_validation_panel(ctrl)


if __name__ == "__main__":
    main()
