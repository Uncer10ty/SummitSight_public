//  Load results from sessionStorage 
const resultsData = JSON.parse(sessionStorage.getItem('analysisResults'));
const overlayImageSrc = sessionStorage.getItem('overlayImage');
const extractionTime = sessionStorage.getItem('extractionTime');
const extractionMethod = sessionStorage.getItem('extractionMethod');

const overlayImageResult = document.getElementById('overlayImageResult');
const resultsCard = document.getElementById('resultsCard');

const RESULT_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
const RESULT_EMOJIS = ['🔵', '🟢', '🟠', '🔴', '🟣'];

let map = null;

window.addEventListener('DOMContentLoaded', () => {
    if (!resultsData) {
        window.location.href = 'index.html';
        return;
    }
    displayResults();
});

function displayResults() {
    // Show extracted skyline overlay
    if (overlayImageSrc && overlayImageResult) {
        overlayImageResult.src = overlayImageSrc;
    } else if (overlayImageResult) {
        overlayImageResult.parentElement.style.display = 'none';
    }

    // Performance summary
    displayPerformanceSummary();

    // Index alignments by rank for embedding in match cards
    const alignments = resultsData.alignments || (resultsData.alignment ? [resultsData.alignment] : []);

    if (resultsData.matches && resultsData.matches.length > 0) {
        displayMatches(resultsData.matches, alignments);
        initMap(resultsData.matches);
    } else {
        displayNoResults();
    }
}

//  Performance summary 
function displayPerformanceSummary() {
    const el = document.getElementById('performanceSummary');
    if (!el) return;

    const segEl = document.getElementById('perfSegmentation');
    const searchEl = document.getElementById('perfSearch');
    const confEl = document.getElementById('perfConfidence');

    if (extractionMethod && extractionTime) {
        const segSecs = (parseInt(extractionTime, 10) / 1000).toFixed(1);
        segEl.textContent = `${extractionMethod} — ${segSecs}s`;
    }

    if (resultsData.processing_time_ms) {
        const searchSecs = (resultsData.processing_time_ms / 1000).toFixed(1);
        searchEl.textContent = `${searchSecs}s`;
    } else if (resultsData.processingTime) {
        const searchSecs = (resultsData.processingTime / 1000).toFixed(1);
        searchEl.textContent = `${searchSecs}s`;
    }

    if (resultsData.matches && resultsData.matches.length > 0) {
        const topConf = resultsData.matches[0].confidence;
        confEl.textContent = `${topConf.toFixed(1)}%`;
    }

    el.style.display = 'block';
}

//  Skyline alignment canvas (drawn inline per candidate) 
function drawSingleAlignment(canvas, alignment) {
    if (!alignment.ref_skyline || !alignment.query_skyline) return;

    const ref = alignment.ref_skyline;
    const query = alignment.query_skyline;
    const len = Math.min(ref.length, query.length);

    const dpr = window.devicePixelRatio || 1;
    const displayWidth = canvas.parentElement.clientWidth;
    const displayHeight = Math.min(200, displayWidth * 0.28);
    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    let yMin = Infinity, yMax = -Infinity;
    for (let i = 0; i < len; i++) {
        yMin = Math.min(yMin, ref[i], query[i]);
        yMax = Math.max(yMax, ref[i], query[i]);
    }
    const yPad = (yMax - yMin) * 0.1 || 1;
    yMin -= yPad;
    yMax += yPad;

    const padLeft = 40, padRight = 10, padTop = 10, padBot = 25;
    const plotW = displayWidth - padLeft - padRight;
    const plotH = displayHeight - padTop - padBot;

    function toX(i) { return padLeft + (i / (len - 1)) * plotW; }
    function toY(v) { return padTop + plotH - ((v - yMin) / (yMax - yMin)) * plotH; }

    // Background
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    ctx.fillStyle = isDark ? '#1e293b' : '#f9fafb';
    ctx.fillRect(0, 0, displayWidth, displayHeight);

    // Grid
    ctx.strokeStyle = isDark ? '#334155' : '#e5e7eb';
    ctx.lineWidth = 0.5;
    const nGrid = 5;
    for (let g = 0; g <= nGrid; g++) {
        const gy = padTop + (g / nGrid) * plotH;
        ctx.beginPath(); ctx.moveTo(padLeft, gy); ctx.lineTo(padLeft + plotW, gy); ctx.stroke();
    }

    // Y-axis labels
    ctx.fillStyle = isDark ? '#94a3b8' : '#6b7280';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'right';
    for (let g = 0; g <= nGrid; g++) {
        const val = yMin + ((nGrid - g) / nGrid) * (yMax - yMin);
        ctx.fillText(val.toFixed(1) + '°', padLeft - 4, padTop + (g / nGrid) * plotH + 3);
    }

    // Filled area under reference
    ctx.fillStyle = 'rgba(70, 130, 180, 0.15)';
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(0));
    for (let i = 0; i < len; i++) ctx.lineTo(toX(i), toY(ref[i]));
    ctx.lineTo(toX(len - 1), toY(0));
    ctx.closePath();
    ctx.fill();

    // Reference line
    ctx.strokeStyle = '#4682B4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < len; i++) { i === 0 ? ctx.moveTo(toX(i), toY(ref[i])) : ctx.lineTo(toX(i), toY(ref[i])); }
    ctx.stroke();

    // Query line (dashed)
    ctx.strokeStyle = '#FF4500';
    ctx.lineWidth = 1.8;
    ctx.setLineDash([6, 3]);
    ctx.beginPath();
    for (let i = 0; i < len; i++) { i === 0 ? ctx.moveTo(toX(i), toY(query[i])) : ctx.lineTo(toX(i), toY(query[i])); }
    ctx.stroke();
    ctx.setLineDash([]);

    // X-axis label
    ctx.fillStyle = isDark ? '#94a3b8' : '#6b7280';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`Azimuth (${alignment.azimuth_start}° — ${(alignment.azimuth_start + alignment.fov).toFixed(0)}°)`,
                 padLeft + plotW / 2, displayHeight - 3);
}

