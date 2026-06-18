# sources/storage-engines/pebble/internal/cache/entry.go

## Purpose
This file defines cache entry metadata, linked-list manipulation, value reference ownership, and the allocator used for CLOCK-Pro entries. Entries are the nodes stored in shard `blocks`/`files` maps and threaded through the hot/cold/test and per-file circular lists.

## Important APIs, Types, And Functions
`entryType` enumerates `etTest`, `etCold`, and `etHot`. `entry` holds `key`, `val`, block/file links, size, type, and `referenced`. `newEntry`, `free`, `next`, `prev`, `link`, `unlink`, `linkFile`, `unlinkFile`, `setValue`, and `acquireValue` manipulate node state. Allocation helpers include `entryAllocNew`, `entryAllocFree`, `entryAllocPool`, `entryAllocCache`, and its allocation/free methods.

## Control Flow
New entries start cold and self-linked in both circular lists. `link`/`unlink` maintain the global CLOCK-Pro list, while `linkFile`/`unlinkFile` maintain the per-file list. `setValue` acquires the new value before publishing it and releases the old value afterward. Allocation normally uses pooled manual memory, but invariant/finalizer or race configurations switch to Go allocation.

## State And Persistence Behavior
Entry state is volatile but memory-safety-critical. The entry holds a cache reference on `Value` and must clear it before freeing. Finalizer builds poison failures by checking that freed entries are zeroed. No disk persistence exists.

## Dependencies And Integration Points
The file depends on `manual`, `buildtags`, `invariants`, `sync.Pool`, atomics, and `unsafe`. It is tightly integrated with `clockpro.go` list operations and `value.go` allocation policy.

## Risks And Edge Cases
Risks include storing Go pointers in manually allocated memory, leaking values when replacing entries, double-free or non-zero entry reuse, and list corruption. The code carefully aligns allocation policy with whether values are Go allocated so the GC can see references when necessary.

## Test Signals
Cache tests exercise entry replacement, deletion, file eviction, and stress replacement. Invariant/finalizer builds add leak/use-after-free detection beyond ordinary tests.
