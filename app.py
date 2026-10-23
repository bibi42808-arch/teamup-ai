import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database.db import SessionLocal, init_db
from database.models import Student, StudentInterest, StudentSkill, Team, TeamJoinRequest, TeamMembership, ConnectionRequest, HackathonOpportunity
from database.seed import initialize_database
from services.connections import list_requests_for_student, send_connection_request, update_connection_request
from services.matching import rank_students
from services.opportunities import list_hackathons
from services.teams import create_team, list_teams, missing_skills_for_team, review_team_join_request, submit_team_join_request, list_join_requests_for_team
from ui.styles import apply_global_styles
from agent.decider import get_decider_status
from agent.tools import find_teammates, find_existing_teams, find_hackathons, analyse_skill_gaps, recommend_next_steps

st.set_page_config(page_title="TeamUp AI", page_icon="🤝", layout="wide", initial_sidebar_state="expanded")
apply_global_styles()

if "db_initialized" not in st.session_state:
    init_db()
    db = SessionLocal()
    try:
        initialize_database(db)
    finally:
        db.close()
    st.session_state["db_initialized"] = True


def get_db():
    return SessionLocal()


def get_students():
    db = get_db()
    try:
        rows = db.query(Student).order_by(Student.id).all()
        students = []
        for row in rows:
            students.append({
                "id": row.id,
                "name": row.full_name,
                "college": row.college,
                "department": row.department,
                "year": row.academic_year,
                "experience_level": row.experience_level,
                "skills": [s.skill_name for s in row.skills],
                "interests": [i.interest_name for i in row.interests],
                "preferred_roles": row.preferred_roles,
                "hackathon_interests": row.hackathon_interests,
                "availability": row.availability,
                "introduction": row.introduction,
                "github_url": row.github_url,
                "portfolio_url": row.portfolio_url,
            })
        return students
    finally:
        db.close()


def get_student_by_id(student_id):
    db = get_db()
    try:
        row = db.query(Student).filter_by(id=student_id).first()
        if not row:
            return None
        return {
            "id": row.id,
            "name": row.full_name,
            "college": row.college,
            "department": row.department,
            "year": row.academic_year,
            "experience_level": row.experience_level,
            "skills": [s.skill_name for s in row.skills],
            "interests": [i.interest_name for i in row.interests],
            "preferred_roles": row.preferred_roles,
            "hackathon_interests": row.hackathon_interests,
            "availability": row.availability,
            "introduction": row.introduction,
            "github_url": row.github_url,
            "portfolio_url": row.portfolio_url,
        }
    finally:
        db.close()


def create_or_update_student(payload: dict, student_id: int | None = None):
    db = get_db()
    try:
        if student_id:
            row = db.query(Student).filter_by(id=student_id).first()
            if not row:
                return {"success": False, "message": "Student not found."}
        else:
            row = Student()
            db.add(row)
        row.full_name = payload.get("full_name", "").strip()
        row.college = payload.get("college", "").strip()
        row.department = payload.get("department", "").strip()
        row.academic_year = payload.get("academic_year", "").strip()
        row.experience_level = payload.get("experience_level", "").strip()
        row.preferred_roles = payload.get("preferred_roles", "").strip()
        row.hackathon_interests = payload.get("hackathon_interests", "").strip()
        row.availability = payload.get("availability", "").strip()
        row.introduction = payload.get("introduction", "").strip()
        row.github_url = payload.get("github_url") or None
        row.portfolio_url = payload.get("portfolio_url") or None
        db.flush()
        for linked in db.query(StudentSkill).filter_by(student_id=row.id).all():
            db.delete(linked)
        for skill in payload.get("skills", []):
            db.add(StudentSkill(student_id=row.id, skill_name=skill))
        for linked in db.query(StudentInterest).filter_by(student_id=row.id).all():
            db.delete(linked)
        for interest in payload.get("interests", []):
            db.add(StudentInterest(student_id=row.id, interest_name=interest))
        db.commit()
        return {"success": True, "message": "Profile saved.", "student_id": row.id}
    finally:
        db.close()


