# Fluid Flow & Heat Transfer Engineering Suite

A multi-page Streamlit engineering application developed for the PE 262 capstone. It combines an object-oriented engineering calculation core with interactive data visualisation.

**Live App URL:** `PASTE_YOUR_STREAMLIT_URL_HERE`

**GitHub Repository:** `PASTE_YOUR_GITHUB_URL_HERE`

## Modules

### Module A — Pipe Flow Analyser
- Fluid selection: water, air, crude oil, or user-defined properties
- Pipe diameter, length, roughness, and flow-rate inputs
- Mean velocity
- Reynolds number and flow regime
- Darcy friction factor
- Darcy-Weisbach pressure drop
- Interactive pressure-drop vs flow-rate plot
- CSV export of the flow-rate sweep

### Module B — Heat Transfer Calculator
- Steady-state conduction through a single-layer flat wall using Fourier's law
- Newton's law of cooling
- Analytical time to reach a target temperature
- Interactive temperature-vs-time cooling curve
- Physical descriptions and unit guidance for inputs

### Module C — Rock & Fluid Data Dashboard
- User CSV upload
- Summary statistics
- Numeric threshold filtering
- Porosity histogram
- Porosity-permeability crossplot when the expected columns are present
- Filtered CSV download
- Built-in sample dataset for demonstration/testing

## Project Structure

```text
fluid-heat-suite/
├── engineering.py
├── app.py
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py
│   ├── 2_Heat_Transfer_Calculator.py
│   └── 3_Rock_Fluid_Dashboard.py
├── requirements.txt
└── README.md
```

## Engineering Methods

For pipe flow, the application uses:

- `v = Q/A`
- `Re = ρvD/μ`
- `f = 64/Re` for laminar flow
- Swamee-Jain explicit approximation to Colebrook for turbulent flow
- Darcy-Weisbach: `ΔP = f(L/D)(ρv²/2)`

The transitional friction factor is linearly interpolated between the laminar value at `Re = 2300` and the turbulent Swamee-Jain estimate at `Re = 4000`. This is explicitly identified as an engineering approximation because transitional pipe flow does not have one universally accepted explicit friction-factor equation.

For heat transfer:

- Fourier's law: `Q = kA(T_hot − T_cold)/L`
- Newton cooling: `T(t) = T∞ + (T₀ − T∞) exp[−hAt/(mcp)]`
- Analytical target time is obtained by rearranging the Newton-cooling equation.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Verification

A water-flow reference case is included in Module A: `D = 0.100 m` and `Q = 0.010 m³/s`, giving `v ≈ 1.273 m/s` and `Re ≈ 127,000`, indicating turbulent flow.

The default flat-wall conduction case gives `Q = 800 W` from Fourier's law.

The Newton-cooling solver is checked by substituting its analytical target time back into the temperature equation.

## AI Assistance

AI assistance was used for code scaffolding, implementation ideas, explanations, debugging, and interface improvements. The final application was reviewed against the assignment requirements and the governing engineering equations. Representative prompts, verification steps, and corrections are documented on the app home page.
