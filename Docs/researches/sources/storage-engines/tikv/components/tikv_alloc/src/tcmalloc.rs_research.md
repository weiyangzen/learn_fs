# sources/storage-engines/tikv/components/tikv_alloc/src/tcmalloc.rs

## Purpose
This file selects tcmalloc as the global allocator backend while reusing default allocator observability fallbacks.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `tcmalloc::TCMalloc`, and returns `tcmalloc::TCMalloc` from `allocator()`. There is no extra runtime control flow.

## State, Dependencies, and Integration
The backend is selected by the `tcmalloc` feature and uses the bundled tcmalloc dependency declared in the manifest. Public stats and profiling functions are the no-op defaults.

## Risks and Test Signals
The crate does not surface tcmalloc-specific statistics, so callers expecting jemalloc-like introspection must tolerate disabled profiling and absent stats. Build/link success is the primary backend signal.
