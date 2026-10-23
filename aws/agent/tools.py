from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import HackathonOpportunity, Student, StudentInterest, StudentSkill, Team, TeamMembership
from services.matching import rank_students
from strands import tool


@tool(description="Search for students that fit a hackathon team need.", inputSchema={
    "type": "object",
    "properties": {
        "student_id": {"type": "integer"},
        "skill_need": {"type": "string"},
        "preferred_category": {"type": "string"},
        "max_results": {"type": "integer", "default": 3}
    },
    "required": ["student_id", "skill_need"]
})
def find_teammates(student_id: int, skill_need: str, preferred_category: str = "", max_results: int = 3) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        current = db.query(Student).filter_by(id=student_id).first()
        if not current:
            return {"error": "Student not found."}
        current_profile = {
            "id": current.id,
            "name": current.full_name,
            "skills": [row.skill_name for row in current.skills],
            "interests": [row.interest_name for row in current.interests],
            "experience_level": current.experience_level,
            "availability": current.availability,
            "desired_skills": [skill_need],
            "desired_roles": [skill_need],
        }
        candidates = []
        for student in db.query(Student).filter(Student.id != student_id).all():
            candidates.append({
                "id": student.id,
                "name": student.full_name,
                "skills": [row.skill_name for row in student.skills],
                "interests": [row.interest_name for row in student.interests],
                "experience_level": student.experience_level,
                "availability": student.availability,
                "hackathon_interests": student.hackathon_interests,
                "preferred_roles": student.preferred_roles,
            })
        ranked = rank_students(current_profile, candidates, preferred_skills=[skill_need], project_category=preferred_category or None, min_score=30)[:max_results]
        return {"tool": "find_teammates", "results": ranked}
    finally:
        db.close()


@tool(description="Find team openings that match a student's interests or skills.", inputSchema={
    "type": "object",
    "properties": {
        "skill": {"type": "string"},
        "category": {"type": "string"},
        "max_results": {"type": "integer", "default": 3}
    },
    "required": ["skill"]
})
def find_existing_teams(skill: str, category: str = "", max_results: int = 3) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        teams = db.query(Team).all()
        matches = []
        for team in teams:
            if category and category.lower() not in team.target_hackathon.lower() and category.lower() not in team.project_title.lower():
                continue
            if skill.lower() in team.required_skills.lower() or skill.lower() in team.open_positions.lower():
                matches.append({
                    "id": team.id,
                    "team_name": team.team_name,
                    "project_title": team.project_title,
                    "target_hackathon": team.target_hackathon,
                    "required_skills": team.required_skills,
                    "open_positions": team.open_positions,
                    "leader_student_id": team.leader_student_id,
                })
        return {"tool": "find_existing_teams", "results": matches[:max_results]}
    finally:
        db.close()


@tool(description="List relevant hackathon opportunities from the app's available sample data.", inputSchema={
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "location_type": {"type": "string"},
        "max_results": {"type": "integer", "default": 3}
    }
})
def find_hackathons(topic: str = "", location_type: str = "", max_results: int = 3) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        rows = db.query(HackathonOpportunity).all()
        matches = []
        for row in rows:
            if topic and topic.lower() not in row.categories.lower() and topic.lower() not in row.description.lower():
                continue
            if location_type and location_type.lower() not in row.location_type.lower():
                continue
            matches.append({
                "id": row.id,
                "name": row.name,
                "organizer": row.organizer,
                "categories": row.categories,
                "eligibility": row.eligibility,
                "location_type": row.location_type,
            })
        return {"tool": "find_hackathons", "results": matches[:max_results]}
    finally:
        db.close()


@tool(description="Identify missing skills for a proposed team.", inputSchema={
    "type": "object",
    "properties": {
        "team_id": {"type": "integer"},
    },
    "required": ["team_id"]
})
def analyse_skill_gaps(team_id: int) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        team = db.query(Team).filter_by(id=team_id).first()
        if not team:
            return {"error": "Team not found."}
        required = [item.strip() for item in team.required_skills.split(',') if item.strip()]
        present = set()
        for member in db.query(TeamMembership).filter_by(team_id=team_id).all():
            student = db.query(Student).filter_by(id=member.student_id).first()
            if student:
                present.update(skill.skill_name for skill in student.skills)
        missing = [skill for skill in required if skill not in present]
        return {"tool": "analyse_skill_gaps", "team_id": team_id, "missing_skills": missing}
    finally:
        db.close()


@tool(description="Recommend the next practical steps for the student situation.", inputSchema={
    "type": "object",
    "properties": {
        "student_id": {"type": "integer"},
        "goal": {"type": "string"}
    },
    "required": ["student_id"]
})
def recommend_next_steps(student_id: int, goal: str = "") -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return {"error": "Student not found."}
        suggestions = [
            "Update your profile with your strongest skill tags.",
            "Send a connection request to a complementary teammate.",
            "Apply to a team that matches your hackathon category.",
        ]
        if goal:
            suggestions.append(f"Focus on {goal} as your next project decision.")
        return {"tool": "recommend_next_steps", "student_id": student_id, "suggestions": suggestions}
    finally:
        db.close()
