
const alertBanner = document.getElementById('alert-banner');

const ctx = document.getElementById('powerChart').getContext('2d');
const powerChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Power (W)',
            data: [],
            borderColor: '#1a73e8',
            backgroundColor: 'rgba(26,115,232,0.2)',
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#1a73e8',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: '#1a73e8',
                titleColor: 'white',
                bodyColor: 'white'
            }
        },
        scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Power (W)' } },
            x: { title: { display: true, text: 'Timestamp' } }
        }
    }
});


function formatDate(ts) {
    const d = new Date(ts);
    return d.toLocaleString("fr-FR", {
        day: "2-digit", month: "2-digit", year: "numeric",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
});
}

async function fetchLatestMeasurements() {
    try {
        const response = await fetch('/api/measurements/latest/');
        const data = await response.json();

        // Update table
        const tbody = document.getElementById('measurement-body');
        tbody.innerHTML = "";
        let alertShown = false;
        if (data.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="5">No measurements available</td>`;
            tbody.appendChild(tr);
            alertBanner.style.display = 'none';
            return;
        }
        data.forEach(m => {
            const tr = document.createElement('tr');
            if (m.power > powerThreshold) alertShown = true;

            tr.innerHTML = `
            <td>
                ${formatDate(m.timestamp)}
            </td>
            <td ${m.power > powerThreshold ? 'class="alert"' : ''}>${m.power}</td>
            <td>${m.voltage}</td>
            <td>${m.current}</td>
            <td>${m.energy}</td>
            `;


            tbody.appendChild(tr);
        });

        alertBanner.style.display = alertShown ? 'block' : 'none';

        const labels = data.map(m => new Date(m.timestamp).toLocaleTimeString());
        const powerValues = data.map(m => m.power);

        powerChart.data.labels = labels.reverse();
        powerChart.data.datasets[0].data = powerValues.reverse();
        powerChart.update();

    } catch (err) {
        console.error("Error fetching measurements:", err);
    }
}

// Polling every 2 seconds
setInterval(fetchLatestMeasurements, 2000);
fetchLatestMeasurements(); // initial load