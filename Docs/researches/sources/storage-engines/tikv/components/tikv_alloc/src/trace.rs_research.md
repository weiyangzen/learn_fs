# sources/storage-engines/tikv/components/tikv_alloc/src/trace.rs

## Purpose
This module implements logical memory tracing as a tree of named or numeric nodes. It is independent of the global allocator backend and lets components attribute memory usage to logical subsystems rather than stack traces.

## Important APIs, Types, and Control Flow
`Id` identifies trace nodes by static name or number and provides raw and readable names. `TraceEvent` represents additive, subtractive, or reset updates and implements combination semantics where later reset events dominate. `MemoryTrace` stores an id, atomic local trace value, and child map keyed by `Id`. It can record events, create RAII guards, snapshot the tree, access subtraces, add children, compute recursive sums, and list child ids.

The exported `mem_trace!` macro constructs an `Arc<MemoryTrace>` tree from nested syntax. `MemoryTraceGuard<T>` increments a trace on creation and decrements on drop or `consume`; it derefs to the wrapped item and can map to a new wrapped type while preserving accounting.

## State, Dependencies, and Integration
Trace values are in-memory atomics with relaxed ordering. Children are immutable after setup in common use, built through `Arc::get_mut` during macro construction. The module uses `fxhash` for faster maps and is re-exported from `tikv_alloc::lib`.

## Risks and Test Signals
Risks include underflow if subtract events exceed current trace, panics on missing `sub_trace`, and stale snapshots under concurrent updates. `MemoryTraceGuard` requires `T: Default` because it moves values out via `mem::take`. Tests cover id formatting, readable names, macro tree construction and sum behavior, and `TraceEvent` combination rules.
