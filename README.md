# BrandPulse — Connected Frontend + Backend

## Flow
Google Login -> persistent session -> authenticated frontend -> FastAPI backend -> autonomous mission -> final result + graph.

## 1. Firebase Google login
1. Create a Firebase project.
2. Enable Authentication > Sign-in method > Google.
3. Add a Web App and copy its Firebase config into `auth/firebase-config.js`.
4. For real backend token verification, create a Firebase service account and set `FIREBASE_SERVICE_ACCOUNT_JSON` to its JSON path.

## 2. Run
Double-click `run.bat`.

The backend runs at `http://127.0.0.1:8000` and the frontend at `http://127.0.0.1:5500`.

## 3. Demo mode
If Firebase is not configured, the login page creates a local Demo User session. The frontend sends a demo bearer token to the backend, so the frontend/backend connection still works end-to-end.

## 4. Real Google mode
When Firebase is configured, the frontend stores the Firebase ID token after Google login and sends it as `Authorization: Bearer <ID_TOKEN>` for mission requests. The FastAPI backend verifies that token with Firebase Admin.


## UI updates
- Pricing section removed from the marketing site.
- Competitive analytics charts added to the landing page.
- Root `login.html` and `signin.html` provide direct access to authentication.
- Final Result now includes confidence, competitor-positioning, and evidence-mix charts.