def run_demo_agent(prompt: str, student_id: int | None = None):
    decision = get_decider_status()
    if decision["mode"] == "development":
        p = prompt.lower()
        if "frontend" in p or "ui" in p:
            tool_name = "find_teammates"
        elif "team" in p and "join" in p:
            tool_name = "find_existing_teams"
        elif "missing" in p or "skill" in p:
            tool_name = "analyse_skill_gaps"
        elif "hackathon" in p:
            tool_name = "find_hackathons"
        else:
            tool_name = "recommend_next_steps"
        if tool_name == "find_teammates":
            result = find_teammates(student_id or 1, "Frontend Developer", "AI")
        elif tool_name == "find_existing_teams":
            result = find_existing_teams("Python", "AI")
        elif tool_name == "analyse_skill_gaps":
            result = analyse_skill_gaps(1)
        elif tool_name == "find_hackathons":
            result = find_hackathons(topic="AI", max_results=3)
        else:
            result = recommend_next_steps(student_id or 1, "AI hackathon")
        return {"tool_name": tool_name, "result": result, "mode": "development"}
    return {"tool_name": "bedrock_decider", "result": {"status": "AWS/Bedrock integration is configured; real model call ready."}, "mode": "bedrock"}


st.sidebar.title("TeamUp AI")
nav = st.sidebar.radio(
    "Navigation",
    [
        "Landing",
        "Dashboard",
        "Find Teammates",
        "Find a Team",
        "Hackathons",
        "My Team",
        "Connections",
        "My Profile",
        "AI Assistant",
        "Settings",
    ],
    index=0,
)

