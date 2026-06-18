## sources/object-store/minio-mc/pkg/httptracer/httptracer.go

Purpose: provides an `http.RoundTripper` wrapper that invokes request/response trace hooks and logs response time in debug output. Important surfaces are `HTTPTracer`, `RoundTripTrace`, `RoundTrip`, and `GetNewTraceTransport`.

Control flow records start time, rejects nil underlying transports, delegates `RoundTrip`, then calls `Trace.Request(req)` and `Trace.Response(res)` if a tracer is configured. State is only wrapper configuration. Dependencies are `net/http`, `time`, `errors`, and MinIO console debug logging. Integration is with HTTP clients that need request/response tracing without changing transport users. Risks include hooks being called after the response returns rather than before the request is sent, returning nil response on hook error, and response body lifetime concerns. The test file is effectively empty.
