<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/Cargo.toml -->
# sources/storage-engines/tikv/components/external_storage/Cargo.toml

Purpose: this manifest defines the non-published `external_storage` crate, TiKV's abstraction layer for local, HDFS, S3, GCS, Azure Blob, and noop storage used by backup, restore, import, and export workflows.

Important build surface: it exposes a `failpoints` feature and an example binary `scli` at `examples/scli.rs`. Runtime dependencies include cloud provider crates (`aws`, `azure`, `gcp`, `gcp_v2`, `cloud`), `encryption`, `file_system`, protobuf definitions through `kvproto`, async libraries, `openssl`, `serde`, `tokio`, `walkdir`, and metrics through `prometheus`.

Integration points: the crate bridges TiKV BR protobuf `StorageBackend` messages to concrete storage implementations. It reuses `file_system::Sha256Reader` for encrypted checksum tracking and `encryption` for local restore encryption and remote file decryption.

State and persistence behavior: the manifest itself has no state, but it wires crates that persist local files, invoke HDFS commands, and write/read remote object storage. The selected dependencies indicate both async stream behavior and blocking file compatibility through `tokio-util`.

Risks: the crate has many optional operational dependencies and provider-specific behavior, so feature and workspace version drift can break storage creation. The example-only `structopt`, `rust-ini`, and `hyper` dev dependencies are separated from runtime dependencies.

Test signals: manifest coverage is indirect through crate tests, provider adapter compilation, and the `scli` example target.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/Cargo.toml -->
