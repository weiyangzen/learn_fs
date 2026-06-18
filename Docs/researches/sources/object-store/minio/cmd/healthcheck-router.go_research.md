<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-router.go -->
# sources/object-store/minio/cmd/healthcheck-router.go

## Purpose
Registers MinIO health check routes under the reserved `/minio/health` path prefix.

## Important APIs, types, and functions
- Constants define `/health`, `/live`, `/ready`, `/cluster`, `/cluster/read`, and the full `/minio/health` prefix.
- `registerHealthCheckRouter` attaches GET and HEAD handlers for cluster, cluster-read, liveness, and readiness checks.

## Control flow
The function creates a subrouter from `router.PathPrefix(healthCheckPathPrefix)` and binds each endpoint/method pair to the corresponding handler wrapped by `httpTraceAll`.

## State and persistence behavior
No persistent state. It mutates the provided mux router during server setup.

## Dependencies and integration points
Depends on `github.com/minio/mux`, standard HTTP methods, route constants shared with request classifiers, health handlers from `healthcheck-handler.go`, and tracing middleware.

## Risks and edge cases
Route constants must remain in sync with `guessIsHealthCheckReq`; otherwise middleware may mishandle health calls. Only GET and HEAD are registered, so other methods fall through to generic error handling.

## Test signals
No direct tests in this group. Signals are router integration tests that verify `/minio/health/live`, `/ready`, `/cluster`, and `/cluster/read` reach the expected handlers for GET and HEAD.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/healthcheck-router.go -->
