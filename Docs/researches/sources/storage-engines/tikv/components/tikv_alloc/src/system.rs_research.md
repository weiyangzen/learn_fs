# sources/storage-engines/tikv/components/tikv_alloc/src/system.rs

## Purpose
This file selects Rust's system allocator backend and reuses the default no-op profiling/stat API.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `std::alloc::System`, and returns `std::alloc::System` from `allocator()`.

## State, Dependencies, and Integration
This backend is used when custom allocator cfgs do not apply, including non-Unix and fuzzing builds. It preserves the same public functions as other backends.

## Risks and Test Signals
System allocator behavior varies by platform, and RocksDB/C malloc replacement may differ from jemalloc builds. Memory profiling and allocator stats are unavailable through this crate in this mode.
