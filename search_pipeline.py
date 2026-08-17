//  Dark Mode Toggle 
(function () {
    const STORAGE_KEY = 'summitsight-theme';

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const btn = document.getElementById('themeToggle');
        if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    // Apply saved preference immediately (before paint)
    const saved = localStorage.getItem(STORAGE_KEY) || 'light';
    applyTheme(saved);

    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('themeToggle');
        if (!btn) return;

        // Re-apply in case DOM wasn't ready above
        applyTheme(localStorage.getItem(STORAGE_KEY) || 'light');

        btn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem(STORAGE_KEY, next);
            applyTheme(next);
        });
    });
})();
