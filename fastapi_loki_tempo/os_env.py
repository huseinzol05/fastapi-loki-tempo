import os

SERVICE_NAME = os.environ.get('SERVICE_NAME', 'fastapi')

OTLP_ENDPOINT = os.environ.get('OTLP_ENDPOINT', None)

JAEGER_HOST = os.environ.get('JAEGER_HOST', None)
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))

TRACING_SAMPLE = float(os.environ.get('TRACING_SAMPLE', 1.0))

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

ENABLE_SCALAR_DOC = os.environ.get('ENABLE_SCALAR_DOC', 'true').lower() == 'true'
SCALAR_DOC_ENDPOINT = os.environ.get('SCALAR_DOC_ENDPOINT', '/scalar')
