from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from app.db import get_db
from app.models import Location, CreateLocation, Organisation, CreateOrganisation
from app.api.utils import fetch_organisation, parse_bounding_box

router = APIRouter()


@router.post("/create", response_model=Organisation)
def create_organisation(
    create_organisation: CreateOrganisation, 
    session: Session = Depends(get_db)
    ) -> Organisation:
    "" """
    Create a new organisation.

    - **create_organisation**: Organisation data (name).
    """
    organisation = Organisation(name=create_organisation.name)

    session.add(organisation)
    session.commit()
    session.refresh(organisation)

    return organisation

@router.get("/", response_model=list[Organisation])
def get_organisations(
    session: Session = Depends(get_db)
    ) -> list[Organisation]:

    """
    Retrieve all organisations.
    """
    organisations = session.exec(select(Organisation)).all()

    return organisations


@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(
    organisation_id: int, 
    session: Session = Depends(get_db)
    ) -> Organisation:
    """
    Fetch an organisation by its ID.

    - **organisation_id**: ID of the organisation to retrieve.
    """

    return fetch_organisation(organisation_id, session)