if nav == "Landing":
    st.markdown(
        """
        <div class="hero-box">
            <div class="feature-pill">TeamUp AI</div>
            <h1>Your Next Hackathon Team Starts Here.</h1>
            <p>Meet like-minded builders, discover your perfect teammates, and turn your ideas into real projects.</p>
            <div class="hero-action-row">
                <button style="background: linear-gradient(135deg, #5b5ce6 0%, #7c4dff 100%); border: none; border-radius: 12px; color: white; padding: 0.78rem 1.25rem; font-weight: 700; cursor: pointer;">Find My Team</button>
                <button style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.22); border-radius: 12px; color: white; padding: 0.78rem 1.25rem; font-weight: 700; cursor: pointer;">Explore Hackathons</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat_cols = st.columns(4)
    stat_values = [
        ("Active students", "1,200+"),
        ("Open teams", "48"),
        ("Hackathons", "26"),
        ("AI matches", "92%"),
    ]
    for idx, (label, value) in enumerate(stat_values):
        with stat_cols[idx]:
            st.markdown(f"<div class='stat-box'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)

    st.markdown("### Why students choose TeamUp AI")
    cols = st.columns(5)
    feature_cards = [
        ("AI-Powered Team Matching", "Find complementary skills and project-fit profiles instantly."),
        ("Discover Hackathons", "Browse relevant challenges and match them to your skills."),
        ("Connect with Builders", "Reach out to peers and form stronger teams quickly."),
        ("Find Missing Skills", "Identify the exact gaps your team needs to close."),
        ("Build Your Portfolio", "Showcase projects, experience, and hackathon momentum."),
    ]
    for i, (title, desc) in enumerate(feature_cards):
        with cols[i]:
            st.markdown(f"<div class='card'><strong>{title}</strong><br><br>{desc}</div>", unsafe_allow_html=True)

    st.markdown("### How it works")
    steps = [
        "Create your profile.",
        "Select your skills and interests.",
        "Discover compatible teammates.",
        "Send connection requests.",
        "Form your team and participate.",
    ]
    for idx, step in enumerate(steps, start=1):
        st.markdown(f"<div class='card'><strong>Step {idx}:</strong> {step}</div>", unsafe_allow_html=True)

elif nav == "Dashboard":
    st.title("Dashboard")
    students = get_students()
    teams = list_teams(get_db())
    hackathons = list_hackathons(get_db())
    metrics = [
        ("Students", len(students)),
        ("Teams", len(teams)),
        ("Hackathons", len(hackathons)),
        ("Open opportunities", sum(1 for t in teams if t["is_recruiting"])),
    ]
    cols = st.columns(len(metrics))
    for idx, (label, value) in enumerate(metrics):
        with cols[idx]:
            st.metric(label, value)

    st.markdown("### Recent demo profiles")
    for student in students[:4]:
        with st.container():
            st.markdown(f"<div class='card'><strong>{student['name']}</strong><br>{student['college']} · {student['experience_level']}<br>Skills: {', '.join(student['skills'][:5])}</div>", unsafe_allow_html=True)

elif nav == "Find Teammates":
    students = get_students()
    student_options = {s["name"]: s for s in students}
    selected_name = st.selectbox("Select your profile", list(student_options.keys()))
    current = student_options[selected_name]

    with st.form("matching_form"):
        skill_need = st.selectbox("Skill you need most", ["Frontend Developer", "Python", "Machine Learning", "Cloud Engineer", "Backend Developer", "UI/UX Design"])
        project_category = st.selectbox("Project category", ["AI", "Web Development", "Cloud Computing", "Data Science", "Healthcare", "Sustainability", "Cybersecurity"])
        availability = st.selectbox("Availability preference", ["Weekends", "Evenings", "Weekdays after 6pm", "Flexible"])
        submitted = st.form_submit_button("Find matches")

    if submitted:
        candidates = []
        for student in students:
            if student["id"] == current["id"]:
                continue
            candidates.append({
                "id": student["id"],
                "name": student["name"],
                "skills": student["skills"],
                "interests": student["interests"],
                "experience_level": student["experience_level"],
                "availability": student["availability"],
                "hackathon_interests": student["hackathon_interests"],
                "preferred_roles": student["preferred_roles"],
            })
        ranked = rank_students(current, candidates, preferred_skills=[skill_need], project_category=project_category, availability=availability, min_score=35)
        if not ranked:
            st.warning("No strong matches found. Try broadening the project category or skill preference.")
        for item in ranked[:5]:
            st.markdown(f"<div class='card'><h4>{item['name']}</h4><p>{item['college'] if 'college' in item else 'Demo student'} • {item['experience_level']}</p><p>Skills: {', '.join(item['skills'])}</p><p>Preferred role: {item.get('preferred_roles', 'Open to roles')}</p><p>Project interests: {', '.join(item.get('interests', []))}</p><p><strong>Compatibility score:</strong> {item['compatibility_score']}/100</p><p>{item['match_explanation']}</p><div style='display:flex; gap:10px;'><button>View Profile</button><button>Send Connection Request</button></div></div>", unsafe_allow_html=True)
            if st.button(f"Send connection to {item['name']}", key=f"conn_{item['id']}"):
                db = get_db()
                try:
                    result = send_connection_request(db, current["id"], item["id"])
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.warning(result["message"])
                finally:
                    db.close()

elif nav == "Find a Team":
    st.title("Find a Team")
    teams = list_teams(get_db(), project_category=None)
    category_filter = st.selectbox("Filter team category", ["All", "AI", "Web Development", "Data Science", "Cloud Computing", "Other"])
    if category_filter != "All":
        teams = [t for t in teams if category_filter.lower() in t["target_hackathon"].lower() or category_filter.lower() in t["project_title"].lower()]
    for team in teams:
        st.markdown(f"<div class='card'><h4>{team['team_name']}</h4><p><strong>Project:</strong> {team['project_title']}</p><p><strong>Hackathon:</strong> {team['target_hackathon']}</p><p><strong>Open roles:</strong> {team['open_positions']}</p><p><strong>Required skills:</strong> {team['required_skills']}</p><p><strong>Current members:</strong> {team['member_count']} / {team['max_team_size']}</p><p>{team['short_description']}</p></div>", unsafe_allow_html=True)
        if st.button(f"Apply to {team['team_name']}", key=f"team_apply_{team['id']}"):
            db = get_db()
            try:
                result = submit_team_join_request(db, team["id"], current_student_id if 'current_student_id' in st.session_state else 1)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.warning(result["message"])
            finally:
                db.close()

elif nav == "Hackathons":
    st.title("Hackathon Opportunities")
    with st.form("hackathon_filters"):
        topic = st.selectbox("Topic", ["All", "AI", "Cloud Computing", "Web Development", "Data Science", "Healthcare", "Sustainability"])
        location = st.selectbox("Format", ["All", "Online", "Hybrid", "In-person"])
        submitted = st.form_submit_button("Apply filters")

    if submitted:
        rows = list_hackathons(get_db(), category=None if topic == "All" else topic, location_type=None if location == "All" else location)
    else:
        rows = list_hackathons(get_db())
    for row in rows:
        st.markdown(f"<div class='card'><h4>{row['name']}</h4><p><strong>Organizer:</strong> {row['organizer']}</p><p>{row['description']}</p><p><strong>Categories:</strong> {row['categories']}</p><p><strong>Eligibility:</strong> {row['eligibility']}</p><p><strong>Registration deadline:</strong> {row['registration_deadline']}</p><p><strong>Format:</strong> {row['location_type']}</p><p><strong>Sample data:</strong> {row['is_sample_data']}</p><a href='{row['registration_url']}' target='_blank'>Official registration URL</a></div>", unsafe_allow_html=True)

elif nav == "My Team":
    st.title("My Team")
    current_student_name = st.selectbox("Select profile", [s["name"] for s in get_students()])
    current_student = next(s for s in get_students() if s["name"] == current_student_name)
    with st.form("team_form"):
        st.subheader("Create a team")
        team_name = st.text_input("Team name")
        project_title = st.text_input("Project title")
        project_description = st.text_area("Project description")
        target_hackathon = st.text_input("Target hackathon")
        required_skills = st.text_input("Required skills (comma-separated)")
        open_positions = st.text_input("Open positions")
        max_team_size = st.number_input("Maximum team size", min_value=2, max_value=10, value=5)
        app_deadline = st.date_input("Application deadline")
        short_description = st.text_area("Short description")
        create_team_clicked = st.form_submit_button("Create team")
    if create_team_clicked:
        db = get_db()
        try:
            result = create_team(db, current_student["id"], {
                "team_name": team_name,
                "project_title": project_title,
                "project_description": project_description,
                "target_hackathon": target_hackathon,
                "required_skills": required_skills,
                "open_positions": open_positions,
                "max_team_size": max_team_size,
                "application_deadline": app_deadline.isoformat(),
                "short_description": short_description,
            })
            if result["success"]:
                st.success(result["message"])
            else:
                st.warning(result["message"])
        finally:
            db.close()

    st.subheader("Your team management")
    db = get_db()
    try:
        led_teams = db.query(Team).filter_by(leader_student_id=current_student["id"]).all()
        if not led_teams:
            st.info("You are not leading any teams yet.")
        for team in led_teams:
            st.markdown(f"<div class='card'><h4>{team.team_name}</h4><p>{team.project_title}</p><p>Missing skills: {', '.join(missing_skills_for_team(db, team.id)) or 'None at the moment'}</p></div>", unsafe_allow_html=True)
            team_requests = list_join_requests_for_team(db, team.id)
            if not team_requests:
                st.write("No join requests waiting.")
            for request in team_requests:
                st.write(f"{request['student_name']} wants to join.")
                if st.button(f"Accept {request['student_name']}", key=f"accept_{request['id']}"):
                    result = review_team_join_request(db, team.id, request["id"], current_student["id"], "accept")
                    st.success(result["message"]) if result["success"] else st.warning(result["message"])
                if st.button(f"Reject {request['student_name']}", key=f"reject_{request['id']}"):
                    result = review_team_join_request(db, team.id, request["id"], current_student["id"], "reject")
                    st.success(result["message"]) if result["success"] else st.warning(result["message"])
    finally:
        db.close()

elif nav == "Connections":
    st.title("Connections")
    profile_name = st.selectbox("Student", [s["name"] for s in get_students()])
    profile = next(s for s in get_students() if s["name"] == profile_name)
    db = get_db()
    try:
        requests = list_requests_for_student(db, profile["id"])
        st.subheader("Incoming requests")
        for req in requests["incoming"]:
            st.write(f"{req['sender_name']} wants to connect.")
            if st.button(f"Accept {req['sender_name']}", key=f"accept_conn_{req['id']}"):
                result = update_connection_request(db, req["id"], profile["id"], "accepted")
                st.success(result["message"]) if result["success"] else st.warning(result["message"])
            if st.button(f"Reject {req['sender_name']}", key=f"reject_conn_{req['id']}"):
                result = update_connection_request(db, req["id"], profile["id"], "rejected")
                st.success(result["message"]) if result["success"] else st.warning(result["message"])
        st.subheader("Outgoing requests")
        for req in requests["outgoing"]:
            st.write(f"Pending with {req['receiver_name']}")
            if st.button(f"Cancel to {req['receiver_name']}", key=f"cancel_conn_{req['id']}"):
                result = update_connection_request(db, req["id"], profile["id"], "cancelled")
                st.success(result["message"]) if result["success"] else st.warning(result["message"])
        st.subheader("Accepted connections")
        for req in requests["accepted"]:
            st.write(f"Connected with {req['peer_name']}")
    finally:
        db.close()

elif nav == "My Profile":
    st.title("My Profile")
    profiles = get_students()
    profile_names = [p["name"] for p in profiles]
    selected_name = st.selectbox("Profile to edit", ["Create new profile"] + profile_names)
    if selected_name == "Create new profile":
        form_data = {
            "full_name": st.text_input("Full name"),
            "college": st.text_input("College or university"),
            "department": st.text_input("Department"),
            "academic_year": st.selectbox("Academic year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"]),
            "experience_level": st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"]),
            "skills": st.multiselect("Technical skills", ["Python", "Java", "JavaScript", "React", "HTML/CSS", "Machine Learning", "Artificial Intelligence", "Data Science", "UI/UX Design", "Backend Development", "Cloud Computing", "AWS", "Database Management", "Cybersecurity", "IoT", "Research", "Presentation and Communication"]),
            "interests": st.multiselect("Areas of interest", ["Artificial Intelligence", "Machine Learning", "Healthcare", "Education", "Agriculture", "Sustainability", "FinTech", "Cybersecurity", "Social Impact", "Web Development"]),
            "preferred_roles": st.text_input("Preferred roles"),
            "hackathon_interests": st.text_input("Hackathon interests"),
            "availability": st.selectbox("Availability", ["Weekends", "Evenings", "Weekdays after 6pm", "Flexible", "Weekends and evenings"]),
            "introduction": st.text_area("Short introduction"),
            "github_url": st.text_input("GitHub profile URL (optional)"),
            "portfolio_url": st.text_input("Portfolio URL (optional)"),
        }
        if st.button("Save profile"):
            result = create_or_update_student(form_data)
            st.success(result["message"]) if result["success"] else st.warning(result["message"])
    else:
        current = next(p for p in profiles if p["name"] == selected_name)
        form_data = {
            "full_name": st.text_input("Full name", value=current["name"]),
            "college": st.text_input("College or university", value=current["college"]),
            "department": st.text_input("Department", value=current["department"]),
            "academic_year": st.selectbox("Academic year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"], index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"].index(current["year"])),
            "experience_level": st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(current["experience_level"])),
            "skills": st.multiselect("Technical skills", ["Python", "Java", "JavaScript", "React", "HTML/CSS", "Machine Learning", "Artificial Intelligence", "Data Science", "UI/UX Design", "Backend Development", "Cloud Computing", "AWS", "Database Management", "Cybersecurity", "IoT", "Research", "Presentation and Communication"], default=current["skills"]),
            "interests": st.multiselect("Areas of interest", ["Artificial Intelligence", "Machine Learning", "Healthcare", "Education", "Agriculture", "Sustainability", "FinTech", "Cybersecurity", "Social Impact", "Web Development"], default=current["interests"]),
            "preferred_roles": st.text_input("Preferred roles", value=current["preferred_roles"]),
            "hackathon_interests": st.text_input("Hackathon interests", value=current["hackathon_interests"]),
            "availability": st.selectbox("Availability", ["Weekends", "Evenings", "Weekdays after 6pm", "Flexible", "Weekends and evenings"], index=["Weekends", "Evenings", "Weekdays after 6pm", "Flexible", "Weekends and evenings"].index(current["availability"])),
            "introduction": st.text_area("Short introduction", value=current["introduction"]),
            "github_url": st.text_input("GitHub profile URL (optional)", value=current["github_url"] or ""),
            "portfolio_url": st.text_input("Portfolio URL (optional)", value=current["portfolio_url"] or ""),
        }
        if st.button("Update profile"):
            result = create_or_update_student(form_data, student_id=current["id"])
            st.success(result["message"]) if result["success"] else st.warning(result["message"])

elif nav == "AI Assistant":
    st.title("AI Assistant")
    st.write("This panel demonstrates the Strands decision workflow. When AWS credentials are configured, the app can call the actual model-based decision layer. Otherwise, a clearly labeled development-mode fallback is shown.")
    decider_status = get_decider_status()
    st.code(str(decider_status))
    prompt = st.text_area("Ask the assistant", value="Find me two teammates for an AI hackathon.")
    if st.button("Run decision flow"):
        result = run_demo_agent(prompt, 1)
        st.subheader("Selected tool")
        st.write(result["tool_name"])
        st.subheader("Mode")
        st.write(result["mode"])
        st.subheader("Result")
        st.json(result["result"])

elif nav == "Settings":
    st.title("Settings")
    st.write("Prototype settings and AWS configuration")
    st.code(
        """
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
STRANDS_DECIDER_MODEL_ID=your-model-id
TEAMUP_ENV=development
        """
    )
    st.warning("Do not store secrets in the repository. Use environment variables or the AWS CLI.")

else:
    st.title("TeamUp AI")
    st.write("Welcome to the app.")
