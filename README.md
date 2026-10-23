# TeamUp AI

TeamUp AI is a Streamlit-based student collaboration platform for hackathon teams.

## Quick start on Windows PowerShell

1. Install Python 3.12 or newer from python.org.
2. Open the project folder in VS Code.
3. Create a virtual environment:
   `py -m venv .venv`
4. Activate it:
   `.\.venv\Scripts\Activate.ps1`
5. Install dependencies:
   `python -m pip install --upgrade pip`
   `python -m pip install -r requirements.txt`
6. Copy the environment template:
   `Copy-Item .env.example .env`
7. Update `.env` with your AWS credentials and model configuration when available.
8. Run the app:
   `streamlit run app.py`
9. Run tests:
   `pytest -q`

## Development mode

If AWS credentials or model access are unavailable, the app starts in development/demo mode. The interface clearly labels the data as sample/demo and keeps the deterministic matching logic active.

## AWS setup

The app uses the AWS SDK and Strands Bedrock integration. Configure AWS credentials via environment variables or the AWS CLI.

## Project structure

- `app.py` - Streamlit app entry point
- `database/` - SQLite models and seed data
- `services/` - matching, connections, team, and opportunity logic
- `agent/` - Strands tool and decision workflow code
- `ui/` - shared styling and reusable UI helpers
- `tests/` - unit tests for deterministic logic
- `docs/` - architecture and decision pattern notes

## Hackathon submission resources

See docs in the `docs/` directory for the architecture description and Strands decision pattern.

## Publishing to GitHub

```powershell
git init
git add .
git commit -m "Initial TeamUp AI prototype"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```
