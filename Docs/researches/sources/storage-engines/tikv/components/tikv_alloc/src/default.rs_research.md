# sources/storage-engines/tikv/components/tikv_alloc/src/default.rs

## Purpose
This file supplies no-op allocator observability and profiling functions for backends that do not implement jemalloc-specific behavior. It is re-exported by system, mimalloc, snmalloc, and tcmalloc implementations.

## Important APIs, Types, and Control Flow
`dump_stats` returns an empty string, `fetch_stats` returns `Ok(None)`, profiling control functions return `ProfError::MemProfilingNotEnabled`, arena count is zero, profiling activity is false, and thread allocation-stat callbacks do nothing. `thread_allocate_exclusive_arena` returns success because non-jemalloc backends do not need arena setup. The unsafe `add_thread_memory_accessor` is intentionally harmless to match the jemalloc API shape.

## State, Dependencies, and Integration
There is no persistent state. The module depends only on `ProfError`, `ProfResult`, and `AllocStats`. It allows the public `tikv_alloc` API to remain stable regardless of selected allocator.

## Risks and Test Signals
The main risk is silent loss of observability when a non-jemalloc backend is selected: callers must handle `None`, empty strings, or profiling-not-enabled errors. This behavior is deliberate and keeps non-jemalloc builds simple.
