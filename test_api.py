import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./citizen_test.db"

from main import app
from database import engine, Base

def run_tests():
    Base.metadata.drop_all(bind=engine)
    
    with TestClient(app) as client:
        res = client.get("/")
        assert res.status_code == 200

        res = client.get("/incidents")
        assert res.status_code == 200
        feed = res.json()
        assert len(feed) >= 3

        res = client.get("/incidents?category=Accident")
        assert res.status_code == 200
        accidents = res.json()
        assert len(accidents) >= 1
        assert all(i["category"].lower() == "accident" for i in accidents)

        res = client.post("/auth/register", json={"username": "adebayo", "password": "password123"})
        assert res.status_code == 201
        reg_data = res.json()
        token = reg_data["token"]
        assert reg_data["username"] == "adebayo"

        res = client.post("/auth/login", json={"username": "examiner_guest", "password": "temp_password"})
        assert res.status_code == 200
        assert res.json()["username"] == "examiner_guest"

        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["reports_count"] == 0

        res = client.post("/incidents", json={
            "title": "Broken traffic light causing gridlock",
            "category": "Other",
            "description": "Traffic lights at Allen Junction are malfunctioning since morning.",
            "latitude": 6.6018,
            "longitude": 3.3515,
            "photo_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        })
        assert res.status_code == 201
        assert res.json()["author_username"] == "Anonymous"

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
        assert user_incident["author_username"] == "adebayo"

        res = client.get("/incidents/me", headers=headers)
        assert res.status_code == 200
        my_reports = res.json()
        assert len(my_reports) == 1
        assert my_reports[0]["id"] == user_incident["id"]

        res = client.get("/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["reports_count"] == 1

        print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
    engine.dispose()
    if os.path.exists("citizen_test.db"):
        try:
            os.remove("citizen_test.db")
        except Exception:
            pass
