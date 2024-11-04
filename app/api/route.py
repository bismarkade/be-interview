from fastapi import APIRouter

from app.api.routes import (
    organisations,
    locations
    )

api_router = APIRouter()

api_router.include_router(organisations.router, prefix="/organisations", tags=["organisation"])
api_router.include_router(locations.router, prefix="/organisations", tags=["location"])