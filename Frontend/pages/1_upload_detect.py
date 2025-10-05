import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page Styling
st.set_page_config(
    page_title="Stellar Signal",
    page_icon="Frontend/images/logo.png",
    layout="centered"
)
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
    .stHeading {
        margin-bottom: 20px;    
    }
    .result-box {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #6C63FF;
        box-shadow: 0 0 20px rgba(108, 99, 255, 0.3);
    }
    .confirmed {
        color: #00FF88;
        font-size: 24px;
        font-weight: bold;
    }
    .false-positive {
        color: #FF6B6B;
        font-size: 24px;
        font-weight: bold;
    }
    .probability {
        font-size: 36px;
        font-weight: bold;
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# Page Title
st.title("Upload & Detect")
st.markdown("### Search for exoplanet candidates by ID or name")

# Check API health
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health_response.status_code == 200:
        health_data = health_response.json()
        if health_data.get("status") == "healthy":
            st.success(f"API Connected | {health_data.get('records', 0)} planets in database")
        else:
            st.warning("API connected but data not loaded")
    else:
        st.error("API is not responding properly")
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to API. Make sure the backend is running on http://localhost:8000")
except Exception as e:
    st.error(f"Error: {str(e)}")

# Input Section
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    planet_query = st.text_input(
        "Enter Planet ID or Name",
        placeholder="e.g., 10811496 or K00753.01",
        help="You can search by numeric ID or KOI name (e.g., K00753.01)"
    )

with col2:
    st.write("")
    st.write("")
    search_button = st.button("Detect Planet", use_container_width=True)

# Display Statistics
try:
    stats_response = requests.get(f"{API_BASE_URL}/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        
        st.markdown("### Database Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Objects", f"{stats['total_objects']:,}")
        with col2:
            st.metric("Confirmed Candidates", stats['confirmed_candidates'])
        with col3:
            st.metric("False Positives", stats['false_positives'])
        with col4:
            st.metric("Avg Probability", f"{stats['average_probability']:.2%}")
except:
    pass

# Search Logic
if search_button and planet_query:
    with st.spinner("Analyzing planet data..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/detect",
                json={"query": planet_query},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display Results
                st.markdown("---")
                st.markdown("### Detection Results")
                
               
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {result['name']}")
                    st.markdown(f"**ID:** {result['id']}")
                    st.markdown(f"**Disposition:** {result['predicted_disposition']}")
                    
                    if result['is_confirmed']:
                        st.markdown('<p class="confirmed">CONFIRMED CANDIDATE</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="false-positive">FALSE POSITIVE</p>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### Probability")
                    prob_percent = result['probability_confirmed'] * 100
                    st.markdown(f'<p class="probability">{prob_percent:.1f}%</p>', unsafe_allow_html=True)
                    st.markdown(f"**Confidence:** {result['confidence_level']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Probability Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=prob_percent,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confirmation Probability", 'font': {'size': 24, 'color': 'white'}},
                    delta={'reference': 50, 'increasing': {'color': "#00FF88"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#FFD700"},
                        'bgcolor': "rgba(0,0,0,0.3)",
                        'borderwidth': 2,
                        'bordercolor': "white",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(255, 107, 107, 0.3)'},
                            {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.3)'},
                            {'range': [80, 100], 'color': 'rgba(0, 255, 136, 0.3)'}
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
                
                # Additional Information
                st.markdown("### Interpretation")
                
                if result['probability_confirmed'] >= 0.75:
                    st.info("**High Confidence**: This object shows strong characteristics of an exoplanet candidate. Further validation recommended.")
                elif result['probability_confirmed'] >= 0.5:
                    st.warning("**Medium Confidence**: This object shows some exoplanet-like characteristics but requires additional analysis.")
                else:
                    st.error("**Low Confidence**: This object is likely a false positive. Transit signal may be caused by stellar activity or instrumental noise.")
                
                # Comparison Chart
                st.markdown("### Probability Distribution")
                
                fig2 = go.Figure()
                
                categories = ['This Planet', 'Average', 'High Threshold']
                values = [prob_percent, 50, 75]
                colors = ['#FFD700', '#6C63FF', '#00FF88']
                
                fig2.add_trace(go.Bar(
                    x=categories,
                    y=values,
                    marker_color=colors,
                    text=[f"{v:.1f}%" for v in values],
                    textposition='outside'
                ))
                
                fig2.update_layout(
                    title="Probability Comparison",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(20,20,30,0.8)",
                    font={'color': "white"},
                    yaxis={'title': 'Probability (%)', 'range': [0, 100]},
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            elif response.status_code == 404:
                st.error("Planet not found. Please check the ID or name and try again.")
                st.info("**Tip**: Try searching with the full KOI name (e.g., K00753.01) or numeric ID.")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure the backend is running.")
            st.code("cd backend\npython -m uvicorn main:app --reload", language="bash")
        except requests.exceptions.Timeout:
            st.error(" Request timed out. Please try again.")
        except Exception as e:
            st.error(f" An error occurred: {str(e)}")

elif search_button and not planet_query:
    st.warning("Please enter a planet ID or name to search.")

# Sample Planets Section
st.markdown("---")
st.markdown("### Sample Planets to Try")

sample_planets = [
    {"id": "10811496", "name": "K00753.01", "type": "False Positive"},
    {"id": "11818800", "name": "K00777.01", "type": "False Positive"},
    {"id": "10319385", "name": "K01169.01", "type": "Confirmed"},
]
cols = st.columns(len(sample_planets))
for i, planet in enumerate(sample_planets):
    with cols[i]:
        st.info(f"**{planet['name']}**\nID: {planet['id']}\nType: {planet['type']}")
