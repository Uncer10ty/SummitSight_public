// SummitSight API Configuration 
// Set SUMMITSIGHT_API_URL before loading this script, or it defaults to
// the Python API running locally (dev) or on DigitalOcean (production).

const API_BASE_URL = (() => {
    // Allow an explicit override via a global set before this script loads
    if (typeof SUMMITSIGHT_API_URL !== 'undefined') return SUMMITSIGHT_API_URL;

    // Production: DigitalOcean Droplet with HTTPS via Let's Encrypt.
    const PRODUCTION_API = 'https://api.summits.studio';

    // Local development: Python Flask API on port 5000
    const LOCAL_API = 'http://localhost:5000';

    const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
    return isLocal ? LOCAL_API : PRODUCTION_API;
})();
