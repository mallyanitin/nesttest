"""Renderer service for retrieving rendered DICOM instances."""

from typing import Tuple

from fastapi import HTTPException

from .dicom_client import get_dicom_client


def get_rendered_image(patient_id: str, sop_instance_uid: str) -> bytes:
    """Retrieve rendered PNG for given SOP Instance UID."""
    client = get_dicom_client()

    # Find instance to obtain study and series UIDs
    instances = client.search_for_instances({"PatientID": patient_id, "SOPInstanceUID": sop_instance_uid})
    if not instances:
        raise HTTPException(status_code=404, detail="Instance not found")

    instance = instances[0]
    study_uid = instance.get("0020000D")  # StudyInstanceUID
    series_uid = instance.get("0020000E")  # SeriesInstanceUID

    rendered = client.retrieve_instance_rendered(
        study_instance_uid=study_uid,
        series_instance_uid=series_uid,
        sop_instance_uid=sop_instance_uid,
        media_types=("image/png",),
    )
    return rendered

