"""API package."""

from fastapi import APIRouter

from . import patients

router = APIRouter()
router.include_router(patients.router)

