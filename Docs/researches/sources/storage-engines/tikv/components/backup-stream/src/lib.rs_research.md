# sources/storage-engines/tikv/components/backup-stream/src/lib.rs

## Purpose
`lib.rs` is the crate root for TiKV backup stream. It declares internal and public modules, enables required nightly features, and re-exports the public construction and service types used by other TiKV components and integration tests.

## Important APIs, types, and functions
- Public modules: `config`, `errors`, `metadata`, `metrics`, `observer`, `router`, and `utils`.
- Private modules: `checkpoint_manager`, `endpoint`, `event_loader`, `service`, `subscription_manager`, `subscription_track`, and `tempfiles`.
- Re-exports: `GetCheckpointResult`, `BackupStreamResolver`, `Endpoint`, `ObserveOp`, `RegionCheckpointOperation`, `RegionSet`, `Task`, and `BackupStreamGrpcService`.

## Control flow
There is no runtime control flow in this file. It controls compile-time visibility and the public crate surface.

## State and persistence behavior
No state is held here. Persistence and runtime state are delegated to the modules it declares.

## Dependencies and integration points
The crate uses `#![feature(trait_alias)]` and `#![feature(test)]`, indicating nightly-only compilation. Re-exporting endpoint and service types makes this root the integration boundary for server setup, gRPC service wiring, and integration tests.

## Risks and edge cases
- Changing module visibility affects integration tests and downstream TiKV components.
- Publicly exporting `utils` for integration tests is called out as a temporary or imperfect boundary.

## Test signals
No direct tests. Compilation of downstream module tests validates that the root exports remain sufficient.
