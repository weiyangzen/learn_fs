<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/main.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/main.rs

## Purpose
This file is the rcloud binary entry point. It configures logging, loads kdevops-derived configuration, constructs shared Actix application state, registers routes, and starts the HTTP server.

## Important APIs and Functions
`main()` uses `#[actix_web::main]`. It builds a JSON `tracing_subscriber` with INFO level, target disabled, thread IDs and file/line enabled. It calls `AppConfig::load()`, creates `web::Data<AppConfig>` and `web::Data<Metrics>`, and starts an `HttpServer` with logger, compression, tracing middleware, and `configure_routes`.

## Control Flow
Startup is linear: initialize tracing, load config, log key paths, clone bind address and worker count, build shared state, initialize metrics, then bind and run the server. Each Actix worker gets an app instance with cloned data handles.

## State, Persistence, and Dependencies
The process stores config and metrics in memory. Persistent VM state remains outside this file in libvirt and disk storage. Dependencies include Actix Web, tracing, the local API/config/metrics/vm modules, and the OS socket bind.

## Risks and Test Signals
`AppConfig::load().expect(...)` makes configuration errors fatal panics rather than formatted startup errors. The service starts successfully even if libvirt/storage are unavailable until a VM endpoint is used. Test signals include successful bind in deployment, `check-health.py`, and Actix route integration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/main.rs -->
