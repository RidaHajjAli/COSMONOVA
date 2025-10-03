import streamlit as st
import pandas as pd
import io

# --- Page Styling ---
st.markdown("""
<style>
    .stAppDeployButton {visibility: hidden;}
    .stMainMenu {visibility: hidden;}
    /* Page Background */
    .stAppViewContainer {
        background-color: #0B0C10; 
        background-image: url("https://img.freepik.com/free-vector/watercolor-galaxy-background-with-stars_23-2149247760.jpg?semt=ais_hybrid&w=740&q=80");
        background-size: cover; 
        background-position: center; 
        background-repeat: no-repeat; 
        background-attachment: fixed; 
    }
            /* Header Transparent */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    .stHeading{
        margin-bottom:20px;    
            }
</style>
""", unsafe_allow_html=True)


# --- Page Title ---
st.markdown("<p class='title'> Simulate & Inject</p>", unsafe_allow_html=True)
st.write("Provide **KOI-style parameters** to generate a synthetic dataset for testing detection.")

# --- Input Section ---
st.subheader(" Planet Transit Parameters")
koi_period = st.number_input("koi_period (days)", min_value=0.1, max_value=1000.0, value=365.0, step=0.1)
koi_time0bk = st.number_input("koi_time0bk (BKJD)", min_value=0.0, max_value=5000.0, value=134.5, step=0.1)
koi_impact = st.slider("koi_impact (0 = central, 1 = grazing)", 0.0, 1.0, 0.5)
koi_duration = st.number_input("koi_duration (hours)", min_value=0.1, max_value=72.0, value=10.0, step=0.1)
koi_depth = st.number_input("koi_depth (ppm)", min_value=10, max_value=100000, value=500, step=10)
koi_prad = st.number_input("koi_prad (Earth radii)", min_value=0.1, max_value=20.0, value=1.0, step=0.1)
koi_model_snr = st.number_input("koi_model_snr", min_value=0.1, max_value=1000.0, value=25.0, step=0.1)

st.subheader(" Stellar Properties")
koi_steff = st.number_input("koi_steff (K)", min_value=2000, max_value=10000, value=5778, step=10)
koi_slogg = st.number_input("koi_slogg (log g, cm/s²)", min_value=0.0, max_value=10.0, value=4.44, step=0.01)
koi_srad = st.number_input("koi_srad (Solar radii)", min_value=0.1, max_value=50.0, value=1.0, step=0.1)
koi_kepmag = st.number_input("koi_kepmag (Kepler magnitude)", min_value=5.0, max_value=20.0, value=12.0, step=0.1)

# --- Generate Button ---
if st.button(" Generate CSV"):
    # Create DataFrame
    data = {
        "koi_period": [koi_period],
        "koi_time0bk": [koi_time0bk],
        "koi_impact": [koi_impact],
        "koi_duration": [koi_duration],
        "koi_depth": [koi_depth],
        "koi_prad": [koi_prad],
        "koi_model_snr": [koi_model_snr],
        "koi_steff": [koi_steff],
        "koi_slogg": [koi_slogg],
        "koi_srad": [koi_srad],
        "koi_kepmag": [koi_kepmag],
    }

    df = pd.DataFrame(data)

    # Save to CSV in memory
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.success("✅ CSV generated successfully!")

    # Download button
    st.download_button(
        label="📥 Download Simulated CSV",
        data=buffer,
        file_name="simulated_exoplanet.csv",
        mime="text/csv"
    )

    # Show preview table
    st.subheader("🔍 Preview of Generated Data")
    st.dataframe(df)
