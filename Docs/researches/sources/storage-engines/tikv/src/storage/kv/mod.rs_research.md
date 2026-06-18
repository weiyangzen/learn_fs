# sources/storage-engines/tikv/src/storage/kv/mod.rs

## Purpose

This module is the storage KV facade. It re-exports `tikv_kv` and exposes the local `TestEngineBuilder` used by tests.

## Important APIs, Types, And Functions

`pub use tikv_kv::*` makes TiKV KV engine traits, types, and helpers available through `crate::storage::kv`. `mod test_engine_builder` declares the local test builder. `pub use test_engine_builder::TestEngineBuilder` exposes it.

## Control Flow

There is no runtime logic. This is import/export wiring.

## State And Persistence Behavior

No state is stored in this module.

## Dependencies And Integration Points

This facade connects the storage module namespace to the external/internal `tikv_kv` crate and the RocksDB test-engine builder.

## Risks And Edge Cases

Because it glob re-exports `tikv_kv`, namespace changes in that crate can affect downstream imports through `storage::kv`. The local builder is always compiled as part of the module, though it is test-oriented.

## Test Signals

Behavior is covered through modules importing `storage::kv` and through `test_engine_builder.rs` tests.
