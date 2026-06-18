# sources/object-store/garage/src/api/admin/lib.rs

Purpose: crate root for the Garage Admin API server. It declares module boundaries, exports the server type, and defines the common authorization and request-handler abstractions used throughout admin modules.

Important APIs/types: exports `api_server::AdminApiServer` as `Admin`; defines `Authorization::{None, MetricsToken, AdminToken}`; defines trait `RequestHandler` with associated `Response` and an async-returning `handle(self, &Arc<Garage>, &Admin)` method. It publicly exposes `api`, `api_server`, and `openapi`, and keeps routers/domain modules private.

Control flow and state: no runtime state is stored here. The trait is the dispatch contract consumed by macros in `macros.rs` and by `api_server.rs`. Module declarations cause handler impls to be linked for tokens, buckets, cluster, layout, block, node, repair, worker, and special endpoints.

Dependencies/integration: depends on `tracing` macros via `#[macro_use] extern crate tracing`, `Arc`, and `garage_model::garage::Garage`. It is the top-level integration point for generated routers/OpenAPI and all endpoint modules.

Risks: adding a new endpoint requires coordinated changes across this module list, `api.rs` endpoint macros, routers/OpenAPI, and a `RequestHandler` impl. The trait uses `impl Future + Send`, so handler futures must remain sendable; non-Send captured state would fail compilation.

Test signals: compile tests are primary. Add endpoint smoke tests when introducing modules to ensure the macro-generated dispatch sees the handler impl and the endpoint is exported through router/OpenAPI as expected.
