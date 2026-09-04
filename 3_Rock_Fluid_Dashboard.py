"""Module C: uploaded rock/fluid data dashboard."""

import io

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="🪨", layout="wide")
st.title("🪨 Module C — Rock & Fluid Data Dashboard")
st.write(
    "Upload a CSV containing rock or fluid measurements. The dashboard provides "
    "summary statistics, threshold filtering, a histogram, a crossplot, and filtered-data download."
)

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if "sample_data_generated" not in st.session_state:
    st.session_state.sample_data_generated = False

if st.button("🎲 Generate sample data"):
    st.session_state.sample_data_generated = True

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif st.session_state.sample_data_generated:
        rng = np.random.default_rng(42)
        n = 150
        porosity = rng.normal(18, 6, n).clip(1, 35)
        permeability = np.exp(0.25 * porosity + rng.normal(0, 1.2, n))
        df = pd.DataFrame({
            "Sample_ID": [f"S{i + 1:03d}" for i in range(n)],
            "Porosity_pct": porosity.round(2),
            "Permeability_mD": permeability.round(2),
        })
    else:
        df = None

    if df is None:
        st.info("👆 Upload a CSV or generate sample data to begin.")
    elif df.empty:
        st.warning("⚠️ The uploaded CSV contains no rows.")
    else:
        st.markdown("### 📋 Data Preview")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if not numeric_cols:
            st.warning("⚠️ No numeric columns were found, so statistics and plots cannot be created.")
        else:
            st.markdown("### 📊 Summary Statistics")
            st.dataframe(df[numeric_cols].describe().round(3), use_container_width=True)

            st.markdown("### 🔍 Filter Samples")
            default_filter = (
                numeric_cols.index("Porosity_pct") if "Porosity_pct" in numeric_cols else 0
            )
            filter_col = st.selectbox("Numeric column to filter", numeric_cols, index=default_filter)
            min_value = float(df[filter_col].min())
            max_value = float(df[filter_col].max())

            if min_value == max_value:
                threshold = min_value
                filtered_df = df.copy()
                st.info(f"All values in {filter_col} are {min_value}; no rows are removed.")
            else:
                threshold = st.slider(
                    f"Show samples where {filter_col} is greater than",
                    min_value=min_value, max_value=max_value, value=min_value,
                )
                filtered_df = df[df[filter_col] > threshold]

            st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** samples.")
            if filtered_df.empty:
                st.warning("⚠️ No samples meet the selected filter. Lower the threshold.")
            else:
                st.markdown("### 📈 Visualisations")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"#### Histogram of {filter_col}")
                    hist = px.histogram(filtered_df, x=filter_col, nbins=25, template="plotly_white")
                    hist.update_layout(height=400)
                    st.plotly_chart(hist, use_container_width=True)

                with c2:
                    st.markdown("#### Crossplot")
                    if len(numeric_cols) >= 2:
                        if "Porosity_pct" in numeric_cols and "Permeability_mD" in numeric_cols:
                            x_default = numeric_cols.index("Porosity_pct")
                            x_axis = st.selectbox("X-axis", numeric_cols, index=x_default, key="x_axis")
                            y_options = [c for c in numeric_cols if c != x_axis]
                            y_default = y_options.index("Permeability_mD") if "Permeability_mD" in y_options else 0
                        else:
                            x_axis = st.selectbox("X-axis", numeric_cols, index=0, key="x_axis")
                            y_options = [c for c in numeric_cols if c != x_axis]
                            y_default = 0
                        y_axis = st.selectbox("Y-axis", y_options, index=y_default, key="y_axis")
                        log_y = st.checkbox("Use logarithmic Y-axis", value=(y_axis == "Permeability_mD"))
                        crossplot = px.scatter(
                            filtered_df, x=x_axis, y=y_axis, template="plotly_white", log_y=log_y
                        )
                        crossplot.update_layout(height=400)
                        st.plotly_chart(crossplot, use_container_width=True)
                    else:
                        st.info("At least two numeric columns are required for a crossplot.")

                st.markdown("### ⬇️ Download Filtered Data")
                buffer = io.StringIO()
                filtered_df.to_csv(buffer, index=False)
                st.download_button(
                    "Download filtered data as CSV", data=buffer.getvalue(),
                    file_name="filtered_rock_fluid_data.csv", mime="text/csv",
                )
except pd.errors.EmptyDataError:
    st.warning("⚠️ The uploaded CSV is empty or unreadable.")
except pd.errors.ParserError:
    st.warning("⚠️ The CSV could not be parsed. Check delimiters, quotes, and row formatting.")
except (TypeError, ValueError) as exc:
    st.warning(f"⚠️ The data could not be processed: {exc}")
