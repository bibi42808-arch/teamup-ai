from database.db import SessionLocal
from database.models import ConnectionRequest
from database.seed import initialize_database
from services.connections import send_connection_request, update_connection_request


def setup_db():
    db = SessionLocal()
    initialize_database(db)
    return db


def test_prevent_duplicate_connection_requests():
    db = setup_db()
    first = send_connection_request(db, 1, 2)
    second = send_connection_request(db, 1, 2)
    assert first["success"] is True
    assert second["success"] is False
    db.close()


def test_accepting_and_rejecting_requests():
    db = setup_db()
    send_connection_request(db, 3, 1)
    request = db.query(ConnectionRequest).filter_by(sender_id=3, receiver_id=1).first()
    accepted = update_connection_request(db, request.id, 1, "accepted")
    rejected = update_connection_request(db, request.id, 1, "rejected")
    assert accepted["success"] is True
    assert rejected["success"] is False
    db.close()
