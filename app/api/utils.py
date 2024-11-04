from fastapi import HTTPException, status
from sqlmodel import  Session
from app.models import Organisation

def fetch_organisation(organisation_id: int, session: Session) -> Organisation:
    
    organisation = session.get(Organisation, organisation_id)

    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation
