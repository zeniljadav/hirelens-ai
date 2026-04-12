import streamlit as st

st.set_page_config(page_title="HireLens AI", layout="wide")

# Header
st.markdown("""
    <h1 style='text-align: center;'>🚀 HireLens AI</h1>
    <p style='text-align: center;'>Smart Resume Analyzer</p>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📌 Options")
option = st.sidebar.selectbox("Choose Feature", ["Upload Resume", "Match with Job"])

# Main UI
if option == "Upload Resume":
    st.subheader("📄 Upload Your Resume")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        st.success("✅ Resume Uploaded Successfully!")

        st.markdown("### 🔍 Analysis Result")
        st.write("Skills: Python, Machine Learning, Data Analysis")
        st.write("Experience: Fresher")
        st.write("Score: 75%")

elif option == "Match with Job":
    st.subheader("💼 Job Matching")

    job_desc = st.text_area("Paste Job Description")

    if st.button("Analyze Match"):
        st.success("Match Score: 80%")