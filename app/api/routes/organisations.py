from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from app.db import get_db
from app.models import Location, CreateLocation, Organisation, CreateOrganisation
from app.api.utils import fetch_organisation

router = APIRouter()

@router.post("/create", response_model=Organisation)
def create_organisation(create_organisation: CreateOrganisation, session: Session = Depends(get_db)) -> Organisation:
    """Create an organisation."""
    organisation = Organisation(name=create_organisation.name)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)
    return organisation


@router.get("/", response_model=list[Organisation])
def get_organisations(session: Session = Depends(get_db)) -> list[Organisation]:
    """
    Get all organisations.
    """
    organisations = session.exec(select(Organisation)).all()
    return organisations



@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(organisation_id: int, session: Session = Depends(get_db)) -> Organisation:
    """
    Get an organisation by id.
    """
    organisation = session.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation


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
    session: Session = Depends(get_db)
    ) -> list[Location]:

    """
    Get locations for a specific organisation ID, optionally filtered by a bounding box.

    """

    organization_location_query = select(Location).where(Location.organisation_id == organisation_id)

    return session.exec(organization_location_query).all()
