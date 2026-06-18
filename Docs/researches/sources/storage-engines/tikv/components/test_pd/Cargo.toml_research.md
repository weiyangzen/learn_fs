# sources/storage-engines/tikv/components/test_pd/Cargo.toml

## Purpose
This manifest defines the private `test_pd` crate, a gRPC-backed mock PD server library for TiKV tests.

## Dependencies And Integration Points
The crate depends on `kvproto`, `grpcio`, `pd_client`, `security`, `tikv_util`, logging crates, `fail`, `futures`, and `tokio`/`tokio-stream`. Those dependencies match its role: serve PD, MetaStorage, and resource-manager protobuf services, support TLS/security manager binding, inject failpoints, and run async streaming handlers.

## State, Persistence, And Risks
The manifest brings in full async and gRPC stacks for tests. Runtime state lives in in-memory mockers and server instances; no persistence dependencies are declared. Because this crate simulates protocol behavior, dependency/API drift in `kvproto` or `pd_client` will surface at compile time.

## Test Signals
Successful compilation validates that the mock server implements the current PD-related protobuf traits. Integration tests use this crate to verify client reconnect, leader changes, metadata storage, retry, split, and service-GC behavior.
