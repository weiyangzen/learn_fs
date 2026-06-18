# sources/storage-engines/tikv/components/sst_importer/Cargo.toml

Purpose: manifest for the SST importer crate, which handles SST upload/download, caching, import-mode switching, writing, ingestion, metrics, and errors.

Important APIs and dependencies: package `sst_importer`, edition 2021, unpublished. Features include test engine selections and failpoints. Dependencies cover API version handling, storage engines, encryption, external storage, file system, grpc/protobuf, metrics, online config, futures/tokio, txn types, UUIDs, and TiKV utilities.

Control flow and integration: the dependency graph supports both local upload/import and remote external-storage download/apply flows. Dev dependencies include test engines, importer test utilities, async compression, tempfile, and tokio-util.

State and persistence behavior: manifest only, but feature choices affect tests and engine backends.

Risks: broad workspace integration means dependency/version changes can affect importer behavior across storage, encryption, API-version, and gRPC boundaries.

Test signals: source modules contain extensive unit/integration tests; this subset includes tests for caching, import files, and import mode.
