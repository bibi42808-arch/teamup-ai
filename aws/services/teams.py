from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.models import Student, Team, TeamJoinRequest, TeamMembership


def create_team(db: Session, leader_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not db.query(Student).filter_by(id=leader_id).first():
        return {"success": False, "message": "Leader profile not found."}
    if int(payload.get("max_team_size", 0)) <= 0:
        return {"success": False, "message": "Maximum team size must be greater than zero."}
    team = Team(
        team_name=payload.get("team_name", "").strip(),
        project_title=payload.get("project_title", "").strip(),
        project_description=payload.get("project_description", "").strip(),
        target_hackathon=payload.get("target_hackathon", "").strip(),
        required_skills=payload.get("required_skills", "").strip(),
        open_positions=payload.get("open_positions", "").strip(),
        max_team_size=int(payload.get("max_team_size", 5)),
        application_deadline=date.fromisoformat(payload.get("application_deadline")),
        short_description=payload.get("short_description", "").strip(),
        leader_student_id=leader_id,
        is_recruiting=1,
    )
    db.add(team)
    db.flush()
    db.add(TeamMembership(team_id=team.id, student_id=leader_id, role="Team Lead"))
    db.commit()
    return {"success": True, "message": "Team created successfully.", "team_id": team.id}


def list_teams(db: Session, project_category: str | None = None) -> List[Dict[str, Any]]:
    teams = db.query(Team).all()
    result = []
    for team in teams:
        if project_category and project_category.lower() not in team.target_hackathon.lower() and project_category.lower() not in team.project_title.lower():
            continue
        members = db.query(TeamMembership).filter_by(team_id=team.id).all()
        result.append({
            "id": team.id,
            "team_name": team.team_name,
            "project_title": team.project_title,
            "target_hackathon": team.target_hackathon,
            "required_skills": team.required_skills,
            "open_positions": team.open_positions,
            "max_team_size": team.max_team_size,
            "application_deadline": team.application_deadline.isoformat() if team.application_deadline else None,
            "short_description": team.short_description,
            "is_recruiting": bool(team.is_recruiting),
            "leader_name": db.query(Student).filter_by(id=team.leader_student_id).first().full_name,
            "member_count": len(members),
            "open_spots": max(team.max_team_size - len(members), 0),
        })
    return result


def submit_team_join_request(db: Session, team_id: int, student_id: int) -> Dict[str, Any]:
    team = db.query(Team).filter_by(id=team_id).first()
    if not team:
        return {"success": False, "message": "Team not found."}
    if team.leader_student_id == student_id:
        return {"success": False, "message": "You are already the team leader."}
    current_members = db.query(TeamMembership).filter_by(team_id=team_id).count()
    pending_requests = db.query(TeamJoinRequest).filter_by(team_id=team_id, status="pending").count()
    if current_members + pending_requests >= team.max_team_size:
        return {"success": False, "message": "The team is at or above its configured size limit for pending requests."}
    existing = db.query(TeamJoinRequest).filter_by(team_id=team_id, student_id=student_id).first()
    if existing:
        return {"success": False, "message": "You already submitted a join request for this team."}
    request = TeamJoinRequest(team_id=team_id, student_id=student_id, status="pending")
    db.add(request)
    db.commit()
    return {"success": True, "message": "Join request submitted.", "request_id": request.id}


def review_team_join_request(db: Session, team_id: int, request_id: int, leader_id: int, decision: str) -> Dict[str, Any]:
    team = db.query(Team).filter_by(id=team_id).first()
    if not team or team.leader_student_id != leader_id:
        return {"success": False, "message": "Only the team leader can review requests."}
    request = db.query(TeamJoinRequest).filter_by(id=request_id, team_id=team_id).first()
    if not request:
        return {"success": False, "message": "Request not found."}
    if decision.lower() not in {"accept", "reject"}:
        return {"success": False, "message": "Decision must be accept or reject."}
    if decision.lower() == "accept":
        current_members = db.query(TeamMembership).filter_by(team_id=team_id).count()
        if current_members >= team.max_team_size:
            return {"success": False, "message": "Team size limit reached. Cannot accept more members."}
        db.add(TeamMembership(team_id=team_id, student_id=request.student_id, role="Member"))
        request.status = "accepted"
        db.commit()
        return {"success": True, "message": "Join request accepted."}
    request.status = "rejected"
    db.commit()
    return {"success": True, "message": "Join request rejected."}


def list_join_requests_for_team(db: Session, team_id: int) -> List[Dict[str, Any]]:
    rows = db.query(TeamJoinRequest).filter_by(team_id=team_id).all()
    res = []
    for row in rows:
        student = db.query(Student).filter_by(id=row.student_id).first()
        res.append({
            "id": row.id,
            "student_id": row.student_id,
            "student_name": student.full_name if student else "Unknown",
            "status": row.status,
        })
    return res


def missing_skills_for_team(db: Session, team_id: int) -> List[str]:
    team = db.query(Team).filter_by(id=team_id).first()
    if not team:
        return []
    required = [item.strip() for item in team.required_skills.split(',') if item.strip()]
    members = db.query(TeamMembership).filter_by(team_id=team_id).all()
    owned = []
    for member in members:
        student = db.query(Student).filter_by(id=member.student_id).first()
        if student:
            owned.extend([skill.skill_name for skill in student.skills])
    present = {item.strip() for item in owned if item.strip()}
    return [skill for skill in required if skill not in present]
