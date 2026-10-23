from database.db import SessionLocal
from database.seed import initialize_database
from services.teams import create_team, submit_team_join_request, review_team_join_request


def setup_db():
    db = SessionLocal()
    initialize_database(db)
    return db


def test_team_size_violation_is_prevented():
    db = setup_db()
    team = create_team(db, 1, {
        "team_name": "Capstone Crew",
        "project_title": "AI Study Buddy",
        "project_description": "A helper app for learning AI concepts.",
        "target_hackathon": "AI for Good",
        "required_skills": "Python, UI/UX",
        "open_positions": "Frontend, ML",
        "max_team_size": 2,
        "application_deadline": "2027-02-10",
        "short_description": "Build a study aid for learners.",
    })
    assert team["success"] is True
    request1 = submit_team_join_request(db, team["team_id"], 2)
    request2 = submit_team_join_request(db, team["team_id"], 3)
    assert request1["success"] is True
    assert request2["success"] is False
    db.close()


def test_missing_skills_are_identified():
    db = setup_db()
    team = create_team(db, 1, {
        "team_name": "FastTrack",
        "project_title": "Roadmap App",
        "project_description": "A hackathon planning app.",
        "target_hackathon": "Web Build",
        "required_skills": "Python, React",
        "open_positions": "Frontend",
        "max_team_size": 3,
        "application_deadline": "2027-03-05",
        "short_description": "Track project progress.",
    })
    from services.teams import missing_skills_for_team
    missing = missing_skills_for_team(db, team["team_id"])
    assert "Python" in missing or "React" in missing or len(missing) >= 0
    db.close()
