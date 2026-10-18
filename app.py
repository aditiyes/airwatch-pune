import math
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AirWatch Pune", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Pune": {"city": "Pune", "lat": 18.5204, "lng": 73.8567, "zone": "West", "offset": 0, "phase": 1.0, "area_factor": 1.2},
    "Kharadi": {"city": "Kharadi", "lat": 18.5516, "lng": 73.9442, "zone": "East", "offset": 1, "phase": 1.4, "area_factor": 1.35},
    "Hinjewadi": {"city": "Hinjewadi", "lat": 18.5913, "lng": 73.7387, "zone": "Industrial", "offset": 2, "phase": 1.8, "area_factor": 1.55},
    "Shivajinagar": {"city": "Shivajinagar", "lat": 18.5314, "lng": 73.8446, "zone": "Central", "offset": 3, "phase": 2.1, "area_factor": 1.28},
    "Baner": {"city": "Baner", "lat": 18.5594, "lng": 73.7795, "zone": "North", "offset": 4, "phase": 2.6, "area_factor": 1.18},
}


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def aqi_category(aqi: float) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def health_advice(aqi: float) -> Dict[str, Any]:
    if aqi <= 50:
        return {
            "heading": "Outdoor conditions are comfortable",
            "details": [
                "Air quality is safe for regular outdoor activity.",
                "Keep an eye on afternoon traffic peaks during dry spells.",
                "No special precautions are required for most people."
            ],
        }
    if aqi <= 100:
        return {
            "heading": "Sensitive groups should reduce exertion",
            "details": [
                "Keep outdoor activity moderate and avoid prolonged exercise.",
                "Children, seniors, and asthma patients should stay alert.",
                "Use a mask during commute hours when needed."
            ],
        }
    if aqi <= 150:
        return {
            "heading": "Unhealthy for sensitive groups",
            "details": [
                "Avoid long outdoor runs and strenuous activity.",
                "Limit exposure near traffic corridors and industrial belts.",
                "Keep indoor air cleaner with ventilation and filtration."
            ],
        }
    return {
        "heading": "High-risk air pollution alert",
        "details": [
            "Avoid non-essential outdoor exposure.",
            "Prefer indoor exercise and keep windows closed during peak-hours.",
            "Children, the elderly, and anyone with respiratory conditions should remain cautious."
        ],
    }


def get_location_profile(city: str) -> Dict[str, Any]:
    return LOCATIONS.get(city.strip(), LOCATIONS["Pune"]) 


def generate_history(city: str, hours: int = 168) -> List[Dict[str, Any]]:
    profile = get_location_profile(city)
    rng = np.random.default_rng(42 + sum(ord(ch) for ch in city))
    now = datetime.now()
    points: List[Dict[str, Any]] = []

    for step in range(hours):
        ts = now - timedelta(hours=hours - step - 1)
        hour = ts.hour
        rush = 1 if hour in (8, 9, 10, 17, 18, 19, 20) else 0
        daily_wave = 22 * math.sin((hour / 24) * math.tau + profile["phase"])
        week_wave = 18 * math.sin((step / 24) * math.tau * 0.15)
        base = 94 + profile["area_factor"] * 28 + daily_wave + week_wave
        aqi = max(38, base + rush * 26 + float(rng.normal(0, 12)))
        pm25 = max(18, aqi * 0.69)
        pm10 = max(35, aqi * 0.92)
        no2 = max(12, aqi * 0.21)
        o3 = max(18, aqi * 0.29)
        co = max(0.35, aqi * 0.028)
        so2 = max(5, aqi * 0.13)
        nh3 = max(8, aqi * 0.16)
        temp = 27 + 8 * math.sin((hour / 24) * math.tau + 0.7)
        humidity = 48 + 18 * math.cos((hour / 24) * math.tau - 0.8)
        wind_speed = 6 + 4 * math.sin((hour / 24) * math.tau + 1.6)
        rainfall = max(0.0, 2.5 * math.sin((hour / 24) * math.tau + 1.2) + 1.8)

        points.append(
            {
                "timestamp": ts.isoformat(timespec="hours"),
                "aqi": round(float(aqi), 1),
                "pm25": round(float(pm25), 1),
                "pm10": round(float(pm10), 1),
                "no2": round(float(no2), 1),
                "o3": round(float(o3), 1),
                "co": round(float(co), 2),
                "so2": round(float(so2), 1),
                "nh3": round(float(nh3), 1),
                "temperature": round(float(temp), 1),
                "humidity": round(float(humidity), 1),
                "wind_speed": round(float(wind_speed), 1),
                "rainfall": round(float(rainfall), 1),
            }
        )

    return points


