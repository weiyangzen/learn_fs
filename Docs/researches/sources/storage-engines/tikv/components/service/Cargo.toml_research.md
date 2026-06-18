# sources/storage-engines/tikv/components/service/Cargo.toml

Purpose: crate manifest for the lightweight `service` component that carries service lifecycle events and a gRPC service manager.

Important APIs and dependencies: package `service`, edition 2021, unpublished Apache-2.0 crate. Runtime dependencies are `atomic`, workspace `crossbeam`, and workspace `tikv_util`.

Control flow and integration: this manifest supports `service_event.rs` and `service_manager.rs`, which are consumed by server startup and status/control paths to pause/resume gRPC and trigger shutdown events.

State and persistence behavior: no build-time persistence beyond Cargo metadata.

Risks: the crate is intentionally tiny; dependency additions should be scrutinized because this component is imported by startup/control paths.

Test signals: no manifest-local tests.
