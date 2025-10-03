import streamlit as st
import plotly.graph_objects as go

# ================================
# Page Config (must be first)
# ================================
st.set_page_config(
    page_title="Stellar Signal",
    page_icon="✨",
    layout="wide"
)

# ================================
# Custom CSS Styling
# ================================
st.markdown("""
<style>
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

    /* Title */
    h1 {
        text-align: center;
        color: #FFFFFF;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 2px 2px 8px #6C63FF;
    }

    /* Metrics styling */
    .stMetric {
        background: rgba(20,20,30,0.8);
        border-radius: 15px;
        padding: 10px;
        color: #FFFFFF;
        box-shadow: 0px 0px 10px #6C63FF;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #11121a;
        color: #FFFFFF;
    }

    .css-1d391kg {
        color: #FF6FB5 !important;
    }

    /* Hide Streamlit's extra buttons */
    .stAppDeployButton {visibility: hidden;}
    .stMainMenu {visibility: hidden;}
     div.stButton > button {
        background-color: #4E56C0;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        transition: 0.3s;
        margin-left:60px;
    }
    .stHeading{
            margin-left:50px;}

    .stImage{
            margin-left:100px;}
    div.stButton > button:hover {
        background-color: #3c429c;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)


# ================================
# Pages
# ================================
def show_home():
    st.title("Stellar Signal: Exoplanet Detection")

    # Metrics Section
    col1, col2, col3 = st.columns(3)
    col1.metric("Confirmed Planets", "2,340")
    col2.metric("Detection Accuracy", "96.2%")
    col3.metric("Kepler Objects", "9,564")

    st.markdown("""
    ##  Welcome!
    Use this platform to detect exoplanets using AI.  
    Upload telescope data, simulate signals, and explore the universe. 
    """)

    st.markdown("Explore the Features")

    # Navigation Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3209/3209265.png", width=120)
        st.subheader("Upload & Detect")
        st.write("Upload telescope datasets and let AI detect possible exoplanet signals.")
        if st.button("Go to Upload & Detect"):
            st.switch_page("pages/1_upload_detect.py")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2907/2907253.png", width=120)
        st.subheader("Simulate & Inject")
        st.write("Simulate planetary transit signals and inject them into light curves.")
        if st.button("Go to Simulate & Inject"):
            st.switch_page("2_simulate_inject.py")

    with col3:
        st.image("image.png", width=120)
        st.subheader("Explanation & Visualization")
        st.write("Understand how detections work and view data visualizations of signals.")
        if st.button("Go to Explanation & Visualization"):
            st.switch_page("3_explain_visualize.py")


show_home()