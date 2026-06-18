# Research: sources/storage-engines/tikv/components/test_sst_importer/Cargo.toml

## sources/storage-engines/tikv/components/test_sst_importer/Cargo.toml

Purpose: manifest for `test_sst_importer`, a private helper crate for SST importer tests. It disables library test harness generation with `[lib] test = false`, which is common for utility crates consumed by integration tests.

Dependencies show the crate's role: Rocks engine and engine traits for SST creation/readback, external storage for backup/restore style streams, futures/grpcio/kvproto for import service clients, `keys` and `txn_types` for TiKV key encoding, `tikv_util` for stream/external IO helpers, `tempfile`, `uuid` for SST metadata IDs, and `crc32fast` for upload integrity.

There is no runtime control flow in the manifest, but it wires the helpers in `src/lib.rs` and `src/util.rs` into the TiKV workspace. State and persistence are delegated to generated temp SST files, local external-storage directories, and Rocks test DBs.

Risks include dependency API drift in grpc streaming, Rocks SST writer traits, and external storage traits. Test signals are downstream SST importer tests compiling and using generated `SstMeta`, upload/write streams, ingest checks, and local storage metadata.
