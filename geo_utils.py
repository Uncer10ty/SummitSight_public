const EXAMPLES = [
    {
        slug: 'midi-d-ossau',
        title: "Pic du Midi d'Ossau",
        subtitle: 'Iconic pyramidal peak - 2,884 m, Bearn, France',
        legacy: {
            overlay: "examples/midi_d'osseau_overlay.jpg",
            satellite: "examples/midi_d'osseau_satellite.png",
        },
        locations: [
            '42.8460N, 0.4358W - Rank #1',
            '42.8441N, 0.4389W - Rank #2',
            '42.8412N, 0.4456W - Rank #3',
        ],
    },
    {
        slug: 'aneto',
        title: 'Aneto',
        subtitle: 'Highest peak in the Pyrenees - 3,404 m, Aragon, Spain',
        locations: [
            '42.6312N, 0.6572E - Rank #1',
            '42.6294N, 0.6518E - Rank #2',
            '42.6355N, 0.6621E - Rank #3',
        ],
    },
    {
        slug: 'canigou',
        title: 'Pic du Canigou',
        subtitle: 'Prominent eastern Pyrenees peak - 2,784 m, Catalonia, France',
        locations: [
            '42.5192N, 2.4564E - Rank #1',
            '42.5165N, 2.4517E - Rank #2',
            '42.5241N, 2.4628E - Rank #3',
        ],
    },
];

const STAGE_LABELS = [
    'Input photo',
    'SegFormer extraction',
    'Found locations',
    'Found coordinate views',
];

const FOCUS_QUERY_PARAM = new URLSearchParams(window.location.search).get('example');

window.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;

    const orderedExamples = reorderExamplesByQuery(EXAMPLES, FOCUS_QUERY_PARAM);
    orderedExamples.forEach((example, index) => {
        grid.appendChild(buildExampleCard(example, index));
    });
});

function reorderExamplesByQuery(examples, focusedSlug) {
    if (!focusedSlug) return examples;
    const focused = examples.find((x) => x.slug === focusedSlug);
    if (!focused) return examples;
    const others = examples.filter((x) => x.slug !== focusedSlug);
    return [focused].concat(others);
}

function buildExampleCard(example, index) {
    const card = document.createElement('article');
    card.className = 'gallery-card';

    const steps = buildSteps(example);

    card.innerHTML = `
        <div class="gallery-card-head">
            <h3>${example.title}</h3>
            <p>${example.subtitle}</p>
        </div>
        <div class="gallery-step-track" data-step-track="${index}">
            ${STAGE_LABELS.map((label, i) => `<button class="gallery-step-pill ${i === 0 ? 'active' : ''}" type="button" data-step-index="${i}">${i + 1}. ${label}</button>`).join('')}
        </div>
        <div class="gallery-stage-panel" data-stage-panel="${index}"></div>
        <div class="gallery-actions">
            <button type="button" class="btn btn-primary gallery-next">Next Step</button>
            <button type="button" class="btn btn-secondary gallery-try">Try Example in Upload (FOV 100)</button>
        </div>
    `;

    let activeIndex = 0;

    const panel = card.querySelector('[data-stage-panel]');
    const stepTrack = card.querySelector('[data-step-track]');
    const nextBtn = card.querySelector('.gallery-next');
    const tryBtn = card.querySelector('.gallery-try');

    function setStage(nextIndex) {
        activeIndex = Math.max(0, Math.min(steps.length - 1, nextIndex));
        panel.innerHTML = steps[activeIndex];

        stepTrack.querySelectorAll('.gallery-step-pill').forEach((pill, idx) => {
            if (idx === activeIndex) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });

        wireImageFallbacks(panel);
    }

    nextBtn.addEventListener('click', () => {
        setStage((activeIndex + 1) % steps.length);
    });

    tryBtn.addEventListener('click', () => {
        window.location.href = `index.html?example=${encodeURIComponent(example.slug)}&fov=100`;
    });

    stepTrack.querySelectorAll('.gallery-step-pill').forEach((pill) => {
        pill.addEventListener('click', () => {
            const nextIndex = parseInt(pill.getAttribute('data-step-index') || '0', 10);
            setStage(nextIndex);
        });
    });

    setStage(0);
    return card;
}

