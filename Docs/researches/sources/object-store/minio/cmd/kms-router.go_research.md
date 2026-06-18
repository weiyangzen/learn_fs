# sources/object-store/minio/cmd/kms-router.go

## Purpose

`kms-router.go` registers MinIO's KMS API routes below the reserved `/minio/kms/v1` prefix. It binds HTTP methods and paths to the handlers in `kms-handlers.go`, applies tracing and gzip compression, and installs default not-found/method-not-allowed handlers.

## Important APIs, Control Flow, And State

The constants `kmsPathPrefix`, `kmsAPIVersion`, and `kmsAPIVersionPrefix` define the public route namespace. `kmsAPIHandlers` is an empty receiver type used to group handler methods. `registerKMSRouter` creates a subrouter from the supplied `mux.Router`, initializes a `gzhttp` wrapper with minimum size 1000 and `gzip.BestSpeed`, and fatal-exits on wrapper initialization failure. For each version currently listed, it registers GET routes for `/status`, `/metrics`, `/apis`, `/version`, POST `/key/create` requiring a `key-id` query, GET `/key/list` requiring a `pattern` query, and GET `/key/status`. Each concrete handler is wrapped as `gz(httpTraceAll(...))`.

This file has no persistent state of its own. It integrates with the global HTTP router startup path, `github.com/minio/mux`, `httpTraceAll`, KMS handler methods, and shared error handlers.

## Risks And Test Signals

Route shape is the main risk: `key/create` and `key/list` use `Queries(...)`, so missing query keys may miss the route and fall into default error handling rather than handler-level validation. Compression wrapping changes response behavior for larger JSON bodies and must remain compatible with tracing. `kms-handlers_test.go` registers this router in the testbed and exercises the declared routes, including query-bearing key APIs.
