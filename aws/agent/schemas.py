from __future__ import annotations

from typing import Any, Dict, List


DECIDER_SYSTEM_PROMPT = """
You are the TeamUp AI decision layer. Pick the best action for the user's request.
Use the available tools and return only a valid JSON object with: tool_name, confidence, rationale.
"""


def build_tool_result(tool_name: str, data: Any, rationale: str, confidence: float = 0.8) -> Dict[str, Any]:
    return {
        "tool_name": tool_name,
        "confidence": confidence,
        "rationale": rationale,
        "data": data,
    }
