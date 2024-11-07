from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from shapely.geometry import Point, Polygon
from typing import Optional
from app.db import get_db
from app.models import CreateLocation, Location,BoundingBox
from app.api.utils import fetch_organisation, parse_bounding_box, parse_bbox

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
    bounding_box: Optional[BoundingBox] = Depends(parse_bbox) 
    ) -> list[Location]:
    """
    Get locations for a specific organisation ID, optionally filtered by a bounding box.

    - **organisation_id**: ID of the organisation.
    - **bounding_box**: Optional bounding box filter (e.g., sw_lat,sw_lon,ne_lat,ne_lon).
    """
    fetch_organisation(organisation_id, session)
    query = select(Location).where(Location.organisation_id == organisation_id)
    
    if bounding_box:
        bbox_polygon = Polygon([
            (bounding_box.sw_lon, bounding_box.sw_lat),  
            (bounding_box.ne_lon, bounding_box.sw_lat),  
            (bounding_box.ne_lon, bounding_box.ne_lat),  
            (bounding_box.sw_lon, bounding_box.ne_lat),  
        ])

        locations = session.exec(query).all()

        #  Can use list comprehension as well but wants it to be readable
        locations_in_bbox = []
        for location in locations:
            point = Point(location.longitude, location.latitude)

            if point.within(bbox_polygon):
                locations_in_bbox.append(location)
        return locations_in_bbox

    return session.exec(query).all()
