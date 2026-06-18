<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual.go -->
# sources/storage-engines/pebble/internal/manual/manual.go

Purpose: defines the shared API and metrics for Pebble's manually managed byte buffers. Platform-specific allocation and freeing live in cgo and non-cgo files, while this file owns `Buf`, allocation purposes, and accounting.

Important APIs/types: `Buf` stores an `unsafe.Pointer` and length; `MakeBufUnsafe` reconstructs a `Buf` from externally retained data/length; `Data`, `Len`, and `Slice` expose the buffer. `Purpose` enumerates `BlockCacheMap`, `BlockCacheEntry`, `BlockCacheData`, `MemTable`, and `NumPurposes`. `Metrics` reports `InUseBytes` by purpose through `GetMetrics`.

Control flow and state: `recordAlloc` and `recordFree` update padded atomic counters. `recordFree` checks for negative counters under invariants, catching mismatched purpose/size frees in invariant builds. `Slice` uses `unsafe.Slice`, so callers must not call it on arbitrary or stale pointers.

Persistence and integration: state is process-local memory accounting, not durable. This file is integrated by `manual_cgo.go`, `manual_nocgo.go`, block cache, and memtable allocation paths. Risks are unsafe reconstruction, mismatched `Free`, non-GC memory visibility, and metrics representing requested bytes rather than allocator overhead or fragmentation. No direct tests are in this subset; validation is mostly from callers and invariant builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manual/manual.go -->
