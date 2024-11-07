from sqlmodel import SQLModel, Field, Relationship


class Base(SQLModel):
    pass

class CreateOrganisation(Base):
    name: str


class Organisation(Base, table=True):
    id: int | None = Field(primary_key=True)
    name: str


class CreateLocation(Base):
    organisation_id: int
    location_name: str
    longitude: float
    latitude: float

class Location(Base, table=True):
    id: int | None = Field(primary_key=True)
    organisation_id: int = Field(foreign_key="organisation.id")
    organisation: Organisation = Relationship()
    location_name: str
    longitude: float
    latitude: float

class BoundingBox(Base):
    """
     Geographical bounding box Model
    """
    sw_lat: float
    sw_lon: float
    ne_lat: float
    ne_lon: float