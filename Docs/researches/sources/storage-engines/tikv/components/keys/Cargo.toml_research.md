# sources/storage-engines/tikv/components/keys/Cargo.toml

## Purpose
This manifest defines the private `keys` crate, which centralizes TiKV key-prefix constants, region/raft key encoding helpers, data key helpers, and prefix rewriting utilities.

## Important APIs, Types, and Functions
The manifest declares runtime dependencies on `byteorder`, `kvproto`, `log_wrappers`, `thiserror`, `tikv_alloc`, and `tikv_util`; dev tests depend on `panic_hook`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest itself has no state, but it supports code that defines persisted RocksDB key layouts.

## Dependencies and Integration Points
`byteorder` is required for big-endian sortable ids, `log_wrappers` redacts/hex-encodes keys in errors, and `kvproto` supplies region metadata.

## Risks
Changing dependency versions here can affect low-level storage key formatting and test behavior. Because this crate sits on a performance-critical path, adding heavy dependencies should be avoided.

## Test Signals
Tests are in `src/lib.rs` and `src/rewrite.rs`; the manifest has no independent tests.
