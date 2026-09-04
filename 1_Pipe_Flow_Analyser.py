"""Module A: interactive pipe-flow analysis page."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engineering import Fluid, Pipe

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="💧", layout="wide")
st.title("💧 Module A — Pipe Flow Analyser")
st.write(
    "Select a fluid and pipe geometry in the sidebar. The calculator reports "
    "mean velocity, Reynolds number, flow regime, Darcy friction factor, and pressure drop."
)

st.sidebar.header("🔧 Pipe & Fluid Inputs")
fluid_choice = st.sidebar.selectbox("Fluid", list(Fluid.PRESETS) + ["User-defined"])

if fluid_choice == "User-defined":
    rho_in = st.sidebar.number_input(
        "Fluid density, ρ (kg/m³)", min_value=0.0, value=1000.0,
        help="Mass of fluid per unit volume. Enter a positive value."
    )
    mu_in = st.sidebar.number_input(
        "Dynamic viscosity, μ (Pa·s)", min_value=0.0, value=0.001,
        format="%.6f", help="Resistance of the fluid to deformation and flow."
    )
else:
    rho_in, mu_in = None, None

D_mm = st.sidebar.number_input(
    "Pipe internal diameter, D (mm)", min_value=0.1, value=100.0, step=1.0,
    help="Inside diameter of the pipe through which the fluid flows."
)
L_m = st.sidebar.number_input(
    "Pipe length, L (m)", min_value=0.1, value=50.0, step=1.0,
    help="Length over which the frictional pressure loss is calculated."
)
eps_mm = st.sidebar.number_input(
    "Absolute roughness, ε (mm)", min_value=0.0, value=0.045, step=0.005,
    format="%.3f", help="Average height of surface roughness inside the pipe."
)
Q_lps = st.sidebar.slider(
    "Flow rate, Q (L/s)", min_value=0.0, max_value=100.0, value=10.0, step=0.5,
    help="Volumetric flow rate through the pipe."
)

try:
    fluid = Fluid(fluid_choice, rho=rho_in, mu=mu_in)
    pipe = Pipe(D_mm / 1000.0, L_m, eps_mm / 1000.0)
    Q = Q_lps / 1000.0
    velocity = pipe.velocity_from_flowrate(Q)
    Re = pipe.reynolds_number(fluid, velocity)
    f = pipe.friction_factor(Re)
    dP = pipe.pressure_drop(fluid, velocity)
    regime = pipe.flow_regime(Re)

    st.markdown("### 📊 Current Results")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Velocity", f"{velocity:.3f} m/s")
    c2.metric("Reynolds Number", f"{Re:,.0f}")
    c3.metric("Flow Regime", regime)
    c4.metric("Darcy Friction Factor", "N/A" if np.isnan(f) else f"{f:.5f}")
    c5.metric("Pressure Drop", f"{dP:,.1f} Pa")

    st.markdown("### 📈 Pressure Drop vs. Flow Rate")
    Q_max = max(2.0 * Q, 0.05)
    Q_range = np.linspace(0.0, Q_max, 120)
    rows = []
    for Q_val in Q_range:
        v = pipe.velocity_from_flowrate(Q_val)
        re_val = pipe.reynolds_number(fluid, v)
        f_val = pipe.friction_factor(re_val)
        dp_val = pipe.pressure_drop(fluid, v)
        rows.append({
            "Flow Rate (L/s)": Q_val * 1000.0,
            "Velocity (m/s)": v,
            "Reynolds Number": re_val,
            "Flow Regime": pipe.flow_regime(re_val),
            "Darcy Friction Factor": f_val,
            "Pressure Drop (Pa)": dp_val,
        })
    sweep_df = pd.DataFrame(rows)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sweep_df["Flow Rate (L/s)"], y=sweep_df["Pressure Drop (Pa)"],
        mode="lines", name="Pressure Drop"
    ))
    fig.add_trace(go.Scatter(
        x=[Q_lps], y=[dP], mode="markers", name="Current Setting",
        marker=dict(size=12, symbol="star")
    ))
    fig.update_layout(
        xaxis_title="Flow Rate (L/s)", yaxis_title="Pressure Drop (Pa)",
        template="plotly_white", height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Flow-Rate Sweep")
    st.dataframe(sweep_df.round(4), use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download Sweep Results as CSV",
        data=sweep_df.to_csv(index=False).encode("utf-8"),
        file_name="pipe_flow_sweep_results.csv",
        mime="text/csv",
    )

    with st.expander("📐 Engineering verification"):
        st.markdown(
            "For water at 20°C, D = 0.100 m and Q = 0.010 m³/s: "
            "A = πD²/4 ≈ 0.007854 m², so v ≈ 1.273 m/s. "
            "Using ρ = 998 kg/m³ and μ = 1.002×10⁻³ Pa·s gives "
            "Re ≈ 127,000, which is turbulent. The app independently evaluates "
            "the same equations for the displayed result."
        )
except ValueError as exc:
    st.warning(f"⚠️ Invalid input: {exc}")
except (TypeError, OverflowError) as exc:
    st.warning(f"⚠️ The calculation could not be completed: {exc}")
