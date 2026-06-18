# sources/object-store/minio/cmd/routers.go

## Purpose
This file composes MinIO's HTTP server router and distributed erasure internode routes.

## Important APIs, Types, and Functions
`registerDistErasureRouters` registers storage REST, peer REST, bootstrap, namespace lock handlers, and grid routes when running distributed erasure. `globalMiddlewares` defines the common middleware chain: custom headers, tracing, auth, browser redirects, cross-domain policy, request limits, request validity, upload forwarding, and bucket forwarding. `configureServerHandler` builds the mux router, registers admin, health, metrics, STS, KMS, and S3 API routers, and applies middlewares.

## Control Flow and State
Router setup is conditional on `globalIsDistErasure` for internode paths, then unconditionally adds public/admin service routers. The mux is configured with `SkipClean(true)` and encoded path support to preserve S3 object key semantics.

## Dependencies and Integration Points
This file integrates peer REST handlers from this subset, storage REST, lock REST, bootstrap handlers, grid managers, admin middleware, and all HTTP API routers.

## Risks and Test Signals
Middleware order is security- and observability-sensitive: tracing must see early returns, auth must run before handlers, and forwarding must occur after validity checks. Path normalization settings are critical for object key compatibility. Route coverage is likely integration-level through API/admin/router tests.
