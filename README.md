# SummitSight

SummitSight is a mountain photo geolocation system that identifies locations candidates by matching an extracted skyline contour against a large DEM-derived skyline database for the Pyrenees.

This repository contains:
- A web UI for uploading skyline images and viewing ranked matches.
- A Node.js proxy server for uploads and requests.
- A Python API for segmentation, search pipeline execution, and progress polling.
- Core retrieval algorithms (coarse FFT search, geographic refine, final ranking).

WARNING:  this is not an easy project to run locally. There are a lot of dependencies to install, models to load, and very large data files that are required. The computer running the project locally must have a lot of RAM or the project will probably crash when trying to load the ML models. 

If you want to try out SummitSight for yourself, it is much easier to use the web-hosted version, ready made for your geolocating needs. 
The URL is:
www.summits.studio

## High Level Architecture

Runtime flow:
1. User uploads image in `public/index.html`.
2. Browser sends image to Node endpoint `/api/extract` (`server.js`).
3. Node forwards to Python `/extract` (`scripts/summit_api.py`).
4. Python runs skyline extraction (`scripts/skyline_hybrid_improved.py`) and stores session data.
5. Browser confirms extraction, then starts `/api/search`.
6. Python runs search pipeline (`scripts/search_pipeline.py`) using:
   - Stage 1 coarse retrieval (`scripts/coarse_search.py`)
   - Stage 2 geographic refinement (`scripts/refine.py`)
   - Stage 3 final ranking (`scripts/refine.py`)
7. Browser polls `/api/search-progress/:sessionId`, then renders map and match cards in `public/results.html` and `public/js/results.js`.

### Core runtime

- `server.js`
  - Express server.
  - Serves static frontend and upload files.
  - Proxies requests to Python API.
- `scripts/summit_api.py`
  - Flask API with async extraction/search jobs.
  - Lazy-loads segmentation models and data arrays.
  - Exposes `/extract`, `/extract-progress/<id>`, `/search`, `/search-progress/<id>`, `/health`, `/stats`.
- `scripts/search_pipeline.py`
  - Orchestrates end-to-end retrieval pipeline.
- `scripts/coarse_search.py`
  - Vectorized FFT-based NCC coarse search over full database.
- `scripts/refine.py`
  - Geographic expansion, refined NCC, final ranking, confidence scoring.
- `scripts/geo_utils.py`
  - Data loading, KD-tree neighborhood lookup, haversine, resampling, pixel-to-elevation conversion.
- `scripts/fov.py`
  - EXIF and iterative FOV estimation utilities.
- `scripts/skyline_hybrid_improved.py`
  - SegFormer extraction pipeline (with compatibility wrappers for legacy callers).

### Frontend

- `public/index.html` + `public/js/upload.js`
  - Upload, extraction approval, FOV selection, search launch.
- `public/results.html` + `public/js/results.js`
  - Renders ranked matches, confidence metrics, skyline alignment chart, and map.
- `public/about.html` + `public/js/about.js`
  - Project narrative and pipeline visuals.
- `public/gallery.html` + `public/js/gallery.js`
  - Interactive examples and pipeline replay UI.
- `public/admin.html` + `public/js/admin.js`
  - Operational health dashboard.
- `public/js/config.js`
  - Environment-dependent API base URL selection.
- `public/js/theme.js`
  - Theme preference behavior.

## Data and models

- `data/metadata_250m.npy` - `[lat, lon, elevation_m]` per viewpoint.
- `data/skylines_250m.npy` - 360-degree skyline profiles (720 samples).
- `data/skylines_rfft.npy` - precomputed FFT for coarse search.
- `data/skylines_sq_rfft.npy` - precomputed squared FFT for NCC normalisation.
- `data/skylines_norm.npz` - normalisation stats.

These are very large files (over 9GBs in total). 
Here are sharepoint links to download them:
URL_METADATA="https://livewarwickac-my.sharepoint.com/:u:/g/personal/u5513359_live_warwick_ac_uk/IQCX0ADjOUxrSaR-OwLVl5EvASzAhKCJzerhS54De7euAUc?e=22GmPs&download=1" # metadata_250m.npy       
URL_SKYLINES="https://livewarwickac-my.sharepoint.com/:u:/g/personal/u5513359_live_warwick_ac_uk/IQCXtHBPS8XsSam5qd17Dl3TAcQeHLpHtXTnLysQISFWfzM?e=rm8hbn&download=1" # skylines_250m.npy       
URL_NORM="https://livewarwickac-my.sharepoint.com/:u:/g/personal/u5513359_live_warwick_ac_uk/IQDwXmmHWYSYTr-CE02ozTJjAeGQCPvvcYC4G0Pv8JWagZQ?e=0lTgk3&download=1" # skylines_norm.npz       
URL_RFFT="https://livewarwickac-my.sharepoint.com/:u:/g/personal/u5513359_live_warwick_ac_uk/IQDSNjC0SxmXQrEnJgP0MIfaAWxRTweRYeddK4Rq2WO2JBA?e=ZlRVyZ&download=1" # skylines_rfft.npy       
URL_SQ_RFFT="https://livewarwickac-my.sharepoint.com/:u:/g/personal/u5513359_live_warwick_ac_uk/IQAG8nqIJXrLRbrMcsx6jIbbAZ5GoG3wimeNjv9QMmL6U-M?e=mdIXTg&download=1" # skylines_sq_rfft.npy     


## Prerequisites

- Node.js 18+ (recommended).
- Python 3.12.
- Pip and virtual environment tooling.
- Enough RAM to hold model + mmap workloads comfortably.
- Everythiing in requirements-backend.txt

## Startup

Terminal 1:

npm install 
python scripts/summit_api.py


Terminal 2:

npm run dev

Then open:
- UI: `http://localhost:3000`
- Python health: `http://localhost:5000/health`
