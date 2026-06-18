# sources/storage-engines/tikv/components/test_coprocessor/Cargo.toml

## Purpose
This manifest defines the private `test_coprocessor` crate, a shared fixture library for building TiDB DAG requests and TiKV coprocessor storage data in tests.

## Dependencies And Features
Default features forward engine selections into `test_storage`: RocksDB KV engine and raft-engine raft storage. Alternate features expose all-RocksDB and panic-engine test modes. Dependencies include `tipb` and `kvproto` protobuf types, TiDB datatype and codec crates, TiKV storage/coprocessor APIs, `test_storage`, `pd_client`, `concurrency_manager`, `resource_metering`, and utilities.

## Integration, State, And Risks
The crate is a test-only bridge between schema/request builders and real TiKV coprocessor endpoints. Its feature forwarding means test behavior depends on selected engine features, so incompatible combinations can surface as compile-time or fixture initialization failures. The crate requires Rust specialization through its source, so it is tied to nightly/feature-gated compilation used by TiKV.

## Test Signals
This manifest is validated by consumers that compile and run coprocessor tests with the desired engine feature set. Dependency drift in protobuf or TiDB datatype APIs will generally show up as builder or request-encoding compile failures.
