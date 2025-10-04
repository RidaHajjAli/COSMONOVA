import streamlit as st
import pandas as pd
import io
import requests
import plotly.graph_objects as go

# API Configuration
API_BASE_URL = "http://localhost:8000"

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
    .prediction-box {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #6C63FF;
        box-shadow: 0 0 20px rgba(108, 99, 255, 0.3);
    }
    .confirmed {
        color: #00FF88;
        font-size: 28px;
        font-weight: bold;
    }
    .false-positive {
        color: #FF6B6B;
        font-size: 28px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Page Title ---
st.title("Simulate & Inject")
st.write("Provide **KOI-style parameters** to generate a synthetic dataset and get AI predictions.")

# Check API health
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health_response.status_code == 200:
        health_data = health_response.json()
        if health_data.get("model_loaded"):
            st.success(f"✅ AI Model Ready | {health_data.get('features', 0)} features loaded")
        else:
            st.warning("⚠️ Model not loaded. Prediction unavailable.")
    else:
        st.error("❌ API is not responding properly")
except:
    st.error("❌ Cannot connect to API. Make sure the backend is running.")

st.markdown("---")

# --- Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Planet Transit Parameters")
    koi_period = st.number_input("koi_period (days)", min_value=0.1, max_value=1000.0, value=365.0, step=0.1)
    koi_time0bk = st.number_input("koi_time0bk (BKJD)", min_value=0.0, max_value=5000.0, value=134.5, step=0.1)
    koi_impact = st.slider("koi_impact (0 = central, 1 = grazing)", 0.0, 1.0, 0.5)
    koi_duration = st.number_input("koi_duration (hours)", min_value=0.1, max_value=72.0, value=10.0, step=0.1)
    koi_depth = st.number_input("koi_depth (ppm)", min_value=10, max_value=100000, value=500, step=10)
    koi_prad = st.number_input("koi_prad (Earth radii)", min_value=0.1, max_value=20.0, value=1.0, step=0.1)

with col2:
    st.subheader("Stellar Properties")
    koi_model_snr = st.number_input("koi_model_snr", min_value=0.1, max_value=1000.0, value=25.0, step=0.1)
    koi_steff = st.number_input("koi_steff (K)", min_value=2000, max_value=10000, value=5778, step=10)
    koi_slogg = st.number_input("koi_slogg (log g, cm/s²)", min_value=0.0, max_value=10.0, value=4.44, step=0.01)
    koi_srad = st.number_input("koi_srad (Solar radii)", min_value=0.1, max_value=50.0, value=1.0, step=0.1)
    koi_kepmag = st.number_input("koi_kepmag (Kepler magnitude)", min_value=5.0, max_value=20.0, value=12.0, step=0.1)

st.markdown("---")

# --- Action Buttons ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    predict_button = st.button("Predict with AI", use_container_width=True, type="primary")

with col2:
    generate_button = st.button("Generate CSV", use_container_width=True)

with col3:
    if st.button("Reset Values", use_container_width=True):
        st.rerun()

# Create DataFrame from inputs
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

# --- Predict with AI ---
if predict_button:
    with st.spinner("Running AI prediction..."):
        try:
            # Prepare data for API
            input_data = {
                "koi_period": koi_period,
                "koi_time0bk": koi_time0bk,
                "koi_impact": koi_impact,
                "koi_duration": koi_duration,
                "koi_depth": koi_depth,
                "koi_prad": koi_prad,
                "koi_model_snr": koi_model_snr,
                "koi_steff": koi_steff,
                "koi_slogg": koi_slogg,
                "koi_srad": koi_srad,
                "koi_kepmag": koi_kepmag,
            }
            
            # Call prediction API
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=input_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                st.markdown("---")
                st.markdown("##  AI Prediction Results")
                
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if result['is_confirmed']:
                        st.markdown('<p class="confirmed">✅ CONFIRMED CANDIDATE</p>', unsafe_allow_html=True)
                        st.markdown(f"**Prediction:** {result['prediction']}")
                    else:
                        st.markdown('<p class="false-positive">❌ FALSE POSITIVE</p>', unsafe_allow_html=True)
                        st.markdown(f"**Prediction:** {result['prediction']}")
                    
                    st.markdown(f"**Confidence Level:** {result['confidence_level']}")
                
                with col2:
                    st.metric("Candidate Probability", f"{result['probability_candidate']*100:.1f}%")
                    st.metric("False Positive Probability", f"{result['probability_false_positive']*100:.1f}%")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Probability Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['probability_candidate'] * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Candidate Probability", 'font': {'size': 24, 'color': 'white'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#FFD700"},
                        'bgcolor': "rgba(0,0,0,0.3)",
                        'borderwidth': 2,
                        'bordercolor': "white",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(255, 107, 107, 0.3)'},
                            {'range': [50, 75], 'color': 'rgba(255, 215, 0, 0.3)'},
                            {'range': [75, 100], 'color': 'rgba(0, 255, 136, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={'color': "white", 'family': "Arial"},
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretation
                st.markdown("###  AI Interpretation")
                
                prob_percent = result['probability_candidate'] * 100
                
                if prob_percent >= 75:
                    st.success(" **High Confidence Detection**: This signal shows strong characteristics of an exoplanet transit. The AI model is highly confident this is a genuine planetary candidate.")
                elif prob_percent >= 50:
                    st.warning(" **Medium Confidence**: The signal shows some exoplanet-like characteristics, but additional validation is recommended. Consider checking for stellar activity or instrumental artifacts.")
                else:
                    st.error(" **Likely False Positive**: The AI model suggests this signal is probably not a genuine planetary transit. It may be caused by stellar variability, eclipsing binaries, or instrumental noise.")
                
                # Comparison Chart
                st.markdown("###  Probability Breakdown")
                
                fig2 = go.Figure(data=[
                    go.Bar(
                        x=['False Positive', 'Candidate'],
                        y=[result['probability_false_positive'] * 100, result['probability_candidate'] * 100],
                        marker_color=['#FF6B6B', '#00FF88'],
                        text=[f"{result['probability_false_positive']*100:.1f}%", 
                              f"{result['probability_candidate']*100:.1f}%"],
                        textposition='outside'
                    )
                ])
                
                fig2.update_layout(
                    title="Classification Probabilities",
                    yaxis={'title': 'Probability (%)', 'range': [0, 100]},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(20,20,30,0.8)",
                    font={'color': "white"},
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            else:
                st.error(f"❌ Prediction failed: {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the backend is running.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# --- Generate CSV ---
if generate_button:
    # Convert DataFrame directly to CSV string
    csv_data = df.to_csv(index=False)
    
    st.success("✅ CSV generated successfully!")
    
    # Download button
    st.download_button(
        label="📥 Download Simulated CSV",
        data=csv_data,
        file_name="simulated_exoplanet.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Show preview table
    st.subheader("🔍 Preview of Generated Data")
    st.dataframe(df, use_container_width=True)


# --- Input Data Preview ---
st.markdown("---")
st.subheader(" Current Input Parameters")
st.dataframe(df, use_container_width=True)

# --- Information Section ---
st.markdown("---")
st.markdown("### How It Works")

with st.expander(" About the Parameters"):
    st.markdown("""
    **Transit Parameters:**
    - **koi_period**: Orbital period in days
    - **koi_time0bk**: Time of first transit in Barycentric Kepler Julian Date
    - **koi_impact**: Impact parameter (0 = central transit, 1 = grazing)
    - **koi_duration**: Transit duration in hours
    - **koi_depth**: Transit depth in parts per million (ppm)
    - **koi_prad**: Planet radius in Earth radii
    
    **Stellar Parameters:**
    - **koi_model_snr**: Signal-to-noise ratio
    - **koi_steff**: Stellar effective temperature in Kelvin
    - **koi_slogg**: Stellar surface gravity
    - **koi_srad**: Stellar radius in Solar radii
    - **koi_kepmag**: Kepler magnitude (brightness)
    """)

with st.expander(" About the AI Model"):
    st.markdown("""
    The AI model uses **CatBoost**, a gradient boosting algorithm trained on thousands of Kepler 
    exoplanet observations. It analyzes the input parameters to determine if the signal is likely 
    a genuine exoplanet candidate or a false positive.
    
    **Classification Criteria:**
    - **Candidate Probability > 75%**: High confidence detection
    - **Candidate Probability 50-75%**: Medium confidence
    - **Candidate Probability < 50%**: Likely false positive
    """)

