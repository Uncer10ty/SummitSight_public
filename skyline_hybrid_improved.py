// API_BASE_URL is provided by config.js (loaded before this script)

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const previewArea = document.getElementById('previewArea');
const previewImage = document.getElementById('previewImage');
const imageInfo = document.getElementById('imageInfo');
const extractBtn = document.getElementById('extractBtn');
const removeBtn = document.getElementById('removeBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const loadingStage = document.getElementById('loadingStage');
const progressBarContainer = document.getElementById('progressBarContainer');
const progressBarFill = document.getElementById('progressBarFill');
const progressText = document.getElementById('progressText');

// Approval step elements
const approvalArea = document.getElementById('approvalArea');
const overlayImage = document.getElementById('overlayImage');
const methodBadge = document.getElementById('methodBadge');
const methodExplanation = document.getElementById('methodExplanation');
const approveBtn = document.getElementById('approveBtn');
const rejectBtn = document.getElementById('rejectBtn');
const fovSlider = document.getElementById('fovSlider');
const fovValue = document.getElementById('fovValue');

let selectedFile = null;
let currentSessionId = null;
let uploadedImageUrl = null;
let extractionTime = null;
let extractionMethod = null;

const EXAMPLE_INPUT_SOURCES = {
    'midi-d-ossau': ["examples/midi-d-ossau/input.jpg", "examples/midi_d'osseau.jpg"],
    aneto: ['examples/aneto/input.jpg'],
    canigou: ['examples/canigou/input.jpg'],
};

// Event Listeners 
browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});
fileInput.addEventListener('change', handleFileSelect);
removeBtn.addEventListener('click', resetUpload);
extractBtn.addEventListener('click', extractSkyline);
approveBtn.addEventListener('click', startSearch);
rejectBtn.addEventListener('click', resetUpload);
fovSlider.addEventListener('input', () => {
    fovValue.textContent = fovSlider.value;
});

initialiseFromQuery();

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target === uploadArea || e.target.closest('.upload-area')) {
        fileInput.click();
    }
});

// File handling 
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) handleFile(file);
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size must be less than 10MB');
        return;
    }
    selectedFile = file;
    displayPreview(file);
}

function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewArea.style.display = 'block';
        approvalArea.style.display = 'none';

        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        imageInfo.innerHTML = `
            <strong>File:</strong> ${file.name}<br>
            <strong>Size:</strong> ${sizeInMB} MB<br>
            <strong>Type:</strong> ${file.type}
        `;
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    selectedFile = null;
    currentSessionId = null;
    uploadedImageUrl = null;
    extractionTime = null;
    extractionMethod = null;
    fileInput.value = '';
    previewImage.src = '';
    uploadArea.style.display = 'block';
    previewArea.style.display = 'none';
    approvalArea.style.display = 'none';
    imageInfo.innerHTML = '';
}

//  Step 1: Extract skyline (async with polling) 
async function extractSkyline() {
    if (!selectedFile) {
        alert('Please select an image first');
        return;
    }

    showLoading('Extracting skyline contours...', 'Uploading image...');
    hideProgressBar();
    extractBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);

        const response = await fetch(`${API_BASE_URL}/extract`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.error || `Server error (${response.status})`);
        }

        const launchData = await response.json();

        if (launchData.status !== 'started' || !launchData.session_id) {
            throw new Error('Unexpected response from server');
        }

        // Poll for extraction progress
        const result = await pollExtractProgress(launchData.session_id);
        hideLoading();

        // Show the approval step
        currentSessionId = result.session_id;
        // The Python API returns overlay as base64; convert to data URL
        if (result.overlay_image) {
            overlayImage.src = `data:image/jpeg;base64,${result.overlay_image}`;
        } else if (result.overlay_url) {
            overlayImage.src = result.overlay_url;
        }
        // Use the local file preview as the uploaded image reference
        uploadedImageUrl = previewImage.src;
        extractionTime = result.processingTime || result.processing_time_ms;
        extractionMethod = 'SegFormer';

        // Method badge
        methodBadge.textContent = 'SegFormer';
        methodBadge.className = 'method-badge badge-blue';

        // Method explanation
        if (methodExplanation) {
            methodExplanation.innerHTML =
                '<strong>SegFormer</strong> semantic segmentation isolated the skyline region and extracted the sky-terrain boundary used for matching.';
            methodExplanation.className = 'method-explanation explanation-good';
        }

        // Store for results page
        sessionStorage.setItem('extractionTime', String(extractionTime));
        sessionStorage.setItem('extractionMethod', extractionMethod);

        previewArea.style.display = 'none';
        approvalArea.style.display = 'block';

    } catch (error) {
        console.error('Extraction error:', error);
        hideLoading();
        alert(`Skyline extraction failed: ${error.message}`);
        extractBtn.disabled = false;
    }
}

