# TeamUp AI architecture

TeamUp AI is a modular Streamlit prototype for student hackathon team matching. It uses SQLite for local persistence and a service layer for core business logic. The UI is intentionally simple and polished for hackathon demos.

## Layers

- Presentation: Streamlit UI and reusable CSS styling.
- Application services: student matching, connection requests, team management, and opportunity filtering.
- Data layer: SQLAlchemy models and SQLite database in `teamup_ai.db`.
- AI layer: Strands tools + optional Bedrock/Decider workflow behind a clear development-mode fallback.

## Decision workflow

When an AI assistant request is sent:

1. The user prompt is received in the Streamlit UI.
2. The app checks whether AWS credentials and a configured model are available.
3. If available, the Strands `Agent` selects the most relevant tool using the configured Bedrock model.
4. The chosen tool runs deterministic Python logic against the app database.
5. The result is returned to the UI and rendered in natural language.
6. If the AI service is unavailable, the app displays a clear development-mode response instead of pretending it is live AI.

## Files

- `app.py` – entry point
- `database/` – SQLite models and seed data
- `services/` – deterministic logic for matching and team workflow
- `agent/` – tool definitions and Bedrock integration
- `ui/` – design styling
