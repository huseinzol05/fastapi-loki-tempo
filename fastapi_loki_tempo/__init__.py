__version__ = '0.0.1'

import os
import logging
import json_logging
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi_loki_tempo.os_env import *
from typing import Optional


logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
logging.getLogger('uvicorn.error').propagate = False


def update_trace_id(json_log_object):
    current_span = trace.get_current_span()
    try:
        trace_id = hex(current_span.context.trace_id)[2:]
        dd_trace_id = str(current_span.context.trace_id & 0xFFFFFFFFFFFFFFFF)
    except Exception as e:
        trace_id = None
        dd_trace_id = None

    json_log_object.update({
        'traceID': trace_id,
        'trace_message': f'traceID={trace_id}',
        'dd.trace_id': dd_trace_id,
    })


class JSONLogWebFormatter(json_logging.JSONLogFormatter):
    def _format_log_object(self, record, request_util):
        json_log_object = super(JSONLogWebFormatter, self)._format_log_object(record, request_util)
        if 'correlation_id' not in json_log_object:
            json_log_object.update({
                'correlation_id': request_util.get_correlation_id(within_formatter=True),
            })
        update_trace_id(json_log_object)
        return json_log_object


class JSONRequestLogFormatter(json_logging.JSONRequestLogFormatter):
    def _format_log_object(self, record, request_util):
        json_log_object = super(
            JSONRequestLogFormatter,
            self)._format_log_object(
            record,
            request_util)
        update_trace_id(json_log_object)
        return json_log_object


class RequestContextLogMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):

        response = await call_next(request)
        correlation_id = json_logging.get_correlation_id(request=request)
        response.headers['X-Correlation-ID'] = correlation_id
        return response


def patch(
    app,
    service_name: str = SERVICE_NAME,
    otlp_endpoint: Optional[str] = OTLP_ENDPOINT,
    jaeger_host: Optional[str] = JAEGER_HOST,
    jaeger_port: Optional[int] = JAEGER_PORT,
    tracing_sample: Optional[float] = TRACING_SAMPLE,
):
    """
    Add OpenTelemetry tracing for FastAPI app.

    Parameters
    ----------
    app: fastapi.FastAPI object
    service_name: str, optional (default=os.environ.get('SERVICE_NAME', 'fastapi'))
        service name for tracing.
    otlp_endpoint: Optional[str], optional (default=os.environ.get('OTLP_ENDPOINT', None))
        if not None, will add OTLP exporter for tracing.
    jaeger_host: Optional[str], optional (default=os.environ.get('JAEGER_HOST', None))
        if not None, will add Jaeger exporter for tracing.
    jaeger_port: Optional[int], optional (default=int(os.environ.get('JAEGER_PORT', 6831)))
        Jaeger port for `jaeger_host`.
    tracing_sample: Optional[float], optional (default=float(os.environ.get('TRACING_SAMPLE', 1.0)))
        Read more at https://opentelemetry.io/docs/concepts/sampling/
    """

    if not 0 < tracing_sample <= 1:
        raise ValueError('`tracing_sample` must, 0 < `tracing_sample` <= 1')

    if otlp_endpoint is None and jaeger_host is None:
        raise ValueError('must set `otlp_endpoint` or `jaeger_host`.')

    if otlp_endpoint and jaeger_host:
        raise ValueError('cannot set `otlp_endpoint` and `jaeger_host` at the same time.')

    json_logging.CREATE_CORRELATION_ID_IF_NOT_EXISTS = True
    json_logging.init_fastapi(enable_json=True, custom_formatter=JSONLogWebFormatter)
    json_logging.init_request_instrument(app, custom_formatter=JSONRequestLogFormatter)
    logger.handlers = logging.getLogger('json_logging').handlers

    app.add_middleware(RequestContextLogMiddleware)
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({'service.name': service_name})
        )
    )
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        logger.info({'message': f'Enable OTLP at {otlp_endpoint}'})

    if jaeger_host:
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=int(jaeger_port),
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        logger.info({'message': f'Enable Jaeger at {jaeger_host}:{jaeger_port}'})

    FastAPIInstrumentor.instrument_app(app)
