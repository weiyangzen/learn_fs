# sources/object-store/rustfs/crates/data-usage/src/lib.rs

## Purpose
This is the public entry point for `rustfs-data-usage`. It exposes the `data_usage` module and re-exports all of its public items for downstream crates.

## Important APIs, Types, and Functions
The file declares `pub mod data_usage;` and `pub use data_usage::*;`. This makes `DataUsageInfo`, `BucketUsageInfo`, `DataUsageCache`, histogram types, replication stats, storage traits, and helper functions available directly under `rustfs_data_usage`.

## Control Flow
There is no runtime flow. The file controls namespace shape and avoids requiring callers to import through `rustfs_data_usage::data_usage::*`.

## State and Persistence
No state is stored here. Serialization and cache persistence behavior live in `data_usage.rs`.

## Dependencies and Integration Points
E2e tests import `rustfs_data_usage::DataUsageInfo`, relying on this re-export. Other RustFS crates can use shared usage models without knowing the internal module layout.

## Risks and Edge Cases
The glob re-export exposes every public item from `data_usage.rs`; adding a new public item there automatically becomes part of the crate-level API. That is convenient but increases semver surface.

## Test Signals
No local tests are present. Coverage is indirect through `data_usage.rs` unit tests and crates that import the re-exported types.
