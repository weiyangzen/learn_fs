<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs

## Purpose
This module registers all HTTP routes for the rcloud service.

## Important APIs
`configure_routes(cfg)` installs an `/api/v1` scope with health, status, VM lifecycle, and image endpoints, plus a top-level `/metrics` route outside the versioned API scope.

## Control Flow
The function mutates Actix `ServiceConfig`. It binds `/api/v1/health`, `/api/v1/status`, `/api/v1/vms` for POST and GET, `/api/v1/vms/{id}` for GET and DELETE, `/api/v1/vms/{id}/start`, `/api/v1/vms/{id}/stop`, `/api/v1/images`, and `/metrics`.

## State, Persistence, and Dependencies
No state is stored here. It depends on handler module exports and Actix Web's routing DSL. Request state comes from `AppConfig` and `Metrics` app data inserted by `main.rs`.

## Risks and Test Signals
There is no authentication or authorization middleware on any route. Route order is straightforward and unlikely to conflict, but `/metrics` being unversioned and unauthenticated may expose operational data. Tests should initialize an Actix app with `configure_routes` and verify route availability and method handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/routes.rs -->
