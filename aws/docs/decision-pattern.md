# Reusable Strands decision pattern

Use a single pattern for all AI decisions:

1. Define domain tools with clear names and schemas.
2. Pass the available tools to a `strands.Agent`.
3. Require model access via environment variables before making a real call.
4. Keep the actual decision model separate from the deterministic business logic.
5. If the model is unavailable, return a graceful development-mode result.

Example structure:

```python
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(region_name="us-east-1", model_id="<configured-model-id>")
agent = Agent(model=model, tools=[find_teammates, find_existing_teams])
result = agent("I need a frontend developer for an AI hackathon.")
```

The model decides which tool to call. The tool itself executes deterministic Python logic against SQLite data.
