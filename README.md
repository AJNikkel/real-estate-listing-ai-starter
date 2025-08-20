# Real Estate Listing AI Starter

This repository contains a simple full‑stack template for generating real estate listing and marketing copy using AI. It consists of a minimal FastAPI backend and a static front‑end that can be hosted on Netlify. The backend can run in `mock` mode (no API key required) or connect to OpenAI when provided with a valid API key.

## Structure

```
├── backend
│   ├── app
│   │   └── main.py      # FastAPI application
│   └── requirements.txt # Python dependencies
├── frontend
│   └── index.html       # Simple HTML UI for the generator
└── netlify.toml         # Netlify configuration for static hosting
```

## Backend

The backend is a small FastAPI service that exposes a single `/generate` endpoint. It accepts JSON describing the property details, tone, audience, output type and optional word count. In `mock` mode it returns a placeholder response. When `PROVIDER=openai` and an `OPENAI_API_KEY` is set, it will use the OpenAI API to generate content. The OpenAI call is intentionally simple and can be customised to fit your brand voice or other requirements.

To run locally:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables:

- `PROVIDER` – either `mock` (default) or `openai`
- `OPENAI_API_KEY` – only required when using `PROVIDER=openai`

## Front‑end

The front‑end is a single static HTML page with embedded JavaScript to call the backend. It collects basic information about a property and calls the `/generate` endpoint. The API base URL can be customised by appending `?api=https://your-backend-url` to the site URL, or by saving a value in local storage (`apiBase`).

To preview locally, open `frontend/index.html` in your browser after starting the backend.

## Deployment

### Backend on Render

Render requires your code to be in a Git repository (GitHub or GitLab). Once the repository is created, sign in to [Render](https://render.com/), choose **New Web Service**, and select your repository’s `backend` directory as the root. Use the following settings:

- **Environment**
  - `PROVIDER=mock` for testing
  - `OPENAI_API_KEY=sk-...` if using OpenAI
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- **Instance Type**: Free

After deployment, note the service URL. This will become your API base for the front‑end.

### Front‑end on Netlify

Netlify can host the static front‑end directly. Sign in to [Netlify](https://app.netlify.com/), choose **Add new site → Import from Git** and select your repository’s `frontend` directory as the publish directory. In your site settings, define the environment variable `VITE_API_BASE` or deploy with a query parameter `?api=` pointing at your Render backend. Netlify will automatically build and serve the `frontend` folder.

Alternatively, you can drag and drop the `frontend/` directory to Netlify’s **Deploy manually** page for quick testing.

## Customisation

The prompt used to generate copy can be customised in `backend/app/main.py`. The front‑end form can be styled further by editing the embedded CSS in `frontend/index.html`. For a more sophisticated UI consider replacing the static HTML with a React or Vue application and connecting it to the same API endpoint.
