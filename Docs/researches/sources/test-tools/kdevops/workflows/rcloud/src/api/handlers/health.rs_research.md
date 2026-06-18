<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs

## Purpose
This module implements rcloud health and status HTTP handlers. It provides a minimal liveness check and a configuration status endpoint.

## Important Types and Functions
`HealthResponse` serializes `status` and `version`. `SystemStatusResponse` serializes operational metadata: status, version, kdevops root, libvirt URI, storage pool path, base images directory, and network bridge. `health_check()` returns `{"status":"healthy","version":CARGO_PKG_VERSION}`. `system_status(config)` reads `AppConfig` from Actix shared data and exposes selected fields.

## Control Flow
Both handlers log a request, construct response structs, and return `HttpResponse::Ok().json(...)`. They do not query libvirt, disk paths, or the VM manager, so they report service process health rather than full dependency health.

## State, Persistence, and Dependencies
State comes from compile-time package version and injected `web::Data<AppConfig>`. Dependencies are Actix Web, Serde, tracing, and the rcloud configuration module.

## Risks and Test Signals
The status endpoint exposes filesystem paths and libvirt URI, which is useful operationally but may be sensitive if the server is network-exposed. The health endpoint can return healthy even if libvirt or storage is broken. The existing integration test exercises `health_check` and validates `status == healthy`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/health.rs -->
