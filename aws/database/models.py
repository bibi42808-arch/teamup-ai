from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    college = Column(String(200), nullable=False)
    department = Column(String(200), nullable=False)
    academic_year = Column(String(50), nullable=False)
    experience_level = Column(String(50), nullable=False)
    preferred_roles = Column(String(300), nullable=False)
    hackathon_interests = Column(String(300), nullable=False)
    availability = Column(String(100), nullable=False)
    introduction = Column(Text, nullable=False)
    github_url = Column(String(300), nullable=True)
    portfolio_url = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    interests = relationship("StudentInterest", back_populates="student", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMembership", back_populates="student", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)


class StudentSkill(Base):
    __tablename__ = "student_skills"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_name = Column(String(120), nullable=False)
    student = relationship("Student", back_populates="skills")

    __table_args__ = (UniqueConstraint("student_id", "skill_name", name="uq_student_skill"),)


class Interest(Base):
    __tablename__ = "interests"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)


class StudentInterest(Base):
    __tablename__ = "student_interests"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    interest_name = Column(String(120), nullable=False)
    student = relationship("Student", back_populates="interests")

    __table_args__ = (UniqueConstraint("student_id", "interest_name", name="uq_student_interest"),)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    team_name = Column(String(200), nullable=False)
    project_title = Column(String(200), nullable=False)
    project_description = Column(Text, nullable=False)
    target_hackathon = Column(String(200), nullable=False)
    required_skills = Column(String(300), nullable=False)
    open_positions = Column(String(300), nullable=False)
    max_team_size = Column(Integer, nullable=False, default=5)
    application_deadline = Column(Date, nullable=False)
    short_description = Column(Text, nullable=False)
    leader_student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    is_recruiting = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    leader = relationship("Student", foreign_keys=[leader_student_id])
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")
    join_requests = relationship("TeamJoinRequest", back_populates="team", cascade="all, delete-orphan")


class TeamMembership(Base):
    __tablename__ = "team_memberships"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    role = Column(String(200), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="memberships")
    student = relationship("Student", back_populates="team_memberships")

    __table_args__ = (UniqueConstraint("team_id", "student_id", name="uq_team_member"),)


class ConnectionRequest(Base):
    __tablename__ = "connection_requests"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("sender_id", "receiver_id", name="uq_connection_request"),)


class TeamJoinRequest(Base):
    __tablename__ = "team_join_requests"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="join_requests")

    __table_args__ = (UniqueConstraint("team_id", "student_id", name="uq_team_join_request"),)


class HackathonOpportunity(Base):
    __tablename__ = "hackathon_opportunities"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    organizer = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    categories = Column(String(200), nullable=False)
    eligibility = Column(String(200), nullable=False)
    registration_deadline = Column(Date, nullable=False)
    event_dates = Column(String(200), nullable=False)
    location_type = Column(String(50), nullable=False)
    registration_url = Column(String(300), nullable=False)
    is_sample_data = Column(Integer, default=1)
