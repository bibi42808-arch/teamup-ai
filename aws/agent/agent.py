from __future__ import annotations

import os
from typing import Any, Dict, List

from strands import Agent
from strands.models import BedrockModel


def has_agent_configuration() -> bool:
    return bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))


def create_agent() -> Agent | None:
    if not has_agent_configuration():
        return None
    model_id = os.getenv("STRANDS_DECIDER_MODEL_ID")
    if not model_id:
        return None
    model = BedrockModel(region_name=os.getenv("AWS_REGION", "us-east-1"), model_id=model_id)
    return Agent(model=model)


def run_decision_flow(prompt: str, tools: List[Any]) -> Dict[str, Any]:
    agent = create_agent()
    if not agent:
        return {"available": False, "reason": "AWS credentials or a configured Strands/Bedrock model are missing."}
    try:
        result = agent(prompt, tools=tools)
        return {"available": True, "result": str(result)}
    except Exception as exc:
        return {"available": False, "reason": f"AI agent error: {exc}"}