function buildSteps(example) {
    const base = `examples/${example.slug}`;
    const inputCandidates = buildCandidates(`${base}/input.jpg`);
    const overlayCandidates = buildCandidates(`${base}/overlay.jpg`, example.legacy?.overlay);
    const resultsCandidates = buildCandidates(`${base}/results.jpg`);
    const coordsCandidates = buildCandidates(`${base}/coords.jpg`);
    const satelliteCandidates = buildCandidates(`${base}/satellite.jpg`, example.legacy?.satellite);

    return [
        `
        <div class="gallery-stage">
            <div class="gallery-stage-title">Input photo</div>
            ${buildCandidateImage(inputCandidates, `${example.title} input photo`)}
        </div>
        `,
        `
        <div class="gallery-stage">
            <div class="gallery-stage-title">SegFormer skyline extraction</div>
            ${buildCandidateImage(overlayCandidates, `${example.title} skyline overlay`)}
        </div>
        `,
        `
        <div class="gallery-stage">
            <div class="gallery-stage-title">Top locations found</div>
            <div class="gallery-stage-grid">
                ${buildCandidateImage(resultsCandidates, `${example.title} results`)}
                <ul class="gallery-location-list">
                    ${example.locations.map((line) => `<li>${line}</li>`).join('')}
                </ul>
            </div>
        </div>
        `,
        `
        <div class="gallery-stage">
            <div class="gallery-stage-title">Coordinate verification and satellite context</div>
            <div class="gallery-stage-grid two-up">
                ${buildCandidateImage(coordsCandidates, `${example.title} coordinate mountain outline`)}
                ${buildCandidateImage(satelliteCandidates, `${example.title} satellite map view`)}
            </div>
        </div>
        `,
    ];
}

function buildCandidates(primaryPath, secondaryPath) {
    const set = [primaryPath];
    if (secondaryPath && !set.includes(secondaryPath)) {
        set.push(secondaryPath);
    }
    return set;
}

function buildCandidateImage(paths, altText) {
    const encoded = encodeURIComponent(JSON.stringify(paths));
    return `<img src="${paths[0]}" data-candidates="${encoded}" alt="${altText}" class="gallery-stage-image">`;
}

function wireImageFallbacks(root) {
    root.querySelectorAll('img').forEach((img) => {
        img.addEventListener('error', () => {
            if (img.getAttribute('data-fallback-final') === 'true') {
                return;
            }

            const currentSrc = img.getAttribute('src');
            const rawCandidates = decodeURIComponent(img.getAttribute('data-candidates') || '%5B%5D');
            const candidates = JSON.parse(rawCandidates);
            const nextSrc = candidates.find((candidate) => candidate !== currentSrc);

            if (nextSrc) {
                const remaining = candidates.filter((candidate) => candidate !== nextSrc);
                img.setAttribute('data-candidates', encodeURIComponent(JSON.stringify(remaining)));
                img.src = nextSrc;
                return;
            }

            img.classList.add('gallery-image-missing');
            img.alt = 'Example asset missing';
            img.setAttribute('data-fallback-final', 'true');
            img.src = createFallbackSVG();
        });
    });
}

function createFallbackSVG() {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700"><rect width="1200" height="700" fill="#e2e8f0"/><rect x="40" y="40" width="1120" height="620" rx="24" fill="#f8fafc" stroke="#94a3b8" stroke-width="6" stroke-dasharray="14 10"/><text x="600" y="325" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="42" fill="#334155">Example asset not added yet</text><text x="600" y="380" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="30" fill="#475569">Place image files under public/examples/&lt;example-slug&gt;/</text></svg>`;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}
