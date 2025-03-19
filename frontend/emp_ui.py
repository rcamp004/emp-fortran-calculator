import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import json
import os

# Backend URL
API_URL = "http://emp-backend:8000/run"

# Title
st.title("EMP Fortran Calculator")

# Test Mode Toggle
test_mode = st.checkbox("Enable Test Mode (Use Expected Output)", value=False)

def show_debug_info(data, title="Debug Info"):
    """ Function to display debugging information in Streamlit """
    st.subheader(title)
    
    if isinstance(data, dict):  # JSON data
        st.json(data)
    elif isinstance(data, pd.DataFrame):  # Pandas DataFrame
        st.write(data)
        st.write("DataFrame Columns:", data.columns.tolist())

def plot_emp_graph(df, title="EMP E-Field over Time"):
    """ Function to plot the EMP E-Field time series graph """
    fig = px.line(df, x='time', y='eField', title=title,
                  labels={'time': 'Time (shakes)', 'eField': 'E-Field (V/m)'},
                  markers=True)
    fig.update_traces(line=dict(width=3))
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

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

# Load expected output if Test Mode is enabled
if test_mode:
    expected_output_file = "/app/tests/expected_output.json"
    st.write(f"Checking if {expected_output_file} exists: {os.path.exists(expected_output_file)}")
    
    if os.path.exists(expected_output_file):
        with open(expected_output_file, "r") as f:
            result = json.load(f)

        st.success("Loaded Expected Output Data!")
        st.subheader("Results (Test Mode)")
        st.write(f"**Peak E-Field:** {result['peakEField']:.3f} V/m")
        st.write(f"**Peak Time:** {result['peakTime']:.2f} shakes")

        df = pd.DataFrame(result['timeSeriesData'])

        if debug_mode:
            show_debug_info(result, title="DEBUG: Loaded Expected Output Data")
            show_debug_info(df, title="DEBUG: Dataframe Contents")

        # Call the plotting function
        plot_emp_graph(df, title="EMP E-Field over Time (Test Mode)")
    else:
        st.error("Test Mode is enabled, but `tests/expected_output.json` was not found.")

# If not in Test Mode, send API request
elif submitted:
    payload = {
        "x": x, "y": y, "z": z, "hob": hob, "gammaYield": gammaYield,
        "bField": bField, "bAngle": bAngle, "nSteps": nSteps,
        "outputControl": outputControl, "ap": ap, "bp": bp, "rnp": rnp, "top": top
    }

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

                if debug_mode:
                    show_debug_info(payload, title="DEBUG: API JSON Payload (Debug Mode)")
                    show_debug_info(df, title="DEBUG: Dataframe Contents")

                # Call the plotting function
                plot_emp_graph(df, title="EMP E-Field over Time")
            else:
                st.error(f"Simulation failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
