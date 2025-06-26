const directions = ["north", "south", "east", "west"];

function updateVideoFeeds() {
    directions.forEach(dir => {
        const img = document.getElementById(`video-${dir}`);
        // For live video, use the streaming endpoint
        img.src = `/api/video/${dir}?t=${Date.now()}`; // cache-busting
    });
}

function updateDetections() {
    fetch('/api/detections')
        .then(res => res.json())
        .then(data => {
            directions.forEach(dir => {
                document.getElementById(`count-${dir}`).textContent = data[dir]?.vehicles ?? '-';
            });
        });
}

function updateTrafficLight() {
    fetch('/api/traffic-light')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('traffic-light-state');
            container.innerHTML = '';
            directions.forEach(dir => {
                const state = data.states[dir];
                const div = document.createElement('div');
                div.className = `light ${state}`;
                div.textContent = `${dir.charAt(0).toUpperCase() + dir.slice(1)}: ${state.toUpperCase()}`;
                container.appendChild(div);
            });
            // Show which is green and for how long
            const info = document.createElement('div');
            info.className = 'light-info';
            info.textContent = `Current Green: ${data.green.toUpperCase()} (${data.duration}s)`;
            container.appendChild(info);
        });
}

function updateLogs() {
    fetch('/api/logs')
        .then(res => res.json())
        .then(data => {
            const logs = data.logs || [];
            const ul = document.getElementById('logs');
            ul.innerHTML = '';
            logs.forEach(log => {
                const li = document.createElement('li');
                li.textContent = `[${log.time}] ${log.event}`;
                ul.appendChild(li);
            });
        });
}

function updateStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
                <div>Total Vehicles: <b>${data.total_vehicles}</b></div>
                <div>Average Wait Time: <b>${data.average_wait_time}</b> s</div>
            `;
        });
}

function updateAll() {
    updateVideoFeeds();
    updateDetections();
    updateTrafficLight();
    updateLogs();
    updateStats();
}

// Initial load
updateAll();
// Periodic updates
setInterval(updateAll, 3000);
