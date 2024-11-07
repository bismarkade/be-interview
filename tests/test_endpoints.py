from pathlib import Path
from typing import Generator
from unittest.mock import patch
from uuid import uuid4
from fastapi import status, HTTPException
import alembic.command
import alembic.config
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.db import get_database_session
from app.main import app
from app.models import BoundingBox
from app.api.utils import parse_bounding_box

_ALEMBIC_INI_PATH = Path(__file__).parent.parent / "alembic.ini"

@pytest.fixture()
def test_client() -> TestClient:
    return TestClient(app)

@pytest.fixture(autouse=True)
def apply_alembic_migrations() -> Generator[None, None, None]:
    # Creates test database per test function
    test_db_file_name = f"test_{uuid4()}.db"
    database_path = Path(test_db_file_name)
    try:
        test_db_url = f"sqlite:///{test_db_file_name}"
        alembic_cfg = alembic.config.Config(_ALEMBIC_INI_PATH)
        alembic_cfg.attributes["sqlalchemy_url"] = test_db_url

        alembic.command.upgrade(alembic_cfg, "head")

        test_engine = create_engine(test_db_url, echo=True)
        with patch("app.db.get_engine") as mock_engine:
            mock_engine.return_value = test_engine
            yield
    finally:
        # database_path.unlink(missing_ok=True)
        if database_path.exists():
            try:
                database_path.unlink(missing_ok=True)
                print(f"Deleted database file: {database_path}")  # Confirmation of deletion
            except Exception as e:
                print(f"Failed to delete {database_path}: {e}")  # Log any errors during deletion
        else:
            print(f"Database file {database_path} does not exist, skipping deletion.")  


def test_organisation_creation_and_retrieval(test_client: TestClient) -> None:
    list_of_organisation_names_to_create = [
        "Climate Research Institute",
        "European Environmental Agency",
        "Green Solutions Network"
    ]

    # Create organisations
    for organisation_name in list_of_organisation_names_to_create:
        response = test_client.post("/api/organisations/create", json={"name": organisation_name})
        assert response.status_code == status.HTTP_200_OK

    # Validate that organisations exist in database
    response = test_client.get("/api/organisations")
    organisations = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(organisations) == len(list_of_organisation_names_to_create)  # Check if the number of retrieved orgs matches created

    created_organisation_names = set(organisation["name"] for organisation in organisations)
    assert created_organisation_names == set(list_of_organisation_names_to_create)


def test_location_creation(test_client: TestClient) -> None:
    """
    create an organization and then create a location location associated with them
    """
    # Create an organization first to associate locations with
    organisation_response = test_client.post("/api/organisations/create", json={"name": "Climate Research Institute"})
    organisation_id = organisation_response.json()["id"]
    print("organisation_id")
    print(organisation_id)

    # Define test locations with real coordinates
    locations_data = [
        {"organisation_id": organisation_id, "location_name": "Salzburg", "longitude": 13.0550, "latitude": 47.8095},
        {"organisation_id": organisation_id, "location_name": "Vienna", "longitude": 16.3738, "latitude": 48.2082},
        {"organisation_id": organisation_id, "location_name": "Berlin", "longitude": 13.4050, "latitude": 52.5200},
        {"organisation_id": organisation_id, "location_name": "Paris", "longitude": 2.3522, "latitude": 48.8566},
        {"organisation_id": organisation_id, "location_name": "Amsterdam", "longitude": 4.9041, "latitude": 52.3676},
    ]

    # Test creating locations
    for location_data in locations_data:
        response = test_client.post("/api/organisations/create/locations", json=location_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["location_name"] == location_data["location_name"]

def test_location_retrieval_by_organisation(test_client: TestClient) -> None:
    # Create an organization and locations for testing
    organisation_response = test_client.post("/api/organisations/create", json={"name": "Climate Research Institute"})
    organisation_id = organisation_response.json()["id"]

    locations_data = [
        {"organisation_id": organisation_id, "location_name": "Salzburg", "longitude": 13.0550, "latitude": 47.8095},
        {"organisation_id": organisation_id, "location_name": "Vienna", "longitude": 16.3738, "latitude": 48.2082},
    ]

    for location_data in locations_data:
        test_client.post("/api/organisations/create/locations", json=location_data)

    # Test getting locations by organisation ID
    response = test_client.get(f"/api/organisations/{organisation_id}/locations")
    assert response.status_code == status.HTTP_200_OK
    locations = response.json()
    assert len(locations) == len(locations_data)
    for location_data in locations_data:
        assert any(location["location_name"] == location_data["location_name"] for location in locations)


def test_location_filtering_by_bounding_box(test_client: TestClient) -> None:
    # Create an organization and locations for testing
    organisation_response = test_client.post("/api/organisations/create", json={"name": "Climate Research Institute"})
    organisation_id = organisation_response.json()["id"]

    # Sample location data
    locations_data = [
        {"organisation_id": organisation_id, "location_name": "Salzburg", "longitude": 13.0550, "latitude": 47.8095},
        {"organisation_id": organisation_id, "location_name": "Vienna", "longitude": 16.3738, "latitude": 48.2082},
        {"organisation_id": organisation_id, "location_name": "Berlin", "longitude": 13.4050, "latitude": 52.5200},
    ]

    # Create locations in the database
    for location_data in locations_data:
        test_client.post("/api/organisations/create/locations", json=location_data)

    # bounding box that covers Salzburg and Vienna
    # sw_lat, sw_lon, ne_lat, ne_lon
    response = test_client.get(f"/api/organisations/{organisation_id}/locations?sw_lat=46.5&sw_lon=12.0&ne_lat=49.0&ne_lon=17.0")
    
    # Check response status code
    assert response.status_code == status.HTTP_200_OK
    
    # Retrieve filtered locations
    filtered_locations = response.json()

    # Salzburg and Vienna should be returned
    assert len(filtered_locations) == 2
    assert any(location["location_name"] == "Salzburg" for location in filtered_locations)
    assert any(location["location_name"] == "Vienna" for location in filtered_locations)
    
    # Berlin should be excluded, as it's outside the bounding box
    assert not any(location["location_name"] == "Berlin" for location in filtered_locations)

