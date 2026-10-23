from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

EXPERIENCE_ORDER = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

MATCH_WEIGHTS = {
    "skills": 0.38,
    "shared_interests": 0.18,
    "hackathon": 0.16,
    "experience": 0.12,
    "availability": 0.08,
    "role_fit": 0.08,
}


def _as_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    if isinstance(value, (list, tuple, set)):
        return {str(item).strip() for item in value if str(item).strip()}
    return {str(value).strip()}


def _skill_overlap(student_skills: Iterable[str], desired_skills: Iterable[str]) -> int:
    s1 = _as_set(student_skills)
    s2 = _as_set(desired_skills)
    return len(s1 & s2)


def _normalize_score(raw: float) -> int:
    return max(0, min(100, int(round(raw))))


def _experience_fit(student_exp: str, current_exp: str) -> float:
    current = EXPERIENCE_ORDER.get((current_exp or "Beginner").strip().title(), 1)
    cand = EXPERIENCE_ORDER.get((student_exp or "Beginner").strip().title(), 1)
    delta = abs(cand - current)
    if delta == 0:
        return 1.0
    if delta == 1:
        return 0.75
    return 0.5


def estimate_compatibility(
    current_student: Dict[str, Any],
    candidate: Dict[str, Any],
    preferred_skills: Optional[Iterable[str]] = None,
    target_project_category: Optional[str] = None,
) -> Dict[str, Any]:
    if not current_student or not candidate:
        return {"score": 0, "explanation": "Incomplete profile data prevents a valid compatibility score."}

    current_skills = _as_set(current_student.get("skills"))
    candidate_skills = _as_set(candidate.get("skills"))
    desired_skills = _as_set(preferred_skills or current_student.get("desired_skills"))

    skill_matches = _skill_overlap(candidate_skills, desired_skills)
    if desired_skills:
        skill_ratio = (len(candidate_skills & desired_skills) / len(desired_skills)) if desired_skills else 0
    else:
        skill_ratio = len(candidate_skills & current_skills) / max(len(current_skills), 1)

    complement_count = len((candidate_skills - current_skills) & desired_skills)
    shared_interests = len(_as_set(candidate.get("interests")) & _as_set(current_student.get("interests")))
    interest_total = max(len(_as_set(current_student.get("interests"))), 1)
    interest_score = (shared_interests / interest_total) * 100

    hackathon_match = 1.0 if not target_project_category else (
        1.0 if target_project_category.lower() in str(candidate.get("hackathon_interests", "")).lower() else 0.5
    )

    experience_score = _experience_fit(candidate.get("experience_level", "Beginner"), current_student.get("experience_level", "Beginner"))
    availability_score = 1.0 if str(candidate.get("availability", "")).lower() == str(current_student.get("availability", "")).lower() else 0.7
    role_score = 1.0 if str(candidate.get("preferred_roles", "")).lower() and any(role.lower() in str(candidate.get("preferred_roles", "")).lower() for role in _as_set(current_student.get("desired_roles"))) else 0.8

    total = (
        skill_ratio * 100 * MATCH_WEIGHTS["skills"]
        + (min(interest_score, 100) / 100) * 100 * MATCH_WEIGHTS["shared_interests"]
        + (hackathon_match * 100) * MATCH_WEIGHTS["hackathon"]
        + (experience_score * 100) * MATCH_WEIGHTS["experience"]
        + (availability_score * 100) * MATCH_WEIGHTS["availability"]
        + (role_score * 100) * MATCH_WEIGHTS["role_fit"]
    )

    score = _normalize_score(total)

    pieces = []
    if complement_count:
        pieces.append(f"{candidate.get('name', 'This student')} brings {complement_count} complementary skill match(es) you need.")
    if shared_interests:
        pieces.append(f"You share {shared_interests} interest area(s), including {', '.join(sorted(list((_as_set(candidate.get('interests')) & _as_set(current_student.get('interests'))))[:2]))}.")
    if target_project_category and target_project_category.lower() in str(candidate.get("hackathon_interests", "")).lower():
        pieces.append(f"Their profile aligns with your preferred {target_project_category} focus.")
    if experience_score >= 0.75:
        pieces.append("Experience levels are compatible for this collaboration.")
    if not pieces:
        pieces.append("Profile overlap is moderate, so the recommendation is a cautious fit based on general project alignment.")

    explanation = " ".join(pieces)
    return {"score": score, "explanation": explanation, "skill_matches": skill_matches, "shared_interests": shared_interests}


def rank_students(
    current_student: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    preferred_skills: Optional[Iterable[str]] = None,
    project_category: Optional[str] = None,
    availability: Optional[str] = None,
    min_score: int = 0,
) -> List[Dict[str, Any]]:
    ranked = []
    for candidate in candidates:
        if candidate.get("id") == current_student.get("id"):
            continue
        if availability and str(candidate.get("availability", "")).lower() != str(availability).lower():
            continue
        result = estimate_compatibility(current_student, candidate, preferred_skills, project_category)
        if result["score"] >= min_score:
            candidate_record = dict(candidate)
            candidate_record["compatibility_score"] = result["score"]
            candidate_record["match_explanation"] = result["explanation"]
            ranked.append(candidate_record)
    return sorted(ranked, key=lambda item: item["compatibility_score"], reverse=True)
