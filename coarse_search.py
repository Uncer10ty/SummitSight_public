//  Admin Health Dashboard 

function formatUptime(seconds) {
    if (!seconds || seconds < 0) return '—';
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

function setTextById(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function getNodeRuntimeStatus() {
    const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
    const isNodeDevPort = window.location.port === '3000';

    if (isLocalHost && isNodeDevPort) {
        return '✓ Local Node UI (port 3000)';
    }
    if (isLocalHost) {
        return '- Local browser run (no Node runtime detected)';
    }
    return '- Static hosting (no Node runtime)';
}

async function fetchHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        const data = await res.json();

        // Direct Python API response (no Node.js proxy)
        const pyOk = data.status === 'OK';

        // Quick cards
        setTextById('apiStatus', pyOk ? '✓ Online' : '✗ Offline');
        setTextById('modelsStatus', data.models_loaded ? '✓ Loaded' : '✗ Not loaded');
        setTextById('memoryRss', data.memory_rss_mb ? `${data.memory_rss_mb} MB` : '—');
        setTextById('dbSize', data.database_size ? data.database_size.toLocaleString() : '—');
        setTextById('uptime', formatUptime(data.uptime_seconds));
        const activeJobs = (data.extract_queue || 0) + (data.search_queue || 0);
        setTextById('activeJobs', String(activeJobs));

        // Detailed table
        setTextById('nodeStatus', getNodeRuntimeStatus());
        setTextById('pythonStatus', pyOk ? '✓ Running' : '✗ Unavailable');
        setTextById('modelsDetail', data.models_loaded ? '✓ SegFormer' : '✗ Not loaded');
        setTextById('dataDetail', data.data_loaded ? '✓ Loaded' : '✗ Not loaded');
        setTextById('memRssDetail', data.memory_rss_mb ? `${data.memory_rss_mb} MB` : '—');
        setTextById('memVmsDetail', data.memory_vms_mb ? `${data.memory_vms_mb} MB` : '—');
        setTextById('cpuDetail', data.cpu_percent !== undefined ? `${data.cpu_percent}%` : '—');
        setTextById('threadsDetail', data.threads !== undefined ? String(data.threads) : '—');
        setTextById('pidDetail', data.pid !== undefined ? String(data.pid) : '—');
        setTextById('dbSizeDetail', data.database_size ? `${data.database_size.toLocaleString()} skylines` : '—');
        setTextById('sessionsDetail', data.active_sessions !== undefined ? String(data.active_sessions) : '—');
        setTextById('extractQueue', `${data.extract_queue || 0} active / ${data.total_extract_jobs || 0} total`);
        setTextById('searchQueue', `${data.search_queue || 0} active / ${data.total_search_jobs || 0} total`);
        setTextById('uptimeDetail', formatUptime(data.uptime_seconds));
        setTextById('lastRefresh', new Date().toLocaleTimeString());

        // Update icon based on status
        const apiCard = document.querySelector('#statusCards .admin-stat-card:first-child .stat-icon');
        if (apiCard) apiCard.textContent = data.status === 'OK' && pyOk ? '🟢' : '🔴';

    } catch (err) {
        setTextById('apiStatus', '✗ Error');
        setTextById('nodeStatus', getNodeRuntimeStatus());
        setTextById('pythonStatus', '✗ Connection failed');
        setTextById('lastRefresh', new Date().toLocaleTimeString() + ' (error)');
        console.error('Health fetch failed:', err);
    }
}

// Initial fetch + auto-refresh
fetchHealth();
setInterval(fetchHealth, 5000);
