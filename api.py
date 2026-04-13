from flask import Flask, request, jsonify
from utils import *

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    resume = request.files.get("resume")
    job_desc = request.form.get("job_desc")

    resume_text = extract_text_from_pdf(resume) if resume else ""

    score = match_resume_job(resume_text, job_desc)
    r_skills = extract_skills(resume_text)
    j_skills = extract_skills(job_desc)
    missing = missing_skills(r_skills, j_skills)

    return jsonify({
        "score": score,
        "skills": r_skills,
        "missing": missing,
        "suggestions": suggest_improvements(missing)
    })

if __name__ == "__main__":
    app.run(debug=True)
