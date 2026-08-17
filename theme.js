<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SummitSight - Skyline Geolocation Tool</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏔️</text></svg>">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <h1>🏔️ SummitSight</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html" class="active">Upload</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="gallery.html">Gallery</a></li>
                <li><button id="themeToggle" class="theme-toggle" title="Toggle dark mode">🌙</button></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <section class="hero">
            <h2>Discover Your Location from Skylines</h2>
            <p class="subtitle">Upload an image of a mountain skyline and let our advanced contour analysis identify your location</p>
        </section>

        <section class="upload-section">
            <div class="upload-card">
                <!-- Step 1: Upload -->
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📷</div>
                    <h3>Upload Your Skyline Image</h3>
                    <p>Drag and drop an image here or click to browse</p>
                    <input type="file" id="fileInput" accept="image/*" hidden>
                    <button class="btn btn-primary" id="browseBtn">Browse Files</button>
                </div>

                <!-- Step 2: Preview original image -->
                <div class="preview-area" id="previewArea" style="display: none;">
                    <div class="preview-header">
                        <h3>Image Preview</h3>
                        <button class="btn btn-secondary" id="removeBtn">Remove</button>
                    </div>
                    <img id="previewImage" src="" alt="Preview">
                    <div class="image-info" id="imageInfo"></div>
                    <button class="btn btn-primary btn-large" id="extractBtn">Extract Skyline</button>
                </div>

                <!-- Step 3: Approve extracted skyline -->
                <div class="approval-area" id="approvalArea" style="display: none;">
                    <div class="preview-header">
                        <h3>Extracted Skyline</h3>
                        <span class="method-badge" id="methodBadge"></span>
                    </div>
                    <p id="methodExplanation" class="method-explanation"></p>
                    <p class="approval-hint">Check that the extracted skyline boundary accurately traces the mountain horizon.</p>
                    <div class="comparison-container">
                        <div class="comparison-item">
                            <h4>Skyline Overlay</h4>
                            <img id="overlayImage" src="" alt="Skyline overlay">
                        </div>
                    </div>
                    <div class="fov-control">
                        <label for="fovSlider"><strong>Field of View:</strong> <span id="fovValue">60</span>°</label>
                        <input type="range" id="fovSlider" min="60" max="360" value="60" step="1">
                        <div class="fov-hints">
                            <span>60° (default - phone camera)</span>
                            <span>120° (wide)</span>
                            <span>360° (photo sphere)</span>
                        </div>
                    </div>
                    <div class="approval-actions">
                        <button class="btn btn-primary btn-large" id="approveBtn">✓ Approve &amp; Search</button>
                        <button class="btn btn-secondary" id="rejectBtn">✗ Try Another Image</button>
                    </div>
                </div>
            </div>

            <!-- Loading overlay with progress stages -->
            <div class="loading-overlay" id="loadingOverlay" style="display: none;">
                <div class="spinner"></div>
                <p id="loadingText">Extracting skyline contours...</p>
                <div class="loading-stage" id="loadingStage"></div>
                <div class="progress-bar-container" id="progressBarContainer" style="display: none;">
                    <div class="progress-bar-fill" id="progressBarFill"></div>
                    <span class="progress-text" id="progressText"></span>
                </div>
            </div>
        </section>

        <section class="features">
            <h3>How It Works</h3>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📸</div>
                    <h4>1. Upload Image</h4>
                    <p>Upload a photo containing a mountain skyline or horizon</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h4>2. Skyline Extraction</h4>
                    <p>SegFormer AI detects and extracts the mountain skyline from your photo</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">✓</div>
                    <h4>3. Approve Skyline</h4>
                    <p>Review the extracted skyline and confirm it looks correct</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🗺️</div>
                    <h4>4. Location Search</h4>
                    <p>Search 1.35 million viewpoints to find the best geographical match</p>
                </div>
            </div>
        </section>
    </main>

    <footer class="footer">
        <p>&copy; 2026 SummitSight. All rights reserved.</p>
    </footer>

    <script src="js/theme.js"></script>
    <script src="js/config.js"></script>
    <script src="js/upload.js"></script>
    <script>
        window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    </script>
    <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
