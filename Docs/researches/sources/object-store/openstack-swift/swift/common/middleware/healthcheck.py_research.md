# sources/object-store/openstack-swift/swift/common/middleware/healthcheck.py

## Purpose
`healthcheck.py` provides a lightweight operational endpoint at `/healthcheck`. It returns `200 OK` with `OK` unless a configured disable file exists, in which case it returns `503` with `DISABLED BY FILE`.

## Important APIs, Types, and Functions
`HealthCheckMiddleware.GET()` returns the healthy response. `DISABLED()` returns the disabled response. `__call__()` intercepts `/healthcheck`. `filter_factory()` exposes the filter.

## Control Flow
Initialization stores an optional `disable_path`. Each request is wrapped as a `Request`; only `/healthcheck` is handled directly. If a disable path is configured and exists on disk, `DISABLED` is selected, otherwise `GET` is selected. Other paths pass through.

## State and Persistence
The only persistent signal is the operator-controlled disable file. The middleware performs a filesystem existence check per healthcheck request and stores no other state.

## Dependencies and Integration Points
It depends on `os.path.exists`, Swift `Request`, and `Response`. It is typically placed early enough that monitors do not require auth or backend availability.

## Risks and Edge Cases
Filesystem checks on every healthcheck are simple but depend on path availability and permissions. The endpoint handles `/healthcheck` regardless of method by selecting the healthy/disabled handler, so method-specific behavior should be considered by operators/tests. Missing or unreadable disable-path parents simply appear as enabled if the file does not exist.

## Test Signals
Tests should cover healthy response body/status/content type, disabled file response, pass-through for other paths, configured and empty disable paths, and method behavior for non-GET requests to `/healthcheck`.
