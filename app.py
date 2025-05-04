import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image
import tempfile
from auth import login_page, register_page, logout
from streamlit_lottie import st_lottie
import requests
import os
import plotly.graph_objects as go
import pandas as pd

# --- Authentication ---
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["login"])[0]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if not st.session_state.logged_in:
    if current_page == "register":
        register_page()
    else:
        login_page()
    st.stop()
st.sidebar.button("🚪 Logout", on_click=logout)

# --- Background Styling ---
def set_background(image_url):
    st.markdown(
        f"""<style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        .main {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 1rem;
        }}
        .block-container {{
            padding-top: 1rem;
        }}
        </style>""",
        unsafe_allow_html=True
    )

# Set healthcare/medical theme background
set_background("https://img.freepik.com/free-vector/clean-medical-background_53876-116875.jpg")

# --- Helper to Load Lottie Files ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Roboflow Setup ---
CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key="0wCuSlFsDHkh6SSLb5iq"
)

def classify_image(image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        image.save(temp_file, format='JPEG')
        temp_file_path = temp_file.name
    result = CLIENT.infer(temp_file_path, model_id="handetect-av6rs/1")
    return result

# --- Precaution Tips ---
# --- Precaution Tips ---
DISEASE_PRECAUTIONS = {
    "parkinson disease": [
        "🧘‍♀️ Exercise regularly with hand/arm stretches.",
        "💊 Take medications on time.",
        "🧑‍⚕️ Attend physiotherapy sessions.",
        "🛡 Use assistive devices for safety.",
        "🥗 Eat fiber-rich, balanced meals.",
        "🧠 Practice stress-reducing activities.",
        "🏠 Create a fall-safe environment at home."
    ],
    "essential tremor": [
        "☕️ Avoid caffeine and stimulants.",
        "🧘‍♂️ Practice relaxation and breathing exercises.",
        "💊 Take beta-blockers or prescribed medication.",
        "🛠 Use heavier utensils or weighted pens.",
        "🧑‍⚕️ Consider deep brain stimulation (DBS) if tremors are severe."
    ],
    "cerebral palsy": [
        "🏋️‍♀️ Engage in regular physical and occupational therapy.",
        "🚶‍♂️ Use assistive mobility devices if needed.",
        "🧠 Early intervention therapies for young children.",
        "🧘‍♀️ Maintain joint flexibility with stretching routines.",
        "🥗 Eat a nutritious, well-balanced diet."
    ],
    "dystonia": [
        "🧘‍♀️ Reduce stress with mindfulness and relaxation techniques.",
        "💉 Use botulinum toxin injections if prescribed.",
        "🛀 Apply heat or massage to reduce muscle stiffness.",
        "🧑‍⚕️ Attend regular rehabilitation or physiotherapy sessions.",
        "🧢 Use sensory tricks (like touching chin or head) to ease muscle spasms."
    ],
    "huntington disease": [
        "🧠 Attend cognitive behavioral therapy sessions.",
        "🥗 Maintain a high-calorie, nutritious diet.",
        "🚶‍♂️ Regular physical exercise to improve mobility.",
        "🧘‍♂️ Manage psychiatric symptoms with prescribed medications.",
        "🗓 Keep a structured daily schedule to support memory and cognition."
    ],
    "normal": [
        "✅ No abnormalities detected. Maintain healthy habits.",
        "🏃‍♂️ Stay physically active daily.",
        "🥗 Eat balanced meals rich in fruits and vegetables.",
        "🧘‍♀️ Manage stress with mindfulness practices.",
        "💧 Stay hydrated and sleep well."
    ]
}


def show_precautions(result):
    predictions = result.get("predictions", [])
    if not predictions:
        st.info("No predictions found.")
        return

    top = max(predictions, key=lambda x: x['confidence'])
    label = top['class'].strip().lower()
    tips = DISEASE_PRECAUTIONS.get(label, ["No specific precautions available."])

    shield = load_lottie_url("https://assets8.lottiefiles.com/packages/lf20_w51pcehl.json")  # permanent shield animation
    if shield:
        st_lottie(shield, height=100)

    with st.container():
        st.markdown(f"### 🛡 Precautions for {label.title()}")
        for tip in tips:
            st.markdown(f"- {tip}")

# --- Show Predictions in Table ---
def show_predictions(result):
    predictions = result.get("predictions", [])
    if not predictions:
        st.warning("No predictions available.")
        return

    top3 = sorted(predictions, key=lambda x: x["confidence"], reverse=True)[:3]

    table_data = pd.DataFrame({
        "Disorder": [p["class"].title() for p in top3],
        "Confidence (%)": [round(p["confidence"] * 100, 2) for p in top3]
    })

    st.markdown("### 📝 Top 3 Predictions (Table View)")
    st.dataframe(table_data.style.background_gradient(cmap='Blues'), use_container_width=True)

    fig = go.Figure(
        data=[go.Bar(
            x=table_data["Confidence (%)"],
            y=table_data["Disorder"],
            orientation='h',
            text=[f"{c}%" for c in table_data["Confidence (%)"]],
            textposition='auto',
            marker_color='mediumseagreen'
        )]
    )
    fig.update_layout(
        title="Top 3 Predictions",
        xaxis_title="Confidence (%)",
        yaxis_title="Disorder",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Page Content ---
with st.container():
    st.title("🖐 Neurological Hand Disorder Detection")

    # Left and Right Animations
    col1, col2 = st.columns([1, 2])
    with col1:
        left_anim = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_LU6TzG.json")  # Brain analysis
        if left_anim:
            st_lottie(left_anim, height=250)
    
    with col2:
        st.subheader("📤 Upload a hand image (JPG or PNG)")
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="🖼 Uploaded Image", use_container_width=True)

            if st.button("🔍 Analyze Image", use_container_width=True):
                with st.spinner("🧠 Processing..."):
                    loading_anim = load_lottie_url("https://assets2.lottiefiles.com/private_files/lf30_m6j5igxb.json")
                    if loading_anim:
                        st_lottie(loading_anim, height=100)
                    result = classify_image(img)
                    st.subheader("📊 Prediction Results")
                    show_predictions(result)
                    show_precautions(result)

# --- Educational Section ---
st.markdown("## 🧠 Understanding Parkinson’s Disease")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Parkinson’s disease** is a chronic neurological disorder that affects motor control due to the loss of dopamine-producing neurons in the brain.

    ### 🧬 What Happens?
    - Neurons in the *substantia nigra* degenerate.
    - Leads to motor symptoms and non-motor complications.

    ### ⚠ Common Symptoms:
    - Tremors in hands or legs
    - Slowed movement (bradykinesia)
    - Muscle rigidity
    - Posture instability
    - Speech issues

    ### 🛠 Management Strategies:
    - Medications like **Levodopa**
    - **Deep Brain Stimulation (DBS)**
    - Regular **exercise** and **therapy**
    """)

with col2:
    brain_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_4kx2q32n.json")  # brain neuron animation
    if brain_anim:
        st_lottie(brain_anim, height=250)