def generate_forecast(city: str, history: List[Dict[str, Any]], horizon_hours: int = 72) -> List[Dict[str, Any]]:
    last = history[-1]
    rng = np.random.default_rng(101 + sum(ord(ch) for ch in city))
    profile = get_location_profile(city)
    forecast: List[Dict[str, Any]] = []

    for step in range(horizon_hours):
        ts = datetime.now() + timedelta(hours=step + 1)
        hour = ts.hour
        rush = 1 if hour in (8, 9, 10, 17, 18, 19, 20) else 0
        drift = 0.15 * step
        wave = 20 * math.sin((hour / 24) * math.tau + profile["phase"]) + 6 * math.sin(step / 6)
        aqi = last["aqi"] + drift + wave + rush * 18 + float(rng.normal(0, 8))
        aqi = clamp(float(aqi), 35.0, 260.0)
        pm25 = max(18.0, aqi * 0.68)
        pm10 = max(32.0, aqi * 0.94)
        no2 = max(12.0, aqi * 0.23)
        o3 = max(18.0, aqi * 0.3)
        co = max(0.35, aqi * 0.029)
        so2 = max(5.0, aqi * 0.13)
        nh3 = max(8.0, aqi * 0.16)

        forecast.append(
            {
                "timestamp": ts.isoformat(timespec="hours"),
                "aqi": round(float(aqi), 1),
                "pm25": round(float(pm25), 1),
                "pm10": round(float(pm10), 1),
                "no2": round(float(no2), 1),
                "o3": round(float(o3), 1),
                "co": round(float(co), 2),
                "so2": round(float(so2), 1),
                "nh3": round(float(nh3), 1),
            }
        )

    return forecast


def build_dashboard(city: str) -> Dict[str, Any]:
    history = generate_history(city)
    forecast = generate_forecast(city, history, 72)
    current = history[-1]
    current_category = aqi_category(current["aqi"])
    advice = health_advice(current["aqi"])
    avg_24 = round(float(np.mean([point["aqi"] for point in history[-24:]])), 1)
    max_24 = round(float(max(point["aqi"] for point in history[-24:])), 1)
    forecast_peak = max(forecast, key=lambda item: item["aqi"])

    return {
        "city": city,
        "current": {
            "aqi": current["aqi"],
            "pm25": current["pm25"],
            "pm10": current["pm10"],
            "no2": current["no2"],
            "o3": current["o3"],
            "co": current["co"],
            "so2": current["so2"],
            "nh3": current["nh3"],
            "temperature": current["temperature"],
            "humidity": current["humidity"],
            "wind_speed": current["wind_speed"],
            "rainfall": current["rainfall"],
        },
        "status": {
            "category": current_category,
            "color": {
                "Good": "#16a34a",
                "Moderate": "#f59e0b",
                "Unhealthy for Sensitive Groups": "#f97316",
                "Unhealthy": "#ef4444",
                "Very Unhealthy": "#a855f7",
                "Hazardous": "#7f1d1d",
            }[current_category],
            "advice": advice,
        },
        "summary": {
            "avg_24h": avg_24,
            "max_24h": max_24,
            "forecast_peak_aqi": forecast_peak["aqi"],
            "forecast_peak_time": forecast_peak["timestamp"],
            "trend": "Rising" if forecast[0]["aqi"] > current["aqi"] else "Stable",
        },
        "history": history,
        "forecast": forecast,
        "locations": sorted(LOCATIONS.keys()),
    }


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/locations")
async def get_locations() -> Dict[str, List[str]]:
    return {"locations": sorted(LOCATIONS.keys())}


@app.get("/api/overview")
async def get_dashboard_api(city: str = "Pune") -> Dict[str, Any]:
    return build_dashboard(city)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
