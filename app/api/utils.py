from fastapi import HTTPException, status
from sqlmodel import  Session
from app.models import Organisation

def fetch_organisation(organisation_id: int, session: Session) -> Organisation:
    
    organisation = session.get(Organisation, organisation_id)

    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation

def parse_bounding_box(bounding_box: str):
    if not bounding_box:
        return None

    coordinates = bounding_box.split(',')

    if len(coordinates) != 4:
        raise HTTPException(status_code=400, detail="bounding_box must contain  four values.")

    try:
        sw_lat, sw_lon, ne_lat, ne_lon = map(float, coordinates)
    except ValueError:
        raise HTTPException(status_code=400, detail="bounding_box values must be valid numbers.")

    return sw_lat, sw_lon, ne_lat, ne_lon