// Map 
function initMap(matches) {
    const mapDiv = document.getElementById('map');
    if (!mapDiv || typeof L === 'undefined') return;

    map = L.map('map');

    // OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    const bounds = [];
    matches.forEach((match, idx) => {
        const lat = parseFloat(match.lat);
        const lon = parseFloat(match.lon);
        if (isNaN(lat) || isNaN(lon)) return;

        const confidence = parseFloat(match.confidence);
        const color = RESULT_COLORS[idx % RESULT_COLORS.length];
        const icon = RESULT_EMOJIS[idx % RESULT_EMOJIS.length];

        const marker = L.circleMarker([lat, lon], {
            radius: idx === 0 ? 12 : 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85,
        }).addTo(map);

        marker.bindPopup(`
            <strong>${icon} #${idx + 1} ${match.location || ''}</strong><br>
            Confidence: ${confidence}%<br>
            ${match.coordinates}<br>
            Elevation: ${match.elevation}
        `);

        if (idx === 0) marker.openPopup();
        bounds.push([lat, lon]);
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
    }
}

// Match cards 
function displayMatches(matches, alignments) {
    const header = document.createElement('div');
    header.innerHTML = `
        <h3 style="color:var(--text-primary); margin-bottom:1rem;">Possible Locations</h3>
        <div class="rank-legend">
            ${RESULT_EMOJIS.map((icon, idx) => `<span class="rank-legend-item"><span class="rank-legend-dot" style="background:${RESULT_COLORS[idx]};"></span>${icon} Result ${idx + 1}</span>`).join('')}
        </div>
    `;
    resultsCard.appendChild(header);

    matches.forEach((match, index) => {
        const alignment = alignments[index] || null;
        resultsCard.appendChild(createResultItem(match, index, alignment));
    });
}

function createResultItem(match, index, alignment) {
    const item = document.createElement('div');
    item.className = 'result-item';
    item.style.cursor = 'pointer';

    const confidence = parseFloat(match.confidence);
    const confidenceClass = getConfidenceClass(confidence);
    const confidenceLabel = getConfidenceLabel(confidence);
    const rankColor = RESULT_COLORS[index % RESULT_COLORS.length];
    const rankEmoji = RESULT_EMOJIS[index % RESULT_EMOJIS.length];

    // Metric details
    const ncc = match.ncc !== undefined ? match.ncc : '—';
    const chamfer = match.chamfer !== undefined ? match.chamfer : '—';
    const rmse = match.rmse !== undefined ? match.rmse : '—';
    const azimuth = match.azimuth !== undefined ? `${match.azimuth}°` : '—';

    item.innerHTML = `
        <div class="result-header">
            <div class="result-location">
                <span class="result-rank-chip" style="background:${rankColor};">${rankEmoji} #${index + 1}</span>
                ${match.location || 'Unknown'}
            </div>
            <div class="confidence-badge ${confidenceClass}">
                ${confidenceLabel} (${confidence.toFixed(1)}%)
            </div>
        </div>
        <div class="result-details">
            ${match.coordinates ? `<p><strong>Coordinates:</strong> ${match.coordinates}</p>` : ''}
            ${match.elevation ? `<p><strong>Elevation:</strong> ${match.elevation}</p>` : ''}
            ${match.region ? `<p><strong>Region:</strong> ${match.region}</p>` : ''}
            <div class="metrics-row">
                <span class="metric" title="Normalised Cross-Correlation">NCC: ${ncc}</span>
                <span class="metric" title="Chamfer Distance (lower = better)">Chamfer: ${chamfer}</span>
                <span class="metric" title="Root Mean Square Error (lower = better)">RMSE: ${rmse}</span>
                <span class="metric" title="Estimated compass bearing">Bearing: ${azimuth}</span>
            </div>
        </div>
    `;

    // Collapsible alignment chart
    if (alignment) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'btn btn-alignment-toggle';
        toggleBtn.textContent = '▸ Show Skyline Alignment';
        toggleBtn.type = 'button';

        const chartContainer = document.createElement('div');
        chartContainer.className = 'alignment-inline-container';
        chartContainer.style.display = 'none';

        const canvas = document.createElement('canvas');
        canvas.className = 'alignment-canvas';
        chartContainer.appendChild(canvas);

        const legend = document.createElement('div');
        legend.className = 'alignment-legend';
        legend.innerHTML = `
            <span class="legend-item"><span class="legend-swatch" style="background:#4682B4;"></span> Reference (database)</span>
            <span class="legend-item"><span class="legend-swatch" style="background:#FF4500;"></span> Query (from image)</span>
        `;
        chartContainer.appendChild(legend);

        let drawn = false;
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = chartContainer.style.display !== 'none';
            chartContainer.style.display = isOpen ? 'none' : 'block';
            toggleBtn.textContent = isOpen ? '▸ Show Skyline Alignment' : '▾ Hide Skyline Alignment';
            if (!drawn) {
                drawn = true;
                requestAnimationFrame(() => drawSingleAlignment(canvas, alignment));
            }
        });

        item.appendChild(toggleBtn);
        item.appendChild(chartContainer);
    }

    // Click to pan map (only on header area, not on the toggle button)
    item.addEventListener('click', (e) => {
        if (e.target.closest('.btn-alignment-toggle') || e.target.closest('.alignment-inline-container')) return;
        const lat = parseFloat(match.lat);
        const lon = parseFloat(match.lon);
        if (map && !isNaN(lat) && !isNaN(lon)) {
            map.setView([lat, lon], 13);
        }
    });

    return item;
}

