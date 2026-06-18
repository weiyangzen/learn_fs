<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/Cargo.toml -->
# sources/object-store/garage/src/web/Cargo.toml

## Purpose
Cargo manifest for `garage_web`, the crate implementing Garage's S3 website endpoint.

## Important APIs, types, and functions
Declares `lib.rs` and workspace dependencies on API common/S3/model/util/table crates plus HTML escaping, percent encoding, HTTP/hyper, Tokio, tracing, thiserror, and OpenTelemetry.

## Control flow
Cargo compiles the web crate against shared Garage crates and applies workspace lints.

## State and persistence behavior
No runtime state. Dependency choices determine web server request handling, S3 object reads, CORS, routing, and telemetry behavior.

## Dependencies and integration points
Integrates the web endpoint with Garage S3 API internals and model tables. Version changes in `hyper`/`http-body-util` can affect response body plumbing.

## Risks and test signals
Manifest drift can break compatibility with shared API error/body types. Build and `web_server.rs` unit tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/Cargo.toml -->
