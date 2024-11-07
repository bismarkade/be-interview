from fastapi import HTTPException, status, Query
from sqlmodel import  Session
from app.models import Organisation, BoundingBox

def fetch_organisation(organisation_id: int, session: Session) -> Organisation:
    
    organisation = session.get(Organisation, organisation_id)

    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation

def parse_bounding_box(bounding_box: BoundingBox | None) -> BoundingBox | None:
    """Validate and return a BoundingBox object or None if the input is empty."""
    
    if bounding_box is None:
        return None

    # Validate bounding box coordinates
    if not all(isinstance(coord, float) for coord in [
        bounding_box.sw_lat, bounding_box.sw_lon, bounding_box.ne_lat, bounding_box.ne_lon
    ]):
        raise HTTPException(status_code=400, detail="All bounding_box coordinates must be valid numbers.")
    
    return bounding_box

def parse_bbox(
    sw_lat: float = Query(None, alias="sw_lat"),
    sw_lon: float = Query(None, alias="sw_lon"),
    ne_lat: float = Query(None, alias="ne_lat"),
    ne_lon: float = Query(None, alias="ne_lon")  
) -> BoundingBox:
    """
    Parses and returns a BoundingBox object if all bounding box coordinates are provided, otherwise returns None.
    """
    if sw_lat is not None and sw_lon is not None and ne_lat is not None and ne_lon is not None:
        return BoundingBox(sw_lat=sw_lat, sw_lon=sw_lon, ne_lat=ne_lat, ne_lon=ne_lon)
    return None  
