from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.models import ConnectionRequest, Student


def send_connection_request(db: Session, sender_id: int, receiver_id: int) -> Dict[str, Any]:
    if sender_id == receiver_id:
        return {"success": False, "message": "You cannot send a request to yourself."}
    existing = db.query(ConnectionRequest).filter(
        ConnectionRequest.sender_id == sender_id,
        ConnectionRequest.receiver_id == receiver_id,
    ).first()
    if existing:
        return {"success": False, "message": "A connection request already exists for this pair."}
    if not db.query(Student).filter_by(id=receiver_id).first():
        return {"success": False, "message": "Target student profile was not found."}
    request = ConnectionRequest(sender_id=sender_id, receiver_id=receiver_id, status="pending")
    db.add(request)
    db.commit()
    return {"success": True, "message": "Connection request sent.", "request_id": request.id}


def update_connection_request(db: Session, request_id: int, actor_id: int, status: str) -> Dict[str, Any]:
    request = db.query(ConnectionRequest).filter_by(id=request_id).first()
    if not request:
        return {"success": False, "message": "Request not found."}
    if request.receiver_id != actor_id and request.sender_id != actor_id:
        return {"success": False, "message": "You are not allowed to manage this request."}
    valid = {"accepted", "rejected", "cancelled"}
    if status.lower() not in valid:
        return {"success": False, "message": "Invalid connection status."}
    if status.lower() == "cancelled" and request.sender_id != actor_id:
        return {"success": False, "message": "Only the sender can cancel a pending request."}
    if request.status in {"accepted", "rejected", "cancelled"}:
        return {"success": False, "message": "This request is already resolved."}
    request.status = status.lower()
    db.commit()
    return {"success": True, "message": f"Request marked as {status.lower()}.", "status": request.status}


def list_requests_for_student(db: Session, student_id: int) -> Dict[str, List[Dict[str, Any]]]:
    incoming = db.query(ConnectionRequest).filter(
        ConnectionRequest.receiver_id == student_id,
        ConnectionRequest.status == "pending",
    ).all()
    outgoing = db.query(ConnectionRequest).filter(
        ConnectionRequest.sender_id == student_id,
        ConnectionRequest.status == "pending",
    ).all()
    accepted = db.query(ConnectionRequest).filter(
        (ConnectionRequest.sender_id == student_id) | (ConnectionRequest.receiver_id == student_id),
        ConnectionRequest.status == "accepted",
    ).all()
    return {
        "incoming": [
            {
                "id": req.id,
                "sender_id": req.sender_id,
                "sender_name": db.query(Student).filter_by(id=req.sender_id).first().full_name,
                "status": req.status,
            }
            for req in incoming
        ],
        "outgoing": [
            {
                "id": req.id,
                "receiver_id": req.receiver_id,
                "receiver_name": db.query(Student).filter_by(id=req.receiver_id).first().full_name,
                "status": req.status,
            }
            for req in outgoing
        ],
        "accepted": [
            {
                "id": req.id,
                "peer_id": req.receiver_id if req.sender_id == student_id else req.sender_id,
                "peer_name": db.query(Student).filter_by(id=(req.receiver_id if req.sender_id == student_id else req.sender_id)).first().full_name,
                "status": req.status,
            }
            for req in accepted
        ],
    }
