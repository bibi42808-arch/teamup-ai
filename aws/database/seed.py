from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from .db import init_db
from .models import (
    ConnectionRequest,
    HackathonOpportunity,
    Interest,
    Skill,
    Student,
    StudentInterest,
    StudentSkill,
    Team,
    TeamJoinRequest,
    TeamMembership,
)


def seed_static_reference_data(db: Session) -> None:
    for skill_name in [
        "Python",
        "Java",
        "JavaScript",
        "React",
        "HTML/CSS",
        "Machine Learning",
        "Artificial Intelligence",
        "Data Science",
        "UI/UX Design",
        "Backend Development",
        "Cloud Computing",
        "AWS",
        "Database Management",
        "Cybersecurity",
        "IoT",
        "Research",
        "Presentation and Communication",
    ]:
        if not db.query(Skill).filter_by(name=skill_name).first():
            db.add(Skill(name=skill_name))

    for interest_name in [
        "Artificial Intelligence",
        "Machine Learning",
        "Healthcare",
        "Education",
        "Agriculture",
        "Sustainability",
        "FinTech",
        "Cybersecurity",
        "Social Impact",
        "Web Development",
    ]:
        if not db.query(Interest).filter_by(name=interest_name).first():
            db.add(Interest(name=interest_name))

    db.commit()


def seed_demo_data(db: Session) -> None:
    if db.query(Student).count() > 0:
        return

    students = [
        Student(
            full_name="Aisha Rahman",
            college="Northeastern University",
            department="Computer Science",
            academic_year="3rd Year",
            experience_level="Advanced",
            preferred_roles="AI Engineer, Python Developer",
            hackathon_interests="AI and ML, Healthcare",
            availability="Weekends and evenings",
            introduction="I love building AI products and mentoring student teams.",
            github_url="https://github.com/aisharahman",
            portfolio_url="https://aisharahman.dev",
        ),
        Student(
            full_name="Daniel Kim",
            college="Georgia Tech",
            department="Human-Centered Computing",
            academic_year="2nd Year",
            experience_level="Intermediate",
            preferred_roles="Frontend Developer, UI/UX Designer",
            hackathon_interests="Web apps, Social impact",
            availability="Evenings and flexible weekends",
            introduction="I enjoy creating intuitive interfaces and connecting design with user needs.",
            github_url="https://github.com/danielkim",
            portfolio_url=None,
        ),
        Student(
            full_name="Priya Nair",
            college="University of Michigan",
            department="Data Science",
            academic_year="4th Year",
            experience_level="Advanced",
            preferred_roles="Data Scientist, Backend Developer",
            hackathon_interests="Data science, FinTech",
            availability="Weekdays after 6pm",
            introduction="I work on data workflows and scalable backend services.",
            github_url="https://github.com/priyanair",
            portfolio_url="https://priyanair.io",
        ),
        Student(
            full_name="Marcus Lee",
            college="University of Texas",
            department="Software Engineering",
            academic_year="1st Year",
            experience_level="Beginner",
            preferred_roles="Full Stack Developer, Cloud Engineer",
            hackathon_interests="Cloud, Web Development",
            availability="Weekends",
            introduction="I am learning cloud and web development and want to contribute creatively.",
            github_url=None,
            portfolio_url=None,
        ),
    ]

    db.add_all(students)
    db.flush()

    skill_map = {
        1: ["Python", "Machine Learning", "Artificial Intelligence", "Data Science"],
        2: ["React", "JavaScript", "HTML/CSS", "UI/UX Design"],
        3: ["Python", "Data Science", "Database Management", "Backend Development"],
        4: ["AWS", "Cloud Computing", "JavaScript", "Backend Development"],
    }
    interest_map = {
        1: ["Artificial Intelligence", "Healthcare", "Machine Learning"],
        2: ["Social Impact", "Web Development", "Education"],
        3: ["FinTech", "Data Science", "Machine Learning"],
        4: ["Web Development", "Sustainability", "Cloud Computing"],
    }

    for student in students:
        for skill_name in skill_map.get(student.id, []):
            db.add(StudentSkill(student_id=student.id, skill_name=skill_name))
        for interest_name in interest_map.get(student.id, []):
            db.add(StudentInterest(student_id=student.id, interest_name=interest_name))

    db.add_all(
        [
            Team(
                team_name="VisionForge",
                project_title="AI Health Mentor",
                project_description="A predictive health assistant for student well-being and risk screening.",
                target_hackathon="AI for Good Hackathon",
                required_skills="Python, Machine Learning, Frontend",
                open_positions="Frontend Developer, Data Analyst",
                max_team_size=5,
                application_deadline=date(2027, 2, 15),
                short_description="Building a health-tech AI assistant for early wellness insights.",
                leader_student_id=1,
                is_recruiting=1,
            ),
            Team(
                team_name="CloudBloom",
                project_title="Smart Campus Dashboard",
                project_description="A cloud-native dashboard for campus sustainability and resource tracking.",
                target_hackathon="AWS HackOn",
                required_skills="AWS, React, Data Visualization",
                open_positions="Cloud Engineer, Frontend Developer",
                max_team_size=4,
                application_deadline=date(2027, 3, 1),
                short_description="An infrastructure and data dashboard for campus sustainability.",
                leader_student_id=4,
                is_recruiting=1,
            ),
        ]
    )
    db.flush()

    db.add_all(
        [
            TeamMembership(team_id=1, student_id=1, role="AI Engineer"),
            TeamMembership(team_id=2, student_id=4, role="Cloud Engineer"),
            TeamMembership(team_id=1, student_id=2, role="Frontend Developer"),
        ]
    )

    db.add_all(
        [
            HackathonOpportunity(
                name="AI for Good Hackathon",
                organizer="Student Innovation Lab",
                description="A social impact challenge centered on health, education, and environmental AI.",
                categories="Artificial Intelligence, Healthcare",
                eligibility="Open to students in any STEM discipline",
                registration_deadline=date(2027, 1, 25),
                event_dates="May 12-14, 2027",
                location_type="Online",
                registration_url="https://example.com/ai-good",
                is_sample_data=1,
            ),
            HackathonOpportunity(
                name="AWS HackOn",
                organizer="Amazon Student Builders",
                description="A cloud computing challenge focusing on modern cloud architecture and productivity tools.",
                categories="Cloud Computing, Web Development",
                eligibility="Students with cloud or application development interests",
                registration_deadline=date(2027, 2, 8),
                event_dates="April 21-23, 2027",
                location_type="Hybrid",
                registration_url="https://example.com/aws-hackon",
                is_sample_data=1,
            ),
        ]
    )
    db.commit()


def initialize_database(db: Session) -> None:
    init_db()
    db.query(ConnectionRequest).delete()
    db.query(TeamJoinRequest).delete()
    db.query(TeamMembership).delete()
    db.query(Team).delete()
    db.query(StudentSkill).delete()
    db.query(StudentInterest).delete()
    db.query(Student).delete()
    db.query(HackathonOpportunity).delete()
    db.query(Skill).delete()
    db.query(Interest).delete()
    db.commit()
    seed_static_reference_data(db)
    seed_demo_data(db)
    db.commit()
