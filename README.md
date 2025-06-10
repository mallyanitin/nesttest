# DICOMweb Proxy

This project provides a FastAPI based proxy for a DICOMweb server. It exposes simple endpoints to list patients, retrieve instances and render images.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with:

```
DICOMWEB_URL=http://your.dicom.server
DICOMWEB_USER=user
DICOMWEB_PASS=pass
```

## Run Locally

```bash
uvicorn main:app --reload
```

## Docker

Build and run the container:

```bash
docker build -t dicomweb-proxy .
docker run -p 8000:8000 dicomweb-proxy
```

## Tests

Run unit tests:

```bash
pytest
```

Run BDD tests (requires Docker):

```bash
behave
```

