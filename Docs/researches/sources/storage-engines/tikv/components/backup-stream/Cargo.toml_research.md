# sources/storage-engines/tikv/components/backup-stream/Cargo.toml

## Purpose
This manifest defines the `backup-stream` component crate, which implements TiKV log backup/backup-stream services, metadata, routing, checkpointing, event loading, and integration tests.

## Important APIs, Types, And Functions
Features include default test engines, failpoints, OpenSSL vendoring for macOS/grpcio test builds, and `backup-stream-debug`. It declares integration and failpoint test targets. Dependencies cover async compression, gRPC/protobuf, external storage, encryption, engine traits/RocksDB, PD client, online config, metrics, raft/raftstore, resolved-ts, Tokio, tracing, UUID, and TiKV core crates.

## Control Flow
Cargo uses the manifest to compile the backup-stream library and its tests. The failpoint test target only builds when the `failpoints` feature is enabled.

## State And Persistence Behavior
The manifest has no runtime state, but selected features affect compiled failpoints, engine implementations, TLS/OpenSSL linkage, and available test suites.

## Dependencies And Integration Points
The crate sits at a high-integration point: storage engines, PD metadata, external storage backends, encryption, raftstore, online config, metrics, and server components all meet here. Server modules instantiate backup-stream endpoint/router/config manager.

## Risks And Edge Cases
- Large dependency surface increases build-feature interaction risk.
- Failpoint and vendored OpenSSL features change test/runtime behavior.
- Default test-engine features must stay aligned with workspace engine abstractions.

## Test Signals
The manifest declares `integration` and `failpoints` test suites. Compile coverage across default, failpoints, and OpenSSL-vendored configurations is important.
