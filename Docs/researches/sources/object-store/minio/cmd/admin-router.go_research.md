# sources/object-store/minio/cmd/admin-router.go

## Purpose
`admin-router.go` defines the versioned MinIO admin HTTP route surface and common middleware for admin handlers. It wires `/minio/admin/<version>` paths to methods on `adminAPIHandlers`, applies gzip, tracing, audit logging, and object-layer readiness checks, and conditionally registers erasure-only or config-enabled APIs.

## Important APIs, Types, And Functions
- Constants define `adminPathPrefix`, `adminAPIVersion`, `adminAPIVersionPrefix`, and special site-replication/client speedtest route suffixes.
- `gzipHandler` is a package-level gzhttp wrapper configured with minimum response size and best-speed gzip compression.
- `hFlag` and flags `noGZFlag`, `traceAllFlag`, and `noObjLayerFlag` control middleware behavior.
- `hFlag.Has` checks flag inclusion.
- `adminMiddleware` wraps each handler with request context setup, audit logging, optional object-layer availability check, trace header/body instrumentation, and optional gzip compression.
- `adminAPIHandlers` is the receiver type for all admin handler methods.
- `registerAdminRouter` creates the admin subrouter and registers all admin API routes for the configured version.

## Control Flow
`registerAdminRouter` creates a subrouter under `adminPathPrefix`, iterates the supported admin API versions, and registers routes by HTTP method, path, handler method, middleware flags, and query constraints. The router registers V2 and deprecated forms for service and update APIs; info, inspect, storage, data usage, metrics; erasure-only heal, pools, rebalance; profiling; config operations when `enableConfigOps` is true; IAM and identity provider operations; bucket quota, replication, batch, metadata, tier, site-replication, lock, speedtest, trace, log, KMS, health, and token-revocation APIs.

`adminMiddleware` is applied at registration time. At request time it attaches a new MinIO request context with handler API name, defers audit logging, checks object-layer and notification subsystem readiness unless `noObjLayerFlag` is present, wraps the handler in header-only or full request tracing based on `traceAllFlag`, and gzip-wraps the resulting handler unless `noGZFlag` is present.

After all versioned routes are registered, `NotFoundHandler` and `MethodNotAllowedHandler` are set to traced error handlers for the admin subrouter.

## State And Persistence Behavior
The file does not persist state. It constructs router registrations and a gzip wrapper at package initialization. Middleware reads global object-layer and notification subsystem readiness and writes request-scoped logging/audit state. Route availability depends on globals such as `globalIsDistErasure`, `globalIsErasure`, and the `enableConfigOps` argument.

## Dependencies And Integration Points
The router integrates with `github.com/minio/mux`, `madmin.AdminAPIVersion`, `gzhttp`, MinIO logging/audit/tracing helpers, `newObjectLayerFn`, `globalNotificationSys`, and every handler method implemented across admin-related files. It is the primary boundary between MinIO's HTTP layer and admin subsystem methods.

## Risks And Edge Cases
Because route matching uses query constraints in several places, route ordering matters for overloaded paths such as `/service`, `/update`, `/list-canned-policies`, and heal paths. Misplaced or missing middleware flags can break streaming responses (`noGZFlag`), allow handlers to run before object-layer readiness, or omit full request tracing. `noObjLayerFlag` is necessary for initialization-time diagnostics like `/info` but expands handler responsibility for nil global checks.

The route file is very broad; adding new admin APIs risks accidental mismatch between method/path/query, policy enforcement in the target handler, and middleware flags. Conditional erasure-only registration means clients may see route-not-found rather than handler-level not-implemented errors depending on deployment mode.

## Test Signals
`admin-handlers_test.go` indirectly verifies router registration for `/service?type=2` and `/info` by constructing signed requests and serving them through the mux router returned by `registerAdminRouter`. There is no exhaustive route-table test in this subset, so most route registrations rely on broader integration coverage or client compatibility tests outside these files.
