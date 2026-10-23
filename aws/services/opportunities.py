from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.models import HackathonOpportunity


def list_hackathons(db: Session, category: str | None = None, location_type: str | None = None, eligibility: str | None = None) -> List[Dict[str, Any]]:
    query = db.query(HackathonOpportunity)
    if category:
        query = query.filter(HackathonOpportunity.categories.ilike(f"%{category}%"))
    if location_type:
        query = query.filter(HackathonOpportunity.location_type.ilike(f"%{location_type}%"))
    if eligibility:
        query = query.filter(HackathonOpportunity.eligibility.ilike(f"%{eligibility}%"))
    rows = query.all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "organizer": row.organizer,
            "description": row.description,
            "categories": row.categories,
            "eligibility": row.eligibility,
            "registration_deadline": row.registration_deadline.isoformat() if row.registration_deadline else None,
            "event_dates": row.event_dates,
            "location_type": row.location_type,
            "registration_url": row.registration_url,
            "is_sample_data": bool(row.is_sample_data),
        }
        for row in rows
    ]
