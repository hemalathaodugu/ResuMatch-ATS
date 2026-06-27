def calculate_score(resume_text, job_description):

    skills = [
        "python",
        "java",
        "javascript",
        "react",
        "flask",
        "mongodb",
        "html",
        "css"
    ]


    matched = []


    for skill in skills:

        if skill in resume_text.lower() and skill in job_description.lower():

            matched.append(skill)


    score = (len(matched) / len(skills)) * 100


    return round(score,2), matched