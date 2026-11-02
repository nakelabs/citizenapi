# Citizens Incident Reporting API (FastAPI + PostgreSQL on Render)

Production-grade, modular, and deployable FastAPI backend designed for **Render.com** with **PostgreSQL**. Powers the **Citizens Incident Reporting Mobile App** (supporting native Cordova Android WebViews, GPS coordinates, photo evidence, category filtering, auto-registration for examiners, and personal report management).

---

## 📁 Project Architecture & File Structure

```text
citizenapi/
├── main.py              # FastAPI app, CORS, routes, lifecycle & seed runner
├── database.py          # SQLAlchemy engine (pre-ping/reconnect), Render URI fix, get_db
├── models.py            # Declarative User & Incident models with author_username
├── schemas.py           # Pydantic v2 input/output validation schemas
├── auth.py              # NIST PBKDF2 password hashing & RFC 7519 JWT auth handling
├── requirements.txt     # Production dependencies
├── render.yaml          # Render Blueprint deployment definition
├── test_api.py          # Verification test suite for all 8 test requirements
├── .gitignore           # Git ignore rules
└── README.md            # Deployment & API documentation
```

---

## 🚀 Exact Render.com Deployment Settings

When deploying to [Render](https://render.com) as a **Web Service**:

| Setting | Exact Value |
| :--- | :--- |
| **Environment** | `Python` |
| **Region** | `Frankfurt (EU Central)` or closest to your users |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Environment Variables on Render
Set these in the **Environment** tab of your Render Web Service:

| Key | Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | *Render PostgreSQL Internal Database URL* | Render provides `postgres://...` which `database.py` automatically normalizes to `postgresql://`. |
| `SECRET_KEY` | *(Click "Generate" or any secure random string)* | Used for cryptographic signing of Bearer JWT tokens. |
| `PYTHON_VERSION` | `3.11.8` | Recommended Python version on Render. |

---

## 📋 Step-by-Step Render Setup Guide

### Option A: 1-Click Render Blueprint (Recommended)
Because this repository includes [`render.yaml`](file:///c:/Users/HomePC/Desktop/citizenapi/render.yaml), you can deploy both the database and web service together:
1. Push this project to GitHub.
2. In Render, navigate to **Blueprints** -> **New Blueprint Instance**.
3. Select your repository. Render will automatically provision:
   - A free managed **PostgreSQL** instance (`citizen-db`)
   - The FastAPI **Web Service** (`citizen-incident-api`) linked to that database.

---

### Option B: Manual Setup via Dashboard

#### 1. Create the PostgreSQL Database
1. Go to **Dashboard** -> **New +** -> **PostgreSQL**.
2. Set:
   - **Name:** `citizen-db`
   - **Database:** `citizen_incident_db`
   - **User:** `citizen_user`
   - **Plan:** Free
3. Click **Create Database**.
4. Once created, copy the **Internal Database URL** (e.g. `postgres://citizen_user:pwd@dpg-xxx:5432/citizen_incident_db`).

#### 2. Create the Web Service
1. Go to **Dashboard** -> **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**:
   - Add `DATABASE_URL` and paste the Internal Database URL from Step 1.
   - Add `SECRET_KEY` (use any random string or click Generate).
5. Click **Create Web Service**.

Tables will be created automatically on the first startup (`Base.metadata.create_all`), and realistic Nigerian incident seed data will be populated automatically.

---

## 📡 API Endpoints Reference

### 1. Health & Discovery
- **`GET /`**: API status, version, and route directory.
- **`GET /docs`**: Interactive Swagger UI.
- **`GET /redoc`**: OpenAPI ReDoc documentation.

---

### 2. Authentication (`/auth`)

#### `POST /auth/register`
Creates a new citizen account.
- **Request Body:**
  ```json
  {
    "username": "adebayo",
    "password": "mypassword123"
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "adebayo",
    "id": 1
  }
  ```

#### `POST /auth/login`
Validates user credentials. **Examiner Feature:** If the user does not exist, automatically registers and signs them in seamlessly.
- **Request Body:**
  ```json
  {
    "username": "examiner_guest",
    "password": "anypassword"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "examiner_guest",
    "id": 2
  }
  ```

#### `GET /auth/me`
Requires `Authorization: Bearer <token>`.
- **Response (`200 OK`):**
  ```json
  {
    "id": 1,
    "username": "adebayo",
    "created_at": "2026-11-02T10:45:00Z",
    "reports_count": 3
  }
  ```

---

### 3. Incidents (`/incidents`)

#### `GET /incidents`
Returns community reports sorted chronologically (newest first).
- **Query Parameter:** `category` (optional, default: `"All"`). Supported values: `Accident`, `Fighting`, `Rioting`, `Robbery`, `Other`, or `All`.
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": 1,
      "title": "Multi-vehicle collision along Lekki-Epe Expressway",
      "category": "Accident",
      "description": "Two passenger buses and a saloon car involved in a collision near Chisco Bus Stop.",
      "latitude": 6.4414,
      "longitude": 3.4988,
      "photo_base64": null,
      "created_at": "2026-11-02T10:30:00Z",
      "author_username": "LagosWatch"
    }
  ]
  ```

#### `GET /incidents/me`
Requires `Authorization: Bearer <token>`. Returns all incidents created by the authenticated user.
- **Response (`200 OK`):**
  ```json
  [
    {
      "id": 5,
      "title": "Flash flooding on Admiralty Way",
      "category": "Accident",
      "description": "Heavy rainfall has led to severe waterlogging obstructing small cars.",
      "latitude": 6.4474,
      "longitude": 3.4723,
      "photo_base64": "data:image/jpeg;base64,...",
      "created_at": "2026-11-02T11:15:00Z",
      "author_username": "adebayo"
    }
  ]
  ```

#### `POST /incidents`
Submits a new incident. Supports both guest and authenticated users:
- **Header:** `Authorization: Bearer <token>` (Optional). If provided, links report to user account; if omitted, attributes to guest (`"Anonymous"`).
- **Request Body:**
  ```json
  {
    "title": "Broken traffic light causing gridlock",
    "category": "Other",
    "description": "Traffic lights at Allen Junction are malfunctioning since morning.",
    "latitude": 6.6018,
    "longitude": 3.3515,
    "photo_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
  ```
- **Response (`201 Created`):**
  ```json
  {
    "id": 6,
    "title": "Broken traffic light causing gridlock",
    "category": "Other",
    "description": "Traffic lights at Allen Junction are malfunctioning since morning.",
    "latitude": 6.6018,
    "longitude": 3.3515,
    "photo_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "created_at": "2026-11-02T11:50:00Z",
    "author_username": "Anonymous"
  }
  ```

---

## 🧪 Local Testing & Verification

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the automated test suite:
   ```bash
   python test_api.py
   ```
3. Run the development server locally:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs) to access Swagger UI.
