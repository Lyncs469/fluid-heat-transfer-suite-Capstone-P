"""Module B: conduction and Newton's-law-of-cooling page."""

import plotly.graph_objects as go
import streamlit as st

from engineering import HeatTransfer

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🔥", layout="wide")
st.title("🔥 Module B — Heat Transfer Calculator")
st.write(
    "Use the sidebar for two independent calculations: steady-state conduction "
    "through a flat wall and transient cooling of an object in a constant-temperature environment."
)

st.sidebar.header("🧱 Conduction — Flat Wall")
k = st.sidebar.number_input(
    "Thermal conductivity, k (W/m·K)", min_value=0.0, value=0.8, step=0.1,
    help="How readily the wall material conducts heat. Higher k means easier heat conduction."
)
A_cond = st.sidebar.number_input(
    "Wall area, A (m²)", min_value=0.0, value=10.0, step=1.0,
    help="Area normal to the direction of heat flow."
)
L_cond = st.sidebar.number_input(
    "Wall thickness, L (m)", min_value=0.0, value=0.2, step=0.01,
    help="Distance heat travels through the wall."
)
T_hot = st.sidebar.number_input("Hot-face temperature (°C)", value=25.0)
T_cold = st.sidebar.number_input("Cold-face temperature (°C)", value=5.0)

st.sidebar.header("🧊 Newton's Law of Cooling")
T0 = st.sidebar.number_input(
    "Initial object temperature, T₀ (°C)", value=90.0,
    help="Temperature of the object at time t = 0."
)
T_inf = st.sidebar.number_input(
    "Ambient temperature, T∞ (°C)", value=20.0,
    help="Constant temperature of the surrounding environment."
)
T_target = st.sidebar.slider(
    "Target temperature (°C)", -20.0, 150.0, 40.0, 1.0,
    help="Temperature the object is required to reach. For cooling, it must lie between T₀ and T∞."
)
h = st.sidebar.number_input(
    "Convective coefficient, h (W/m²·K)", min_value=0.0, value=10.0, step=1.0,
    help="How strongly the surrounding fluid transfers heat at the object's surface."
)
A_cool = st.sidebar.number_input(
    "Object surface area, A (m²)", min_value=0.0, value=0.05, step=0.01,
    help="Exposed surface area available for convection."
)
m = st.sidebar.number_input(
    "Object mass, m (kg)", min_value=0.0, value=0.3, step=0.1,
    help="Mass of the object being cooled."
)
cp = st.sidebar.number_input(
    "Specific heat capacity, cp (J/kg·K)", min_value=0.0, value=4186.0, step=100.0,
    help="Energy required to raise 1 kg of the object by 1°C."
)

st.markdown("## 1️⃣ Steady-State Conduction Through a Flat Wall")
try:
    Q_cond = HeatTransfer.conduction_flat_wall(k, A_cond, L_cond, T_hot, T_cold)
    c1, c2 = st.columns(2)
    c1.metric("Heat Transfer Rate, Q", f"{Q_cond:,.2f} W")
    c2.metric("Heat Flux, Q/A", f"{Q_cond / A_cond:,.2f} W/m²")
    with st.expander("📐 Fourier's-law verification"):
        st.write(
            "Q = kA(T_hot − T_cold)/L. With the default values, "
            "Q = 0.8 × 10 × (25 − 5) / 0.2 = 800 W."
        )
except ValueError as exc:
    st.warning(f"⚠️ Invalid conduction input: {exc}")

st.markdown("---")
st.markdown("## 2️⃣ Newton's Law of Cooling")
try:
    time_s = HeatTransfer.cooling_time(T0, T_target, T_inf, h, A_cool, m, cp)
    c1, c2, c3 = st.columns(3)
    c1.metric("Time to Target", f"{time_s:,.1f} s")
    c2.metric("Time", f"{time_s / 60:,.2f} min")
    c3.metric("Time", f"{time_s / 3600:,.3f} hr")

    t_max = max(1.5 * time_s, 1.0)
    t, temperature = HeatTransfer.cooling_curve(T0, T_inf, h, A_cool, m, cp, t_max)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=temperature, mode="lines", name="Object Temperature"))
    fig.add_hline(y=T_target, line_dash="dash", annotation_text="Target")
    fig.add_hline(y=T_inf, line_dash="dot", annotation_text="Ambient")
    fig.add_vline(x=time_s, line_dash="dash", annotation_text="Target time")
    fig.update_layout(
        title="Cooling Curve", xaxis_title="Time (s)", yaxis_title="Temperature (°C)",
        template="plotly_white", height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 Newton-cooling verification"):
        st.write(
            "The model is T(t) = T∞ + (T₀ − T∞) exp[−hAt/(mcp)]. "
            "The displayed target time is obtained analytically and can be checked "
            "by substituting it back into this equation."
        )
except ValueError as exc:
    st.warning(f"⚠️ Invalid cooling input: {exc}")
