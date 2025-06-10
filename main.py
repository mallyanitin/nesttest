"""Entry point for the FastAPI DICOMweb proxy."""

import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from uvicorn import run

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api import patients
from services.dicom_client import get_settings

import json
from typing import Iterable


class FileSpanExporter(SpanExporter):
    """Custom span exporter writing spans to a file."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._file = open(file_path, "a")

    def export(self, spans: Iterable[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            ctx = span.get_span_context()
            data = {
                "name": span.name,
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
                "start": span.start_time,
                "end": span.end_time,
                "status": span.status.status_code.name,
            }
            self._file.write(json.dumps(data) + "\n")
        self._file.flush()
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self._file.close()


def configure_logging() -> None:
    """Configure application logging."""
    log_file = os.getenv("LOG_FILE", "app.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    handlers = [logging.StreamHandler()]
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=3)
    handlers.append(file_handler)

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=handlers)


def configure_tracing() -> None:
    """Set up OpenTelemetry tracing exporters."""
    resource = Resource.create({"service.name": "dicomweb-proxy"})
    provider = TracerProvider(resource=resource)

    # Console exporter
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    # File exporter
    otel_file = os.getenv("OTEL_TRACE_FILE", "app-otel.log")
    provider.add_span_processor(SimpleSpanProcessor(FileSpanExporter(otel_file)))

    # Optional OTLP exporter
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint and otlp_endpoint.startswith(("http://", "https://")):
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))

    trace.set_tracer_provider(provider)


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    configure_logging()
    configure_tracing()

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_class=PlainTextResponse)
    def health() -> str:
        return "ok"

    app.include_router(patients.router)
    FastAPIInstrumentor.instrument_app(app)
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    run("main:app", host="0.0.0.0", port=8000, reload=False)

