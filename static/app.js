const state = {
  locations: [],
  activeCity: 'Pune',
  forecastChart: null,
  pollutantChart: null,
};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderLocationSelector(locations) {
  const container = document.getElementById('locationSwitcher');
  container.innerHTML = '';

  locations.forEach((location) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = location;
    button.className = `location-button ${location === state.activeCity ? 'active' : ''}`;
    button.addEventListener('click', () => {
      state.activeCity = location;
      loadDashboard();
    });
    container.appendChild(button);
  });
}

function renderOverview(data) {
  const current = data.current;
  const status = data.status;
  const summary = data.summary;

  document.getElementById('aqiValue').textContent = `${Math.round(current.aqi)}`;
  document.getElementById('statusBadge').textContent = status.category;
  document.getElementById('statusBadge').style.background = `${status.color}22`;
  document.getElementById('statusBadge').style.borderColor = `${status.color}88`;
  document.getElementById('statusBadge').style.color = '#f8fafc';

  document.getElementById('summaryText').textContent = `${data.city}: ${status.advice.heading}. ${status.advice.details[0]}`;
  document.getElementById('pm25Value').textContent = `${current.pm25} µg/m³`;
  document.getElementById('pm10Value').textContent = `${current.pm10} µg/m³`;
  document.getElementById('no2Value').textContent = `${current.no2} ppb`;
  document.getElementById('o3Value').textContent = `${current.o3} ppb`;

  document.getElementById('avg24Value').textContent = `${summary.avg_24h}`;
  document.getElementById('peak24Value').textContent = `${summary.max_24h}`;
  document.getElementById('peakWindowValue').textContent = new Date(summary.forecast_peak_time).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
  });
  document.getElementById('trendValue').textContent = summary.trend;

  const adviceHeading = document.getElementById('adviceHeading');
  adviceHeading.textContent = status.advice.heading;

  const adviceList = document.getElementById('adviceList');
  adviceList.innerHTML = status.advice.details.map((item) => `<li>${item}</li>`).join('');

  const recommendationList = document.getElementById('recommendationList');
  const recommendations = [
    `Keep outdoor workouts shorter in ${data.city} when AQI rises above 100.`,
    'Use a mask on busy roads and near industrial zones during commute peaks.',
    'Check forecast spikes before planning long walks, cycling, or school sports.',
    'Prefer indoor air filtration and ventilation during severe pollution windows.'
  ];
  recommendationList.innerHTML = recommendations.map((item) => `<li>${item}</li>`).join('');

  renderForecastChart(data.forecast);
  renderPollutantChart(data.current);
}

function renderForecastChart(forecast) {
  const labels = forecast.map((point) => new Date(point.timestamp).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric'
  }));
  const values = forecast.map((point) => point.aqi);

  const ctx = document.getElementById('forecastChart').getContext('2d');
  if (state.forecastChart) {
    state.forecastChart.destroy();
  }

  state.forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'AQI forecast',
        data: values,
        borderColor: '#65d0ff',
        backgroundColor: 'rgba(101, 208, 255, 0.15)',
        borderWidth: 3,
        fill: true,
        tension: 0.38,
        pointRadius: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: '#a7c7d8', maxTicksLimit: 8 },
          grid: { display: false },
        },
        y: {
          ticks: { color: '#a7c7d8' },
          grid: { color: 'rgba(148,163,184,0.12)' },
          beginAtZero: false,
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

function renderPollutantChart(current) {
  const ctx = document.getElementById('pollutantChart').getContext('2d');
  const values = [
    current.pm25,
    current.pm10,
    current.no2,
    current.o3,
    current.so2,
  ];
  const labels = ['PM2.5', 'PM10', 'NO₂', 'O₃', 'SO₂'];

  if (state.pollutantChart) {
    state.pollutantChart.destroy();
  }

  state.pollutantChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Current pollutant levels',
        data: values,
        backgroundColor: ['#60a5fa', '#22c55e', '#f59e0b', '#f97316', '#ef4444'],
        borderRadius: 10,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: '#a7c7d8' },
          grid: { display: false },
        },
        y: {
          ticks: { color: '#a7c7d8' },
          grid: { color: 'rgba(148,163,184,0.12)' },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

async function loadDashboard() {
  try {
    const data = await fetchJson(`/api/overview?city=${encodeURIComponent(state.activeCity)}`);
    renderOverview(data);
  } catch (error) {
    console.error(error);
    document.getElementById('summaryText').textContent = 'Unable to load air-quality data right now.';
  }
}

async function init() {
  try {
    const data = await fetchJson('/api/locations');
    state.locations = data.locations;
    renderLocationSelector(state.locations);
    loadDashboard();
  } catch (error) {
    console.error(error);
  }
}

init();
