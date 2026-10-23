from services.matching import estimate_compatibility, rank_students


def test_matching_students_with_complementary_skills():
    current = {
        "id": 1,
        "name": "Student A",
        "skills": ["Python", "Machine Learning", "Artificial Intelligence"],
        "interests": ["Artificial Intelligence", "Healthcare"],
        "experience_level": "Advanced",
        "availability": "Weekends",
        "desired_skills": ["Frontend", "React", "UI/UX Design"],
        "desired_roles": ["Frontend Developer", "UI/UX Designer"],
    }
    candidate = {
        "id": 2,
        "name": "Student B",
        "skills": ["React", "JavaScript", "HTML/CSS", "UI/UX Design"],
        "interests": ["Artificial Intelligence", "Social Impact"],
        "experience_level": "Intermediate",
        "availability": "Weekends",
        "hackathon_interests": "AI and ML, Healthcare",
        "preferred_roles": "Frontend Developer, UI/UX Designer",
    }

    match = estimate_compatibility(current, candidate, current["desired_skills"], "AI")
    assert match["score"] >= 70
    assert "complementary" in match["explanation"].lower()


def test_filtering_by_project_category():
    current = {
        "id": 1,
        "skills": ["Python"],
        "interests": ["Artificial Intelligence"],
        "experience_level": "Beginner",
        "availability": "Weekends",
        "desired_skills": ["Python"],
        "desired_roles": ["Backend Developer"],
    }
    candidates = [
        {"id": 2, "name": "A", "skills": ["React"], "interests": ["Web Development"], "experience_level": "Intermediate", "availability": "Weekends", "hackathon_interests": "Web Development", "preferred_roles": "Frontend Developer"},
        {"id": 3, "name": "B", "skills": ["Python", "Machine Learning"], "interests": ["Artificial Intelligence"], "experience_level": "Advanced", "availability": "Weekends", "hackathon_interests": "AI and ML", "preferred_roles": "AI Engineer"},
    ]
    ranked = rank_students(current, candidates, project_category="AI")
    assert ranked[0]["id"] == 3


def test_calculating_compatibility_scores():
    current = {
        "id": 1, "name": "Student A", "skills": ["Python"], "interests": ["Healthcare"], "experience_level": "Intermediate", "availability": "Evenings", "desired_skills": ["Python"], "desired_roles": ["Data Scientist"],
    }
    candidate = {
        "id": 2, "name": "Student B", "skills": ["Python", "Machine Learning"], "interests": ["Healthcare"], "experience_level": "Advanced", "availability": "Evenings", "hackathon_interests": "AI and ML", "preferred_roles": "AI Engineer",
    }
    match = estimate_compatibility(current, candidate, current["desired_skills"], "AI")
    assert 0 <= match["score"] <= 100


def test_incomplete_profile_handling():
    current = {"id": 1, "name": "Incomplete", "skills": [], "interests": [], "experience_level": "Beginner", "availability": "Weekends", "desired_skills": []}
    candidate = {"id": 2, "name": "Candidate", "skills": ["Python"], "interests": ["AI"], "experience_level": "Beginner", "availability": "Weekend", "hackathon_interests": "AI"}
    match = estimate_compatibility(current, candidate)
    assert match["score"] >= 0