function displayNoResults() {
    resultsCard.innerHTML = `
        <div class="no-results">
            <h3>No Matches Found</h3>
            <p>We couldn't find a matching location in our database.</p>
            <p>This could mean:</p>
            <ul style="list-style:none; padding:0; margin-top:1rem;">
                <li>• The skyline is not in our current database (Pyrenees only)</li>
                <li>• The image quality may be too low</li>
                <li>• The skyline is obscured by clouds or fog</li>
                <li>• The image doesn't contain a clear mountain horizon</li>
            </ul>
            <p style="margin-top:1.5rem;">Try uploading a different image with a clearer skyline.</p>
        </div>
    `;
}

function getConfidenceClass(c) {
    if (c >= 80) return 'confidence-high';
    if (c >= 50) return 'confidence-medium';
    return 'confidence-low';
}

function getConfidenceLabel(c) {
    if (c >= 80) return 'High Confidence';
    if (c >= 50) return 'Medium Confidence';
    return 'Low Confidence';
}

function formatCoordinates(lat, lon) {
    const latDir = lat >= 0 ? 'N' : 'S';
    const lonDir = lon >= 0 ? 'E' : 'W';
    return `${Math.abs(lat).toFixed(4)}°${latDir}, ${Math.abs(lon).toFixed(4)}°${lonDir}`;
}
