# fastapi-loki-tempo

FastAPI boilerplate for Loki and Tempo. 

Loki and Tempo is a very useful Open Source stack to combine logging + tracing.

## What is this?

1. Will convert all logs from `logging` module into json format, and each logs contain tracing ID,

```json
{"written_at": "2023-10-01T15:16:27.952Z", "written_ts": 1696173387952311000, "msg": "I sleep for 0.23938469734819534 seconds", "type": "log", "logger": "root", "thread": "MainThread", "level": "INFO", "module": "app", "line_no": 23, "correlation_id": "7e2b2e38-606d-11ee-80fc-6905893e1fcd", "traceID": "2a8642fab4a4c6e22224ca24e8815670", "trace_message": "traceID=2a8642fab4a4c6e22224ca24e8815670", "dd.trace_id": "2460313556319557232"}
```

2. Support Loki tracing message `traceID=`, so this allow the users correlate Loki with Tempo.

## Installation

```bash
pip3 install git+https://github.com/huseinzol05/fastapi-loki-tempo
```

## how to

Simple as,

```python
import fastapi_loki_tempo
from fastapi import Request, FastAPI

app = FastAPI()
fastapi_loki_tempo.patch(app=app)
```

```python
def patch(
    app,
    service_name: str = SERVICE_NAME,
    otlp_endpoint: Optional[str] = OTLP_ENDPOINT,
    jaeger_host: Optional[str] = JAEGER_HOST,
    jaeger_port: Optional[int] = JAEGER_PORT,
    tracing_sample: Optional[float] = TRACING_SAMPLE,
    enable_prometheus_metrics = Optional[float] = ENABLE_PROMETHEUS_METRICS,
    enable_scalar_doc: Optional[bool] = ENABLE_SCALAR_DOC,
    scalar_doc_endpoint: Optional[str] = SCALAR_DOC_ENDPOINT
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
    enable_prometheus_metrics: Optional[float], optional (default=float(os.environ.get('TRACING_SAMPLE', 1.0)))
        Enable Prometheus metrics using https://github.com/trallnag/prometheus-fastapi-instrumentator
    """
```

Run FastAPI,

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 7070
```

## Example

1. Run Grafana stack,

```bash
docker-compose -f grafana/docker-compose.yaml up --build
```

- Will forward GRPC OTLP at port `4317`.
- Will forward Jaeger UDP at port `6831`.

2. Run FastAPI,

Using OTLP,

```bash
OTLP_ENDPOINT=http://localhost:4317 uvicorn app:app --reload --host 0.0.0.0 --port 7072
```

Using Jaeger,

```bash
JAEGER_HOST=localhost JAEGER_PORT=6831 uvicorn app:app --reload --host 0.0.0.0 --port 7072
```

3. Request API at http://localhost:7072/random

```bash
curl -X 'GET' \
  'http://localhost:7072/random?minimum=0.1&maximum=2' \
  -H 'accept: application/json'
```

```json
{"written_at": "2023-10-01T15:16:27.952Z", "written_ts": 1696173387952311000, "msg": "I sleep for 0.23938469734819534 seconds", "type": "log", "logger": "root", "thread": "MainThread", "level": "INFO", "module": "app", "line_no": 23, "correlation_id": "7e2b2e38-606d-11ee-80fc-6905893e1fcd", "traceID": "2a8642fab4a4c6e22224ca24e8815670", "trace_message": "traceID=2a8642fab4a4c6e22224ca24e8815670", "dd.trace_id": "2460313556319557232"}
{"written_at": "2023-10-01T15:16:28.192Z", "written_ts": 1696173388192492000, "type": "request", "correlation_id": "7e2b2e38-606d-11ee-80fc-6905893e1fcd", "remote_user": "-", "request": "/random", "referer": "http://localhost:7072/docs", "x_forwarded_for": "-", "protocol": "HTTP/1.1", "method": "GET", "remote_ip": "127.0.0.1", "request_size_b": -1, "remote_host": "127.0.0.1", "remote_port": 59378, "request_received_at": "2023-10-01T15:16:27.951Z", "response_time_ms": 240, "response_status": 200, "response_size_b": "51", "response_content_type": "application/json", "response_sent_at": "2023-10-01T15:16:28.192Z", "traceID": "2a8642fab4a4c6e22224ca24e8815670", "trace_message": "traceID=2a8642fab4a4c6e22224ca24e8815670", "dd.trace_id": "2460313556319557232"}
```

You can check Jaeger UI at http://localhost:16686,

<img src="jaeger.png" width="800px">
