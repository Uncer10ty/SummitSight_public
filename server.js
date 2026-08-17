/**
 * SummitSight Node.js API Gateway
 *
 * This code serves as the primary middleware connecting client applications to the core Python processing backend. 
 * It handles HTTP routing, manages multipart image uploads via Multer (10MB limit and format validation), and serving static assets. 
 * Itt also implements an asynchronous proxy, sending the heavy tasks (skyline extraction and search) to Python API
 * and exposes polling endpoints to manage progress responses.
 */

const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const http = require('http');
const FormData = require('form-data');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Python Flask API address
const PYTHON_API = {
    host: 'localhost',
    port: parseInt(process.env.PYTHON_API_PORT || '5000'),
};

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// Ensure uploads directory exists (for storing uploads and generated overlays)
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadsDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, 'skyline-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB limit
    },
    fileFilter: function (req, file, cb) {
        const allowedTypes = /jpeg|jpg|png|gif|bmp|webp/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Only image files are allowed!'));
        }
    }
});

// proxy a multipart file to the Python API
function proxyFileToPython(endpoint, filePath, originalName) {
    return new Promise((resolve, reject) => {
        const form = new FormData();
        form.append('image', fs.createReadStream(filePath), originalName);

        const options = {
            host: PYTHON_API.host,
            port: PYTHON_API.port,
            path: endpoint,
            method: 'POST',
            headers: form.getHeaders(),
            timeout: 120000,  // 2 min timeout for model inference
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(body) });
                } catch (e) {
                    reject(new Error('Invalid JSON from Python API'));
                }
            });
        });

        req.on('error', (err) => reject(err));
        req.on('timeout', () => { req.destroy(); reject(new Error('Python API timeout')); });
        form.pipe(req);
    });
}

// POST JSON to the Python API 
function postJsonToPython(endpoint, payload) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify(payload);
        const options = {
            host: PYTHON_API.host,
            port: PYTHON_API.port,
            path: endpoint,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
            },
            timeout: 300000,  // 5 min timeout for full search
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data) });
                } catch (e) {
                    reject(new Error('Invalid JSON from Python API'));
                }
            });
        });

        req.on('error', (err) => reject(err));
        req.on('timeout', () => { req.destroy(); reject(new Error('Python API timeout')); });
        req.write(body);
        req.end();
    });
}

// 
// ROUTES
// 

// Health check 
app.get('/api/health', async (req, res) => {
    try {
        const pyHealth = await getJsonFromPython('/health').catch(() => null);
        res.json({
            status: 'OK',
            message: 'SummitSight API is running',
            pythonApi: pyHealth ? pyHealth.data : { status: 'UNAVAILABLE' },
            timestamp: new Date().toISOString(),
        });
    } catch {
        res.json({
            status: 'OK',
            message: 'SummitSight API is running (Python API not connected)',
            timestamp: new Date().toISOString(),
        });
    }
});

// Pipeline step 1: extract skyline (async,returns session_id, then poll progress)
app.post('/api/extract', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image file uploaded' });
        }

        console.log(`[Extract] Processing: ${req.file.filename}`);

        const result = await proxyFileToPython('/extract', req.file.path, req.file.originalname);

        if (result.status !== 200) {
            fs.unlink(req.file.path, () => {});
            return res.status(result.status).json(result.data);
        }

        // Python returns { status: "started", session_id }, we can poll later
        // Store uploaded file path so can reference it when extraction completes
        const sessionId = result.data.session_id;
        if (!app.locals.extractSessions) app.locals.extractSessions = {};
        app.locals.extractSessions[sessionId] = {
            uploadedFilename: req.file.filename,
            startTime: Date.now(),
        };

        res.json({
            status: 'started',
            session_id: sessionId,
        });

    } catch (error) {
        console.error('[Extract] Error:', error.message);
        res.status(500).json({
            error: 'Skyline extraction failed',
            message: error.message,
        });
    }
});

