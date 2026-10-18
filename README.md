# AirWatch Pune

AirWatch Pune is a demo air-quality forecasting and health-advisory dashboard for Pune. It uses generated sample pollution data and forecast logic; it does not currently fetch live sensor data or train a machine-learning model.

## Live demo

Visit **[AirWatch Pune](https://airwatch-pune.onrender.com)**.

## Features

- Pune location selector with area-specific profiling
- Real-time AQI and pollutant overview
- 24-hour, 48-hour, and 72-hour forecast views
- Health and safety guidance based on AQI thresholds
- Clean dashboard UI for operators and end users
- FastAPI backend with mocked data generation and forecast logic

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate  # Linux/macOS
# or .\.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then open: http://localhost:8000

## Project structure

- `app.py` — FastAPI application and synthetic forecasting engine
- `templates/index.html` — dashboard layout
- `static/styles.css` — dashboard styling
- `static/app.js` — render logic and API calls

## Deploying

This project is ready to be hosted on Render or any Python-capable app platform. The Render Blueprint uses the platform-provided port; a sample Dockerfile is included for container deployment.

```bash
docker build -t airwatch-pune .
docker run -p 8000:8000 airwatch-pune
```

## GitHub

Initialize a repo and push to GitHub:

```bash
git init
git add .
git commit -m "Initial AirWatch Pune dashboard"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```
