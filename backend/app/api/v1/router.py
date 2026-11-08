from fastapi import APIRouter

from app.api.v1.endpoints import assets, auth, engagements, scans

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(engagements.router)
api_router.include_router(assets.router)
api_router.include_router(scans.router)
