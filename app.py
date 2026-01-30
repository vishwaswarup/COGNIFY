
import streamlit as st
import textwrap
import google.generativeai as genai
import time
import os

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Cognify",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        /* DARK THEME */
        .stApp {
            background-color: #0f172a;
            background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
        }
        
        /* ENSURE SIDEBAR IS VISIBLE */
        [data-testid="stSidebar"] {
            visibility: visible !important;
            display: block !important;
            background-color: #0f172a !important;
        }
        
        /* GLASS CARDS */
        .glass-card {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease;
        }
        .glass-card:hover {
            border-color: rgba(6, 182, 212, 0.3);
        }
        
        /* TEXT STYLES */
        h1, h2, h3 { font-weight: 800; letter-spacing: -0.02em; }
        
        .gradient-text {
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .highlight { color: #38bdf8; font-weight: 600; }
        
        /* BUTTONS */
        .stButton>button {
            background: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            border-color: #38bdf8;
            color: #38bdf8;
            background: #0f172a;
        }
        
        /* PROGRESS BAR */
        .progress-container {
            background: #334155;
            height: 8px;
            border-radius: 4px;
            margin-top: 5px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
state_defaults = {
    "history": {"topics_completed": [], "hesitation_events": 0, "incorrect_answers": [], "weak_concepts": []},
    "score": 0,
    "current_topic": None,
    "start_read_time": None,
    "quiz_submitted": False,
    "ai_help_triggered": False,
    "page": "home"
}

for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- EARLY UI RENDER (IMPORTANT FOR CLOUD) ---
inject_custom_css()

# --- SIDEBAR RENDER (ALWAYS VISIBLE) ---
with st.sidebar:
    st.markdown("## 🎓 Student Profile")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Topics", len(st.session_state.history['topics_completed']), "/ 4")
    with col2:
        st.metric("Score", st.session_state.score, "pts")
    
    st.markdown("---")
    
    # Progress bar
    progress_pct = min(len(st.session_state.history['topics_completed']) * 25, 100) / 100
    st.progress(progress_pct)
    
    st.markdown("---")
    
    if st.button("🏠 Return to Home", use_container_width=True, key="sidebar_home_btn"):
        st.session_state.page = "home"
        st.rerun()

# API Config

# --- API CONFIG ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.error("⚠️ API key not configured")
        st.info("Add GEMINI_API_KEY in Streamlit → Settings → Secrets")

    st.error("Setup Error: API Key missing")
    st.stop()



genai.configure(api_key=api_key)
# Using gemma-3-1b-it as discovered
model = genai.GenerativeModel('gemma-3-1b-it')

# --- 2. CONTENT ---
# --- 2. CONTENT ---
TOPICS = {
    "Photosynthesis": {
        "icon": "🌱",
        "desc": "How plants create energy from sunlight.",
        "notes": """
        <h3 class="gradient-text" style="font-size: 1.5rem; margin-bottom: 10px;">Photosynthesis</h3>
        <p><strong>Photosynthesis</strong> is the process by which green plants use sunlight to synthesize nutrients.</p>
        
        <ul style="margin-left: 20px; color: #cbd5e1;">
            <li><strong>Inputs</strong>: Carbon Dioxide + Water + Light</li>
            <li><strong>Location</strong>: Chloroplasts (containing chlorophyll)</li>
            <li><strong>Outputs</strong>: Glucose (Energy) + Oxygen</li>
        </ul>
        
        <blockquote style="border-left: 3px solid #38bdf8; padding-left: 10px; margin-top: 15px; color: #94a3b8; font-style: italic;">
            It is essentially how plants convert light energy into chemical energy.
        </blockquote>
        """,
        "mcqs": [
            {"question": "What is the primary byproduct?", "options": ["Carbon Dioxide", "Oxygen", "Nitrogen"], "correct": "Oxygen", "concept": "Outputs"},
            {"question": "Where does this process take place?", "options": ["Mitochondria", "Chloroplasts", "Nucleus"], "correct": "Chloroplasts", "concept": "Cell Structures"}
        ]
    },
    "Gravity": {
        "icon": "🍎",
        "desc": "The force of attraction between masses.",
        "notes": """
        <h3 class="gradient-text" style="font-size: 1.5rem; margin-bottom: 10px;">Gravity</h3>
        <p><strong>Gravity</strong> is a fundamental interaction which causes mutual attraction between all things that have mass.</p>
        
        <ul style="margin-left: 20px; color: #cbd5e1;">
            <li><strong>Mass</strong>: The more massive an object, the stronger its pull.</li>
            <li><strong>Distance</strong>: Gravity gets weaker quickly as you move away (Inverse Square Law).</li>
        </ul>
        
        <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center; margin-top: 15px; font-family: monospace;">
            F = G * (m1 * m2) / r²
        </div>
        """,
        "mcqs": [
            {"question": "If you double the distance, gravity becomes...", "options": ["Stronger", "4x Weeker", "No change"], "correct": "4x Weeker", "concept": "Inverse Square"},
            {"question": "What creates gravity?", "options": ["Speed", "Mass", "Color"], "correct": "Mass", "concept": "Mass"}
        ]
    },
    "Water Cycle": {
        "icon": "💧",
        "desc": "The continuous movement of water.",
        "notes": """
        <h3 class="gradient-text" style="font-size: 1.5rem; margin-bottom: 10px;">The Water Cycle</h3>
        <p>Water on Earth is constantly moving and changing states.</p>
        
        <ol style="margin-left: 20px; color: #cbd5e1;">
            <li><strong>Evaporation</strong>: Liquid turns to vapor (driven by the Sun).</li>
            <li><strong>Condensation</strong>: Vapor cools to form clouds.</li>
            <li><strong>Precipitation</strong>: Water falls as rain or snow.</li>
        </ol>
        """,
        "mcqs": [
            {"question": "What drives the water cycle?", "options": ["The Sun", "The Wind", "Gravity"], "correct": "The Sun", "concept": "Energy Source"},
            {"question": "Clouds form via...", "options": ["Evaporation", "Condensation", "Precipitation"], "correct": "Condensation", "concept": "Phase Change"}
        ]
    },
    "Newton's First Law": {
        "icon": "⚽",
        "desc": "The Law of Inertia.",
        "notes": """
        <h3 class="gradient-text" style="font-size: 1.5rem; margin-bottom: 10px;">Newton's First Law</h3>
        <p>An object will remain at rest or in uniform motion unless acted upon by an external force.</p>
        
        <ul style="margin-left: 20px; color: #cbd5e1;">
            <li><strong>Inertia</strong>: The tendency to resist changes in motion.</li>
            <li><strong>Example</strong>: A ball rolling forever until friction stops it.</li>
        </ul>
        """,
        "mcqs": [
            {"question": "This law is also known as...", "options": ["Law of Inertia", "Law of Gravity"], "correct": "Law of Inertia", "concept": "Inertia"},
            {"question": "What is needed to change motion?", "options": ["Mass", "External Force", "Velocity"], "correct": "External Force", "concept": "Forces"}
        ]
    }
}

# --- 3. AI HELPERS ---
def get_ai_response(prompt):
    try: return model.generate_content(prompt).text
    except: return "AI currently unavailable."

# --- 4. UI SECTIONS ---

def show_home():
    inject_custom_css()
    
    st.markdown('<h1 class="gradient-text" style="font-size: 3.5rem; text-align: center; margin-bottom: 10px;">Cognify</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #cbd5e1; font-size: 1.1rem; margin-bottom: 40px;">Select a topic to start learning.</p>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (name, d) in enumerate(TOPICS.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 2rem;">{d['icon']}</div>
                    <div>
                        <h3 style="margin: 0; font-size: 1.2rem;">{name}</h3>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{d['desc']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {name}", key=f"btn_{name}", use_container_width=True):
                st.session_state.current_topic = name
                st.session_state.start_read_time = time.time()
                st.session_state.quiz_submitted = False
                st.session_state.ai_help_triggered = False
                st.session_state.page = "topic"
                st.rerun()

    if st.session_state.history["topics_completed"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 View Progress Summary", type="primary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()

def show_topic():
    inject_custom_css()
    topic = st.session_state.current_topic
    data = TOPICS[topic]
    
    st.markdown(f"<h1>{data['icon']} {topic}</h1>", unsafe_allow_html=True)
    
    # NOTES
    st.markdown("### 📖 Study Notes")
    # Fix: Dedent the HTML content so it's not treated as a code block
    clean_notes = textwrap.dedent(data["notes"]).strip()
    st.markdown(f'<div class="glass-card">{clean_notes}</div>', unsafe_allow_html=True)
    
    # HESITATION LOGIC
    elapsed = time.time() - st.session_state.start_read_time
    if elapsed > 60 and not st.session_state.quiz_submitted:
        if not st.session_state.ai_help_triggered:
            st.session_state.ai_help_triggered = True
        
        st.info("💡 You've been reading for a while. Need any help?")
        
        c1, c2 = st.columns(2)
        if c1.button("✨ Simplify Notes"):
            with st.spinner("Rewriting..."):
                simp = get_ai_response(f"Simplify this explanation clearly:\n{data['notes']}")
                st.markdown(f'<div class="glass-card">{simp}</div>', unsafe_allow_html=True)
        if c2.button("🔑 Get a Hint"):
            with st.spinner("Thinking..."):
                hint = get_ai_response(f"Give a helpful hint about the main concept of:\n{data['notes']}")
                st.markdown(f'<div class="glass-card"><strong>Hint:</strong> {hint}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # QUIZ
    st.subheader("✍️ Quiz")
    with st.form("quiz"):
        user_answers = {}
        for i, q in enumerate(data["mcqs"]):
            st.markdown(f"""
            <div class="glass-card" style="padding: 15px; margin-bottom: 10px;">
                <strong class="highlight">Question {i+1}</strong><br>
                {q['question']}
            </div>
            """, unsafe_allow_html=True)
            
            if st.form_submit_button(f"Give Hint for Q{i+1}"):
                st.caption(f"💡 {get_ai_response(f'Hint for question: {q['question']}')}")

            user_answers[i] = st.radio("Select Answer:", q["options"], key=f"q_{i}", label_visibility="collapsed")
            st.write("")
        
        if st.form_submit_button("Submit Answers", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            
            correct_count = 0
            for i, q in enumerate(data["mcqs"]):
                if user_answers[i] == q["correct"]:
                    correct_count += 1
                    st.success(f"Q{i+1}: Correct")
                else:
                    st.error(f"Q{i+1}: Incorrect")
                    st.session_state.history["weak_concepts"].append(q["concept"])
                    with st.expander("See Explanation"):
                        st.write(get_ai_response(f"Explain why '{user_answers[i]}' is wrong for '{q['question']}'"))
            
            # SCORE UPDATE
            score_gain = correct_count * 10
            st.session_state.score += score_gain
            if score_gain > 0: st.success(f"+{score_gain} Points!")
            
            if topic not in st.session_state.history["topics_completed"]:
                st.session_state.history["topics_completed"].append(topic)

    if st.session_state.quiz_submitted:
        if st.button("Finish Session", type="primary"):
            st.session_state.page = "summary"
            st.rerun()

def show_summary():
    inject_custom_css()
    st.markdown('<h1 class="gradient-text">📊 Performance Summary</h1>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card" style="display: flex; justify-content: space-around; align-items: center;">
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; color: #38bdf8; font-weight: 800;">{len(st.session_state.history['topics_completed'])}</div>
            <div style="color: #94a3b8;">Topics Completed</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; color: #818cf8; font-weight: 800;">{st.session_state.score}</div>
            <div style="color: #94a3b8;">Total Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("AI Feedback")
    if st.session_state.history["topics_completed"]:
        with st.spinner("Generating feedback..."):
            summary = get_ai_response(f"Provide encouraging feedback for a student with this history: {st.session_state.history}")
            st.markdown(f'<div class="glass-card">{summary}</div>', unsafe_allow_html=True)
    else:
        st.info("Complete some topics to get feedback.")

# --- 5. APP ROUTER ---
if st.session_state.page == "home": show_home()
elif st.session_state.page == "topic": show_topic()
elif st.session_state.page == "summary": show_summary()



