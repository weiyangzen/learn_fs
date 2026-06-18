# sources/storage-engines/tikv/components/tikv_alloc/src/mimalloc.rs

## Purpose
This file selects mimalloc as the global allocator backend while reusing the default no-op observability implementation.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `mimalloc::MiMalloc`, and returns `mimalloc::MiMalloc` from `allocator()`. There is no additional control flow.

## State, Dependencies, and Integration
The backend is compiled when the `mimalloc` feature and Unix allocator cfg select it in `lib.rs`. Profiling, stats, thread accounting, and arena APIs behave like `default.rs`.

## Risks and Test Signals
The risk is that allocator replacement succeeds while TiKV-specific memory stats become unavailable. Tests would be primarily compile/link tests plus shared no-op API behavior.
