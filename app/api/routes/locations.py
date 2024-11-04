from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from app.db import get_db
from app.models import CreateLocation, Location
from app.api.utils import fetch_organisation, parse_bounding_box

router = APIRouter()

@router.post("/create/locations", response_model=Location)
def create_location(
    create_location: CreateLocation,
    session: Session = Depends(get_db)
    )-> Location:
    """
    Create a new location associated with an organisation.

    - **create_location**: Location data (organisation_id, name, coordinates(lon, lat)).
    """
    organisation = fetch_organisation(create_location.organisation_id, session)

    location = Location(
        organisation_id = organisation.id,
        location_name = create_location.location_name,
        longitude = create_location.longitude,
        latitude = create_location.latitude
    )

    session.add(location)
    session.commit()
    session.refresh(location)

    return location



@router.get("/{organisation_id}/locations", response_model=list[Location])
def get_organisation_locations(
    organisation_id: int, 
    session: Session = Depends(get_db), 
    bounding_box: str = None  
    ) -> list[Location]:
    """
    Get locations for a specific organisation ID, optionally filtered by a bounding box.

    - **organisation_id**: ID of the organisation.
    - **bounding_box**: Optional bounding box filter (e.g., sw_lat,sw_lon,ne_lat,ne_lon).
    """
    fetch_organisation(organisation_id, session)
    query = select(Location).where(Location.organisation_id == organisation_id)

    bbox_coordinates = parse_bounding_box(bounding_box)
    if bbox_coordinates:
        sw_lat, sw_lon, ne_lat, ne_lon = bbox_coordinates
        query = query.where(
            (Location.latitude >= sw_lat) & (Location.latitude <= ne_lat) &
            (Location.longitude >= sw_lon) & (Location.longitude <= ne_lon)
        )
    

    return session.exec(query).all()
