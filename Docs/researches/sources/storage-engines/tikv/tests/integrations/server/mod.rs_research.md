# sources/storage-engines/tikv/tests/integrations/server/mod.rs

Purpose: wires server integration test modules and provides a helper to construct a TiKV gRPC server around any `Tikv` service implementation.

Important APIs and functions: submodules `debugger`, `gc_worker`, `kv_service`, `lock_manager`, `raft_client`, `security`, `server`, `status_server`; helper `tikv_service<T>(kv, ip, port) -> grpcio::Result<Server>` where `T: Tikv + Clone + Send + 'static`.

Control flow: `tikv_service` creates a two-thread gRPC environment, builds a default `SecurityManager`, configures channel args with two concurrent streams and unlimited message size, registers `create_tikv(kv)`, binds through security manager, and builds the server.

State and persistence: no persistence. It creates runtime gRPC server and security binding state for tests.

Dependencies and integration: generated kvproto TiKV service, `grpcio`, TiKV security config/manager, and the server integration test module tree.

Risks: default security config is unsuitable for tests that need custom TLS/security behavior; low stream limit may constrain unrelated reuse.

Test signals: compilation and downstream server tests confirm module wiring and service construction remain valid.
