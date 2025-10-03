# pages/1_upload_simulated.py
import streamlit as st
import pandas as pd
import plotly.express as px


st.title(" Upload Simulated Data")
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

st.markdown("""
    ###  Analyze Your Simulation  
    Upload the **CSV file you generated from the Simulate & Inject page** to see how the system processes and interprets the data.  
    """)

uploaded_file = st.file_uploader("Upload your simulated light curve (CSV)", type=["csv"])

if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.dataframe(df.head())

        # Plot uploaded light curve
        fig = px.line(df, x="Time", y="Brightness",
                      title="Uploaded Simulated Light Curve",
                      template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Placeholder analysis
        st.subheader(" AI Analysis Result")
        st.success(" Planet Transit Detected with 91% Confidence")
        st.metric("Estimated Orbital Period", "27 days")
else:
        st.info("⬆️ Please upload a CSV file generated from the Simulate & Inject page.")

