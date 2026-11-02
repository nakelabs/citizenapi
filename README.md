# Citizens Incident Reporting API

A production FastAPI backend designed to run on Render.com with PostgreSQL, powering a mobile incident reporting application.

## Overview

The API supports real-time community incident reporting with GPS tracking, photo evidence handling, category filtering, and user authentication.

## Key Features

- Incident Reporting: Submit incident reports with titles, descriptions, categories, GPS coordinates (latitude/longitude), and optional base64 photo evidence.
- Community Feed: View all submitted reports sorted chronologically with author attribution.
- Category Filtering: Filter the live feed by category (Accident, Fighting, Rioting, Robbery, Other).
- User Authentication: Secure registration and login using PBKDF2-SHA256 password hashing and HS256 JWT bearer tokens.
- Streamlined Testing: Automatic user registration on login if credentials do not exist, simplifying examiner assessment.
- Personal Incident Management: Authenticated endpoint to retrieve reports created by the current user along with submission counts.
- Flexible Reporting: Allows both authenticated citizen reports and anonymous guest submissions.
- Database Lifecycle: Automatic table creation on startup and automated seeding with realistic community incident data if the database is empty.
- Mobile Webview Support: Permissive CORS configuration accommodating Cordova native Android apps running under file:// and http://localhost.

## Tech Stack

- Framework: FastAPI
- Server: Uvicorn
- Database: PostgreSQL
- ORM: SQLAlchemy
- Data Validation: Pydantic v2
- Authentication: JWT (RFC 7519) and PBKDF2
