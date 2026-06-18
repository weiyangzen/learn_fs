# sources/storage-engines/tikv/components/tikv_kv/Cargo.toml

## Purpose
This manifest defines `tikv_kv`, the key-value abstraction layer directly used by TiKV. It ties together engine traits, raftstore test engines, RocksDB engine support, transaction key types, metrics, logging, and async primitives.

## Important APIs, Types, and Control Flow
Default features enable RocksDB KV test engine and raft-engine raft test engine through `raftstore`. Additional feature flags select RocksDB test engines, panic engines, or failpoints. Runtime dependencies include `engine_traits`, `engine_rocks`, `engine_panic`, `raftstore`, `kvproto`, `txn_types`, `futures`, `prometheus`, `tikv_util`, and logging/error crates.

## State, Dependencies, and Integration
This crate sits between TiKV's storage logic and concrete engine implementations. The manifest shows integration with raftstore, PD client, filesystem abstractions, and metrics, indicating that code in this crate must remain generic over snapshot and iterator traits while supporting real RocksDB and test engines.

## Risks and Test Signals
Feature combinations determine which engines are available for tests. Failpoint support is optional. Dev dependencies on `keys` and `panic_hook` support cursor and engine behavior tests.
