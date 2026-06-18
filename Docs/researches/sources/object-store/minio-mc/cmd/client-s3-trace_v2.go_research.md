# sources/object-store/minio-mc/cmd/client-s3-trace_v2.go

## Purpose

`client-s3-trace_v2.go` implements debug HTTP tracing for S3 signature v2 clients. It lets mc dump request and response headers without exposing v2 access keys or signatures.

## Important APIs, Control Flow, And State

`traceV2` satisfies the `httptracer.HTTPTracer` interface. `newTraceV2` constructs it. `Request` saves the original `Authorization` header, replaces it with a redacted v2 form, dumps outbound headers with `httputil.DumpRequestOut`, writes the trace through `console.Debug`, and restores the original header before the request proceeds. `Response` dumps response headers for success and includes the body for non-OK/non-partial/non-no-content statuses; it also prints TLS certificate information when present.

## Dependencies, Integration, Risks, And Tests

The tracer is installed by `Config.initTransport` when debug is enabled and the configured signature is S3v2. Dependencies are `net/http`, `httputil`, `strings`, `httptracer`, and console debug output. Risks are accidental body logging for error responses and incomplete redaction if future v2 authorization formats change. Test coverage is indirect through debug transport construction and STS/S3 client tests.
