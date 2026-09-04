"""Home page for the PE 262 Fluid Flow & Heat Transfer Engineering Suite."""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Engineering Suite",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Fluid Flow & Heat Transfer Engineering Suite")
st.subheader("PE 262 Capstone Project")
st.write(
    "A multi-page engineering application combining pipe-flow calculations, "
    "heat-transfer analysis, and rock/fluid data analysis. The engineering "
    "calculations are separated into a reusable object-oriented Python module."
)

st.markdown("### Modules")
st.markdown(
    "- **💧 Pipe Flow Analyser:** velocity, Reynolds number, flow regime, Darcy friction factor, pressure drop, sweep plot, and CSV export.\n"
    "- **🔥 Heat Transfer Calculator:** Fourier-law conduction and Newton's-law cooling with an interactive cooling curve.\n"
    "- **🪨 Rock & Fluid Data Dashboard:** CSV upload, statistics, filtering, histogram, crossplot, and filtered CSV download."
)

st.info("Use the page navigation in the left sidebar to open any module.")

st.markdown("---")
st.markdown("### 🤖 AI Assistance Documentation")
st.write(
    "AI tools were used as development assistants for code structure, explanations, "
    "debugging ideas, and interface improvements. The final calculations were independently "
    "checked against the governing engineering equations before deployment."
)

with st.expander("Three representative AI prompts and verification"):
    st.markdown(
        """
**Prompt 1 — OOP structure**  
Asked the AI to design a reusable `engineering.py` module containing `Fluid`, `Pipe`, and `HeatTransfer` classes with input validation and docstrings.  
**Verified/corrected:** checked the class interfaces, units, validation rules, and Darcy-Weisbach/Reynolds-number equations.

**Prompt 2 — Heat-transfer calculations**  
Asked the AI to implement Fourier's law and Newton's law of cooling, including analytical cooling time and a temperature-vs-time curve.  
**Verified/corrected:** checked the algebra for the cooling-time equation and added validation so the target temperature must lie strictly between the initial and ambient temperatures.

**Prompt 3 — Data dashboard**  
Asked the AI to build CSV upload, summary statistics, threshold filtering, a porosity histogram, a porosity-permeability crossplot, and CSV download.  
**Verified/corrected:** ensured the app handles empty/invalid CSV files and automatically uses `Porosity_pct` and `Permeability_mD` when those columns exist.
        """
    )

st.caption("Built with Python, Streamlit, NumPy, Pandas, and Plotly.")
