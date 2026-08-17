<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results - SummitSight</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏔️</text></svg>">
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin="" />
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <h1>🏔️ SummitSight</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Upload</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="gallery.html">Gallery</a></li>
                <li><button id="themeToggle" class="theme-toggle" title="Toggle dark mode">🌙</button></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <section class="results-hero">
            <h2>Analysis Results</h2>
            <p class="subtitle">Skyline matched against 1,347,655 viewpoints in the Pyrenees</p>
        </section>

        <section class="results-section">
            <!-- Performance summary -->
            <div class="performance-summary" id="performanceSummary" style="display:none;">
                <h3>Performance Summary</h3>
                <div class="perf-row">
                    <div class="perf-item">
                        <span class="perf-label">Segmentation</span>
                        <span class="perf-value" id="perfSegmentation">-</span>
                    </div>
                    <div class="perf-item">
                        <span class="perf-label">Search</span>
                        <span class="perf-value" id="perfSearch">-</span>
                    </div>
                    <div class="perf-item">
                        <span class="perf-label">Top Confidence</span>
                        <span class="perf-value" id="perfConfidence">-</span>
                    </div>
                </div>
            </div>

            <!-- Extracted skyline -->
            <div class="image-comparison-card">
                <h3>Extracted Skyline</h3>
                <img id="overlayImageResult" src="" alt="Skyline overlay" style="max-width:100%; max-height:400px; border-radius:0.5rem; display:block; margin:0 auto;">
            </div>

            <!-- Map -->
            <div class="map-card">
                <h3>Match Locations</h3>
                <div id="map" style="height: 400px; border-radius: 0.5rem;"></div>
            </div>

            <!-- Match results -->
            <div class="results-card" id="resultsCard">
                <!-- Dynamically populated -->
            </div>

            <div class="actions">
                <a href="index.html" class="btn btn-primary">Analyse Another Image</a>
            </div>
        </section>
    </main>

    <footer class="footer">
        <p>&copy; 2026 SummitSight. All rights reserved.</p>
    </footer>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>
    <script src="js/theme.js"></script>
    <script src="js/results.js"></script>
    <script>
        window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    </script>
    <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
