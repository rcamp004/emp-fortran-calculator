import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import json  # For pretty-printing JSON

# Backend URL
API_URL = "http://emp-backend:8000/run"

# Title
st.title("EMP Fortran Calculator")

# Input form
with st.form("emp_form"):
    st.subheader("Input Parameters")
    x = st.number_input("X Target Coordinate (meters)", value=0.0, format="%.5f")
    y = st.number_input("Y Target Coordinate (meters)", value=0.0, format="%.5f")
    z = st.number_input("Z Target Coordinate (meters)", value=0.0, format="%.5f")
    hob = st.number_input("Height of Burst (km)", value=100.0, format="%.5f")
    gammaYield = st.number_input("Gamma Yield (kT)", value=0.001, format="%.5f")
    bField = st.number_input("B Field (kW/m²)", value=0.00002, format="%.5E")
    bAngle = st.number_input("B Angle (degrees)", value=20.0, format="%.5f")
    nSteps = st.number_input("Number of Steps", min_value=10, max_value=10000, value=200, step=10)
    outputControl = st.selectbox("Output Control", options=[0, 1, 2], index=0)
    ap = st.number_input("AP parameter", value=2.2, format="%.5f")
    bp = st.number_input("BP parameter", value=0.25, format="%.5f")
    rnp = st.number_input("RNP parameter", value=5.62603, format="%.5f")
    top = st.number_input("TOP parameter", value=2.24, format="%.5f")

    # Checkbox for enabling debug mode
    debug_mode = st.checkbox("Show API JSON Payload (Debug Mode)", value=False)

    submitted = st.form_submit_button("Calculate EMP")

# API call and result display
if submitted:
    payload = {
        "x": x, "y": y, "z": z, "hob": hob, "gammaYield": gammaYield,
        "bField": bField, "bAngle": bAngle, "nSteps": nSteps,
        "outputControl": outputControl, "ap": ap, "bp": bp, "rnp": rnp, "top": top
    }

    # If debug mode is enabled, display the payload before sending
    if debug_mode:
        st.subheader("API JSON Payload (Debug)")
        st.json(payload)  # Nicely formatted JSON display

    with st.spinner("Running simulation. Please wait..."):
        try:
            response = requests.post(API_URL, json=payload)

            if response.ok:
                result = response.json()
                st.success("Simulation complete!")

                st.subheader("Results")
                st.write(f"**Peak E-Field:** {result['peakEField']:.3f} V/m")
                st.write(f"**Peak Time:** {result['peakTime']:.2f} shakes")

                df = pd.DataFrame(result['timeSeriesData'])
                fig = px.line(df, x='time', y='eField', title="EMP E-Field over Time",
                              labels={'time': 'Time (shakes)', 'eField': 'E-Field (V/m)'},
                              markers=True)
                fig.update_traces(line=dict(width=3))
                fig.update_layout(hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Simulation failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
