# sources/storage-engines/tikv/components/compact-log-backup/Cargo.toml

## Purpose
Manifest for the `compact-log-backup` workspace crate, which compacts log-backup artifacts into SST outputs and metadata migrations.

## APIs and control flow
The package is private, edition 2021, and exposes a `failpoints` feature forwarding to `fail/failpoints`. The dependency set shows the crate is asynchronous and storage-heavy: it uses external storage, cloud IO, backup-stream types, Rocks engine traits, protobuf metadata, encryption, zstd/async compression, Tokio, futures, tracing, Prometheus, and TiKV utility crates.

## State, dependencies, and integration
Runtime state is not in the manifest, but dependency wiring indicates integration with Rocks SST creation (`engine_rocks`, `engine_traits`), BR protobufs (`kvproto`), external storage, backup stream metadata, and TiKV transaction/key codecs. `zstd` is noted as test-utils-only while still in normal dependencies; `pprof`, `tempfile`, and `test_util` are dev dependencies.

## Risks and test signals
The crate depends on many workspace crates, so feature or version drift can affect compilation broadly. The `tokio` feature set includes runtime, macros, time, sync, and signal support, which implies async execution paths must be tested under runtime context. Manifest validation is compile-time plus crate test suites.
