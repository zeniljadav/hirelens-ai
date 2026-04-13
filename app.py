import streamlit as st
import sqlite3
import hashlib
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------
st.set_page_config(page_title="HireLens AI", layout="wide")

# ------------------ DATABASE ------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
''')
conn.commit()

# ------------------ AUTH FUNCTIONS ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    hashed = hash_password(password)
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result:
        return hash_password(password) == result[0]
    return False

# ------------------ LOGIN UI ------------------
menu_auth = st.sidebar.selectbox("Account", ["Login", "Signup"])

if not st.session_state.logged_in:

    if menu_auth == "Login":
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.title("📝 Signup")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Signup"):
            if create_user(new_user, new_pass):
                st.success("Account created! Login now.")
            else:
                st.error("User already exists")

    st.stop()

# ------------------ SIDEBAR ------------------
st.sidebar.title("🚀 HireLens AI")
menu = st.sidebar.radio("Navigation", ["Home", "Dashboard", "Analyzer", "History", "Profile"])

st.sidebar.markdown(f"👤 {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ------------------ FUNCTIONS ------------------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_skills(text):
    skills = ["python", "machine learning", "data analysis", "sql", "java", "excel"]
    return [s for s in skills if s in text.lower()]

def missing_skills(resume, job):
    return list(set(job.lower().split()) - set(resume.lower().split()))[:10]

def generate_pdf(score, skills, missing):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "HireLens AI Report", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Match Score: {score}%", ln=True)

    pdf.cell(200, 10, " ", ln=True)
    pdf.cell(200, 10, "Skills Found:", ln=True)
    for s in skills:
        pdf.cell(200, 10, f"- {s}", ln=True)

    pdf.cell(200, 10, " ", ln=True)
    pdf.cell(200, 10, "Missing Skills:", ln=True)
    for m in missing:
        pdf.cell(200, 10, f"- {m}", ln=True)

    pdf.output("report.pdf")

# ------------------ HOME ------------------
if menu == "Home":
    st.title("🚀 HireLens AI")
    st.write("AI-powered Resume Intelligence Platform")

    col1, col2, col3 = st.columns(3)
    col1.info("📄 Upload Resume")
    col2.info("🧠 AI Matching")
    col3.info("📊 Get Insights")

# ------------------ DASHBOARD ------------------
elif menu == "Dashboard":
    st.title("📊 Dashboard")

    user = st.session_state.username
    user_history = st.session_state.history.get(user, [])

    total = len(user_history)
    scores = [h["score"] for h in user_history]
    avg = int(sum(scores)/total) if total else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Analyses", total)
    col2.metric("Average Score", f"{avg}%")

    if scores:
        fig, ax = plt.subplots()
        ax.plot(scores)
        ax.set_title("Score Trend")
        ax.set_xlabel("Attempts")
        ax.set_ylabel("Score")
        st.pyplot(fig)
    else:
        st.info("No data yet")

# ------------------ ANALYZER ------------------
elif menu == "Analyzer":
    st.title("📄 Resume Analyzer")

    col1, col2 = st.columns(2)
    uploaded_file = col1.file_uploader("Upload Resume", type=["pdf"])
    job_desc = col2.text_area("Job Description")

    if st.button("🚀 Analyze"):
        if uploaded_file and job_desc:

            with st.spinner("Analyzing..."):
                resume_text = extract_text(uploaded_file)

                # TF-IDF (FAANG LEVEL)
                cv = TfidfVectorizer(stop_words='english')
                matrix = cv.fit_transform([resume_text, job_desc])
                score = cosine_similarity(matrix)[0][1]
                score_percent = round(score * 100, 2)

                skills = extract_skills(resume_text)
                missing = missing_skills(resume_text, job_desc)

                user = st.session_state.username
                if user not in st.session_state.history:
                    st.session_state.history[user] = []

                st.session_state.history[user].append({"score": score_percent})

            st.subheader("Results")

            col1, col2, col3 = st.columns(3)
            col1.metric("Score", f"{score_percent}%")
            col2.metric("Skills", len(skills))
            col3.metric("Missing", len(missing))

            st.progress(int(score_percent))

            if score_percent > 80:
                st.success("🔥 High Match")
            elif score_percent > 60:
                st.warning("⚡ Medium Match")
            else:
                st.error("❌ Low Match")

            st.write("### Skills Found")
            st.write(skills)

            st.write("### Missing Skills")
            st.write(missing)

            if st.button("📄 Download Report"):
                generate_pdf(score_percent, skills, missing)
                with open("report.pdf", "rb") as f:
                    st.download_button("Download", f, file_name="report.pdf")

        else:
            st.warning("Upload resume + job description")

# ------------------ HISTORY ------------------
elif menu == "History":
    st.title("📜 History")

    user = st.session_state.username
    user_history = st.session_state.history.get(user, [])

    if user_history:
        for i, h in enumerate(user_history):
            st.write(f"{i+1}. Score: {h['score']}%")
    else:
        st.info("No history")

# ------------------ PROFILE ------------------
elif menu == "Profile":
    st.title("👤 Profile")

    user = st.session_state.username
    user_history = st.session_state.history.get(user, [])

    total = len(user_history)
    avg = int(sum([h["score"] for h in user_history])/total) if total else 0

    st.write(f"Username: {user}")
    st.metric("Total Analyses", total)
    st.metric("Average Score", f"{avg}%")
