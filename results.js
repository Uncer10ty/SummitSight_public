<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example Gallery - SummitSight</title>
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
                <li><a href="index.html">Upload</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="gallery.html" class="active">Gallery</a></li>
                <li><button id="themeToggle" class="theme-toggle" title="Toggle dark mode">🌙</button></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <section class="about-hero gallery-hero">
            <h2>Interactive Example Gallery</h2>
            <p class="subtitle">Click through a sped-up replay of the full pipeline for each example.</p>
        </section>

        <section class="gallery-grid" id="galleryGrid"></section>
    </main>

    <footer class="footer">
        <p>&copy; 2026 SummitSight. All rights reserved.</p>
    </footer>

    <script src="js/theme.js"></script>
    <script src="js/gallery.js"></script>
</body>
</html>