// Poll extracting progress (still step 1)
app.get('/api/extract-progress/:sessionId', async (req, res) => {
    try {
        const sessionId = req.params.sessionId;
        const result = await getJsonFromPython(`/extract-progress/${sessionId}`);

        // If done, save overlay to disk and add URLs to response
        if (result.data.status === 'done' && result.data.overlay_image) {
            const overlayFilename = `overlay-${sessionId}.jpg`;
            const overlayPath = path.join(uploadsDir, overlayFilename);
            fs.writeFileSync(overlayPath, Buffer.from(result.data.overlay_image, 'base64'));

            // Look up the uploaded file info
            const sessInfo = (app.locals.extractSessions || {})[sessionId] || {};
            const uploadedFilename = sessInfo.uploadedFilename || '';
            const startTime = sessInfo.startTime || Date.now();

            // Clean up the mapping
            if (app.locals.extractSessions) delete app.locals.extractSessions[sessionId];

            // use URLs instead of base64 
            delete result.data.overlay_image;
            result.data.overlay_url = `/uploads/${overlayFilename}`;
            result.data.uploaded_url = uploadedFilename ? `/uploads/${uploadedFilename}` : '';
            result.data.processingTime = Date.now() - startTime;
        }

        res.status(result.status).json(result.data);
    } catch (error) {
        console.error('[Extract Progress] Error:', error.message);
        res.status(500).json({ error: 'Extract progress check failed', message: error.message });
    }
});

// Step 2: Start search (returns immediately, search runs in background)
app.post('/api/search', async (req, res) => {
    try {
        const { session_id, fov } = req.body;

        if (!session_id) {
            return res.status(400).json({ error: 'Missing session_id' });
        }

        console.log(`[Search] Launching background search for session ${session_id}`);

        const result = await postJsonToPython('/search', {
            session_id,
            fov: fov || 65,
        });

        if (result.status !== 200) {
            return res.status(result.status).json(result.data);
        }

        res.json(result.data);

    } catch (error) {
        console.error('[Search] Error:', error.message);
        res.status(500).json({
            error: 'Search failed',
            message: error.message,
        });
    }
});

// Step 2b: Poll search progress 
function getJsonFromPython(endpoint) {
    return new Promise((resolve, reject) => {
        const options = {
            host: PYTHON_API.host,
            port: PYTHON_API.port,
            path: endpoint,
            method: 'GET',
            timeout: 30000,
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data) });
                } catch (e) {
                    reject(new Error('Invalid JSON from Python API'));
                }
            });
        });

        req.on('error', (err) => reject(err));
        req.on('timeout', () => { req.destroy(); reject(new Error('Python API timeout')); });
        req.end();
    });
}

app.get('/api/search-progress/:sessionId', async (req, res) => {
    try {
        const result = await getJsonFromPython(`/search-progress/${req.params.sessionId}`);
        res.status(result.status).json(result.data);
    } catch (error) {
        console.error('[Progress] Error:', error.message);
        res.status(500).json({ error: 'Progress check failed', message: error.message });
    }
});

// Get database statistics
app.get('/api/stats', async (req, res) => {
    try {
        const result = await getJsonFromPython('/stats');
        res.status(result.status).json(result.data);
    } catch (error) {
        console.error('[Stats] Error:', error.message);
        res.status(502).json({
            error: 'Stats unavailable',
            message: error.message,
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ 
                error: 'File size too large. Maximum size is 10MB.' 
            });
        }
    }
    
    res.status(500).json({ 
        error: 'Internal server error',
        message: error.message 
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        error: 'Not found',
        path: req.path 
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════╗
║       SummitSight Server Running       ║
╠════════════════════════════════════════╣
║  Port: ${PORT}                            ║
║  URL: http://localhost:${PORT}            ║
║  Environment: ${process.env.NODE_ENV || 'development'}              ║
╚════════════════════════════════════════╝
    `);
    console.log('API Endpoints:');
    console.log('  POST /api/extract  -  Extract skyline from image');
    console.log('  POST /api/search   -  Search database for matches');
    console.log('  GET  /api/health   -  Health check');
    console.log('  GET  /api/stats    -  Database statistics');
    console.log('  Python API:  http://localhost:' + PYTHON_API.port);
    console.log('');
});

module.exports = app;
