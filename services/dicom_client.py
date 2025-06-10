"""Utility to initialize and provide a DICOMwebClient instance."""

from functools import lru_cache
from typing import Optional

from requests.auth import HTTPBasicAuth
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    DICOMWEB_URL: str
    DICOMWEB_USER: Optional[str] = None
    DICOMWEB_PASS: Optional[str] = None

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


@lru_cache()
def get_dicom_client() -> DICOMwebClient:
    """Construct and cache a DICOMwebClient with basic auth."""
    settings = get_settings()
    auth = None
    if settings.DICOMWEB_USER and settings.DICOMWEB_PASS:
        auth = HTTPBasicAuth(settings.DICOMWEB_USER, settings.DICOMWEB_PASS)
    session = create_session_from_auth(auth) if auth else None
    client = DICOMwebClient(url=settings.DICOMWEB_URL, session=session)
    return client

