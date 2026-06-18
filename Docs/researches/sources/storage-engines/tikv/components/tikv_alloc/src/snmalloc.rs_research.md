# sources/storage-engines/tikv/components/tikv_alloc/src/snmalloc.rs

## Purpose
This file selects snmalloc as the global allocator backend while reusing default allocator API fallbacks.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `snmalloc_rs::SnMalloc`, and returns that allocator from `allocator()`. There is no runtime logic beyond allocator construction.

## State, Dependencies, and Integration
The backend is selected by the `snmalloc` feature under the cfg rules in `lib.rs`. It keeps the public API compatible with jemalloc builds but does not provide profiling or detailed stats.

## Risks and Test Signals
Operational tooling expecting jemalloc stats will receive no-op values. The main validation signal is successful feature build and global allocator installation.
