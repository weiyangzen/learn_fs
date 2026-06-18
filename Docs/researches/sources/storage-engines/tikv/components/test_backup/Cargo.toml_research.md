# sources/storage-engines/tikv/components/test_backup/Cargo.toml

## Purpose
This manifest defines the private `test_backup` crate. It is not published and exists as shared test support for TiKV backup behavior, including cluster-backed backup endpoints, raw/txn backup validation, disk snapshot backup tests, and checksum comparisons.

## Dependencies And Integration Points
The crate depends on internal workspace crates for backup execution (`backup`), raftstore test clusters (`test_raftstore`, `raftstore`), TiKV storage and coprocessor paths (`tikv`), Rocks engine traits (`engine_rocks`, `engine_traits`), API-version encoding, external local storage, and utility workers. It also uses `kvproto` and `grpcio` to call TiKV RPCs, `tidb_query_common` to scan data, `txn_types` for timestamps, `futures` channels/executors, and `crc64fast`/`rand` for checksum and temporary directory support.

## State, Persistence, And Risks
The manifest enables real integration tests rather than lightweight unit fixtures. It pulls in RocksDB-backed engines, local external storage, gRPC clients, worker threads, and raftstore clusters, so tests using this crate are stateful and timing-sensitive. The source tree has no feature flags here, meaning dependency feature selection is inherited from workspace defaults. A small formatting issue (`external_storage ={ workspace = true }`) is syntactically valid TOML but inconsistent with surrounding style.

## Test Signals
Because this is a support crate manifest, validation is compile-time and integration-test oriented: successful builds prove that backup test helpers can link against backup, raftstore, TiKV, and protobuf APIs together.
