"""API routes for patient operations."""

from fastapi import APIRouter, HTTPException

from ..services.dicom_client import get_dicom_client
from ..services.renderer import get_rendered_image

router = APIRouter()


@router.get("/patients")
def list_patients():
    """List unique patients from studies."""
    client = get_dicom_client()
    studies = client.search_for_studies()

    patients = {}
    for study in studies:
        pid = study.get("00100020")  # PatientID
        if not pid:
            continue
        if pid not in patients:
            patients[pid] = {
                "id": pid,
                "name": study.get("00100010"),
                "age": study.get("00101010"),
            }
    return list(patients.values())


@router.get("/patients/{patient_id}/instances")
def list_instances(patient_id: str):
    """Return SOP Instance UIDs for a patient."""
    client = get_dicom_client()
    instances = client.search_for_instances({"PatientID": patient_id})

    uids = [inst.get("00080018") for inst in instances]
    return [uid for uid in uids if uid]


@router.get("/patients/{patient_id}/instances/{sop_id}/render")
def render_instance(patient_id: str, sop_id: str):
    """Return rendered PNG bytes for an instance."""
    image = get_rendered_image(patient_id, sop_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

