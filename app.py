from flask import Flask, render_template, request, redirect, send_file
from database.mongodb import (
    save_candidate,
    delete_candidate,
    get_candidate,
    candidates
)

from utils.parser import (
    extract_pdf_text,
    extract_docx_text
)

from utils.matcher import calculate_score

from io import BytesIO
import os


app = Flask(__name__)

# Upload Folder Configuration
UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("resume")

    if not file:
        return "No file uploaded"

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf_text(filepath)

    elif filename.endswith(".docx"):
        text = extract_docx_text(filepath)

    else:
        return "Unsupported file format"

    job_description = request.form.get(
        "job_description",
        ""
    )

    score, matched_skills = calculate_score(
        text,
        job_description
    )

    status = (
        "Shortlisted"
        if score >= 60
        else "Rejected"
    )

    candidate_data = {
        "resume_text": text,
        "ats_score": score,
        "matched_skills": matched_skills,
        "status": status
    }

    print("Sending data to MongoDB")

    save_candidate(candidate_data)

    print("MongoDB save completed")

    return render_template(
        "dashboard.html",
        score=score,
        skills=matched_skills,
        text=text,
        status=status
    )



@app.route("/history")
def history():

    search = request.args.get(
        "search",
        ""
    )

    status_filter = request.args.get(
        "status",
        ""
    )

    data = list(
        candidates.find()
    )

    if search:

        data = [
            c for c in data
            if search.lower()
            in " ".join(
                c["matched_skills"]
            ).lower()
        ]

    if status_filter:

        data = [
            c for c in data
            if c["status"] == status_filter
        ]

    total_candidates = len(data)

    shortlisted = sum(
        1
        for c in data
        if c["status"] == "Shortlisted"
    )

    rejected = sum(
        1
        for c in data
        if c["status"] == "Rejected"
    )

    if total_candidates > 0:

        average_score = sum(
            c["ats_score"]
            for c in data
        ) / total_candidates

    else:

        average_score = 0

    return render_template(
        "history.html",
        candidates=data,
        total_candidates=total_candidates,
        shortlisted=shortlisted,
        rejected=rejected,
        average_score=round(
            average_score,
            2
        ),
        search=search
    )

@app.route("/delete/<id>")
def delete(id):

    delete_candidate(id)

    return redirect("/history")


@app.route("/candidate/<id>")
def candidate(id):

    data = get_candidate(id)

    return render_template(
        "candidate.html",
        candidate=data
    )



@app.route("/download/<id>")
def download(id):

    data = get_candidate(id)

    if not data:
        return "Candidate not found"

    buffer = BytesIO()

    buffer.write(
        data["resume_text"].encode("utf-8")
    )

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume.txt",
        mimetype="text/plain"
    )



if __name__ == "__main__":
    app.run(
        debug=True
    )