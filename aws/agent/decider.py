from __future__ import annotations

import os
from typing import Any, Dict


def is_development_mode() -> bool:
    return os.getenv("TEAMUP_ENV", "development").lower() == "development" or not bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))


def get_decider_status() -> Dict[str, Any]:
    return {
        "mode": "development" if is_development_mode() else "bedrock",
        "model_id": os.getenv("STRANDS_DECIDER_MODEL_ID", "not configured"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "awsConfigured": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")),
    }