function pollExtractProgress(sessionId) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/extract-progress/${sessionId}`);
                const data = await res.json();

                // Update progress text with the latest extract message
                if (data.messages && data.messages.length > 0) {
                    const last = data.messages[data.messages.length - 1];
                    // Strip the [extract] prefix for display
                    loadingStage.textContent = last.replace(/^\[extract\]\s*/, '');
                }

                if (data.status === 'done') {
                    clearInterval(interval);
                    resolve(data);
                } else if (data.status === 'error') {
                    clearInterval(interval);
                    reject(new Error(data.message || 'Extraction failed on server'));
                }
            } catch (err) {
                clearInterval(interval);
                reject(err);
            }
        }, 800); // poll every 0.8s (extraction is faster than search)
    });
}

//  Step 2: Search (after user approves) 
async function startSearch() {
    if (!currentSessionId) {
        alert('No extraction session — please extract a skyline first.');
        return;
    }

    showLoading('Searching 1.35 million viewpoints...', 'Initialising search pipeline...');
    hideProgressBar();
    approveBtn.disabled = true;

    try {
        // 1. Launch the search (returns immediately)
        const launchRes = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                fov: parseInt(fovSlider.value, 10),
            }),
        });

        if (!launchRes.ok) {
            const err = await launchRes.json().catch(() => ({}));
            throw new Error(err.error || `Server error (${launchRes.status})`);
        }

        // 2. Poll for progress until done
        const pollResult = await pollSearchProgress(currentSessionId);

        hideLoading();

        // Store results + overlay URL for the results page
        sessionStorage.setItem('analysisResults', JSON.stringify(pollResult));
        sessionStorage.setItem('uploadedImage', uploadedImageUrl);
        sessionStorage.setItem('overlayImage', overlayImage.src);

        window.location.href = 'results.html';

    } catch (error) {
        console.error('Search error:', error);
        hideLoading();
        alert(`Search failed: ${error.message}`);
        approveBtn.disabled = false;
    }
}

function pollSearchProgress(sessionId) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/search-progress/${sessionId}`);
                const data = await res.json();

                // Update progress text with the latest pipeline message
                if (data.messages && data.messages.length > 0) {
                    const last = data.messages[data.messages.length - 1];
                    loadingStage.textContent = last;

                    // Parse coarse chunk progress for the progress bar
                    const chunkMatch = last.match(/Coarse:\s*chunk\s+(\d+)\/(\d+)/i);
                    if (chunkMatch) {
                        const current = parseInt(chunkMatch[1], 10);
                        const total = parseInt(chunkMatch[2], 10);
                        showProgressBar(current, total);
                    } else if (!last.includes('Coarse')) {
                        // Non-chunk message -> hide the bar (moved past coarse stage)
                        hideProgressBar();
                    }
                }

                if (data.status === 'done') {
                    clearInterval(interval);
                    resolve(data);
                } else if (data.status === 'error') {
                    clearInterval(interval);
                    reject(new Error(data.message || 'Search failed on server'));
                }
                // else status === 'running' -> keep polling

            } catch (err) {
                clearInterval(interval);
                reject(err);
            }
        }, 1500); // poll every 1.5 s
    });
}

//  Loading helpers 
function showLoading(text, stage) {
    loadingText.textContent = text;
    loadingStage.textContent = stage || '';
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
    hideProgressBar();
    extractBtn.disabled = false;
    approveBtn.disabled = false;
}

function showProgressBar(current, total) {
    if (!progressBarContainer) return;
    progressBarContainer.style.display = 'block';
    const pct = Math.min(100, Math.round((current / total) * 100));
    progressBarFill.style.width = pct + '%';
    progressText.textContent = `Chunk ${current}/${total}`;
}

function hideProgressBar() {
    if (!progressBarContainer) return;
    progressBarContainer.style.display = 'none';
    progressBarFill.style.width = '0%';
    progressText.textContent = '';
}

async function initialiseFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const requestedFov = parseInt(params.get('fov') || '', 10);
    const requestedExample = params.get('example');

    if (!Number.isNaN(requestedFov)) {
        const clamped = Math.max(parseInt(fovSlider.min, 10), Math.min(parseInt(fovSlider.max, 10), requestedFov));
        fovSlider.value = String(clamped);
        fovValue.textContent = String(clamped);
    }

    if (!requestedExample) return;

    const loaded = await loadExampleImage(requestedExample);
    if (!loaded) {
        showManualExampleMessage(requestedExample);
    }
}

async function loadExampleImage(exampleSlug) {
    const candidates = EXAMPLE_INPUT_SOURCES[exampleSlug] || [];
    if (candidates.length === 0) return false;

    for (const path of candidates) {
        try {
            const response = await fetch(path);
            if (!response.ok) continue;

            const blob = await response.blob();
            if (!blob.type.startsWith('image/')) continue;

            const extension = blob.type.split('/')[1] || 'jpg';
            const exampleFile = new File([blob], `${exampleSlug}.${extension}`, { type: blob.type });
            handleFile(exampleFile);

            const helperLine = document.createElement('div');
            helperLine.style.marginTop = '0.5rem';
            helperLine.style.fontSize = '0.85rem';
            helperLine.style.color = 'var(--secondary-color)';
            helperLine.textContent = 'Example loaded automatically. FOV set to 100deg.';
            imageInfo.appendChild(helperLine);

            return true;
        } catch (err) {
            console.warn('Example image load failed:', path, err);
        }
    }

    return false;
}

function showManualExampleMessage(exampleSlug) {
    const text = `Could not auto-load the ${exampleSlug} image. Please add/select it manually, then set FOV to 100deg.`;
    alert(text);
}