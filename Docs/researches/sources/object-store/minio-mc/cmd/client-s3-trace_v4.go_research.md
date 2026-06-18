# sources/object-store/minio-mc/cmd/client-s3-trace_v4.go

## Purpose

`client-s3-trace_v4.go` implements debug tracing for S3 signature v4 clients. It redacts authorization credentials and SSE-C key headers before dumping HTTP traffic.

## Important APIs, Control Flow, And State

`traceV4` satisfies `httptracer.HTTPTracer`; `newTraceV4` returns a value instance. `Request` captures the original authorization and SSE-C customer key headers, redacts the SSE-C key, uses regex replacement to hide the access key inside `Credential=.../` and the hex `Signature=...`, dumps headers, then restores the original authorization. `Response` mirrors v2 tracing: successful responses dump headers only, error-like responses dump body too, and TLS certificate details are printed when available.

## Dependencies, Integration, Risks, And Tests

`Config.initTransport` installs this tracer for debug S3v4 clients. Dependencies include `httputil`, `regexp`, `strings`, `httptracer`, and console debug. Risks are regex drift as authorization formats evolve, error-body leakage in debug logs, and the SSE-C header being restored only indirectly by the request object lifecycle rather than explicitly. Test signals are indirect through debug-enabled S3/admin tests.
