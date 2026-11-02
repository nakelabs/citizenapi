"""
Automated Verification Suite for Citizen Incident Reporting API.
Tests all 8 core capabilities:
1. Startup & Seeding
2. Authentication (Register)
3. Authentication (Login with Auto-Registration)
4. Authenticated /auth/me with reports count
5. Anonymous Incident Submission (POST /incidents)
6. Authenticated Incident Submission (POST /incidents)
7. Community Feed & Category Filtering (GET /incidents?category=...)
8. Personal Incident Management (GET /incidents/me)
"""

import os
from fastapi.testclient import TestClient

# Ensure test DB is used
os.environ["DATABASE_URL"] = "sqlite:///./citizen_test.db"

from main import app
from database import engine, Base

def run_tests():
    # Reset test database
    Base.metadata.drop_all(bind=engine)
    
    with TestClient(app) as client:
        print("\n--- 1. Testing Health & Root Endpoint ---")
        res = client.get("/")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print("Root response:", res.json())

        print("\n--- 2. Testing Database Seeding on Startup ---")
        res = client.get("/incidents")
        assert res.status_code == 200
        feed = res.json()
        print(f"Initial feed item count: {len(feed)}")
        assert len(feed) >= 3, "Database should be seeded with at least 3 incidents"
        for item in feed:
            print(f" - [{item['category']}] {item['title']} (by {item['author_username']})")

        print("\n--- 3. Testing Category Filter ---")
        res = client.get("/incidents?category=Accident")
        assert res.status_code == 200
        accidents = res.json()
        assert len(accidents) >= 1
        assert all(i["category"].lower() == "accident" for i in accidents)
        print(f"Category filter 'Accident' returned {len(accidents)} item(s).")

        print("\n--- 4. Testing User Registration ---")
        res = client.post("/auth/register", json={"username": "adebayo", "password": "password123"})
        assert res.status_code == 201
        reg_data = res.json()
        token = reg_data["token"]
        user_id = reg_data["id"]
        print(f"Registered user '{reg_data['username']}' (ID: {user_id}) with token.")

        print("\n--- 5. Testing Auto-Registration on Login for New User ---")
        res = client.post("/auth/login", json={"username": "examiner_guest", "password": "temp_password"})
        assert res.status_code == 200
        examiner_data = res.json()
        examiner_token = examiner_data["token"]
        print(f"Auto-registered and logged in examiner user '{examiner_data['username']}'.")

        print("\n--- 6. Testing /auth/me for Authenticated User ---")
        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/auth/me", headers=headers)
        assert res.status_code == 200
        me = res.json()
        print(f"User /auth/me: id={me['id']}, username={me['username']}, reports_count={me['reports_count']}")
        assert me["reports_count"] == 0

        print("\n--- 7. Testing Anonymous Incident Submission ---")
        res = client.post("/incidents", json={
            "title": "Broken traffic light causing gridlock",
            "category": "Other",
            "description": "Traffic lights at Allen Junction are malfunctioning since morning.",
            "latitude": 6.6018,
            "longitude": 3.3515,
            "photo_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        })
        assert res.status_code == 201
        anon_incident = res.json()
        print("Anonymous Incident Created:", anon_incident["title"], "| Author:", anon_incident["author_username"])
        assert anon_incident["author_username"] == "Anonymous"

        print("\n--- 8. Testing Authenticated Incident Submission & /incidents/me ---")
        res = client.post("/incidents", headers=headers, json={
            "title": "Flash flooding on Admiralty Way",
            "category": "Accident",
            "description": "Heavy rainfall has led to severe waterlogging obstructing small cars.",
            "latitude": 6.4474,
            "longitude": 3.4723,
            "photo_base64": None
        })
        assert res.status_code == 201
        user_incident = res.json()
        print("User Incident Created:", user_incident["title"], "| Author:", user_incident["author_username"])
        assert user_incident["author_username"] == "adebayo"

        # Check /incidents/me
        res = client.get("/incidents/me", headers=headers)
        assert res.status_code == 200
        my_reports = res.json()
        print(f"/incidents/me returned {len(my_reports)} report(s).")
        assert len(my_reports) == 1
        assert my_reports[0]["id"] == user_incident["id"]

        # Check /auth/me reports count updated
        res = client.get("/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["reports_count"] == 1
        print("Updated reports count verified:", res.json()["reports_count"])

        print("\n ALL 8 TEST REQUIREMENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
    # Dispose engine to release Windows file lock before cleanup
    engine.dispose()
    if os.path.exists("citizen_test.db"):
        try:
            os.remove("citizen_test.db")
        except Exception:
            pass

