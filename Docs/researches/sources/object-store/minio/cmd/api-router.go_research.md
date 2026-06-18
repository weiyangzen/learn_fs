# sources/object-store/minio/cmd/api-router.go

## Purpose
Registers the S3-compatible HTTP API surface, shared object-layer/server accessors, rejected/not-implemented APIs, per-handler middleware flags, and CORS behavior.

## Important APIs, types, and functions
- `newHTTPServerFn`, `setHTTPServer`, `newConsoleServerFn`, `setConsoleSrv`, `newObjectLayerFn`, and `setObjectLayer` guard global pointers with `globalObjLayerMutex`.
- `objectAPIHandlers` stores an `ObjectAPI` accessor.
- `s3HFlag` controls gzip, trace-body, and throttling behavior.
- `s3APIMiddleware` wraps handlers with tracking writer, trace, gzip, max-client throttling, and API stats.
- `registerAPIRouter` wires virtual-host and path-style S3 routes.
- `corsHandler` configures CORS allowed/exposed headers and methods.

## Control flow
Router registration builds host-based routers for configured domains, with a Kubernetes exception for `minio.<domain>`, then appends a path-style bucket router. For each bucket router it registers rejected object APIs, object operations, multipart operations, tagging, retention/legal-hold, select, lambda GET, bucket configuration APIs, listing variants, delete, replication extensions, rejected bucket APIs, and legacy ListObjects V1. Root routes cover bucket listing and event listening, with default not-found/method-not-allowed handlers.

## State and persistence behavior
No durable state. It reads and writes global in-memory server/object-layer references and reads global domain/API CORS config.

## Dependencies and integration points
Depends on `minio/mux`, MinIO HTTP constants, tracing, gzip, max-client throttling, stats collection, object API handlers implemented in other files, global domain/Kubernetes config, and wildcard CORS matching.

## Risks and edge cases
Route order matters because many methods share paths and differ only by headers/query parameters. Forgetting `traceHdrsS3HFlag` on large-body handlers risks high memory usage. Host-style routing can conflict with Kubernetes service names or reserved bucket names.

## Test signals
No direct tests in this subset; behavior is exercised by higher-level S3 API tests.
