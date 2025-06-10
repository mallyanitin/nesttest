import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


@pytest.fixture
def mock_client():
    with patch("services.dicom_client.get_dicom_client") as mock:
        yield mock


def test_list_patients(mock_client):
    mock_instance = MagicMock()
    mock_instance.search_for_studies.return_value = [
        {"00100020": "P1", "00100010": "John", "00101010": "030Y"},
        {"00100020": "P2", "00100010": "Alice", "00101010": "025Y"},
    ]
    mock_client.return_value = mock_instance

    response = client.get("/patients")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "P1", "name": "John", "age": "030Y"},
        {"id": "P2", "name": "Alice", "age": "025Y"},
    ]


def test_list_instances(mock_client):
    mock_instance = MagicMock()
    mock_instance.search_for_instances.return_value = [
        {"00080018": "1"},
        {"00080018": "2"},
    ]
    mock_client.return_value = mock_instance

    response = client.get("/patients/P1/instances")
    assert response.status_code == 200
    assert response.json() == ["1", "2"]


def test_render_instance(mock_client):
    mock_instance = MagicMock()
    mock_instance.search_for_instances.return_value = [
        {"0020000D": "study1", "0020000E": "series1"}
    ]
    mock_instance.retrieve_instance_rendered.return_value = b"data"
    mock_client.return_value = mock_instance

    response = client.get("/patients/P1/instances/1/render")
    assert response.status_code == 200
    assert response.content == b"data"

