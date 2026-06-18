# sources/storage-engines/pebble/internal/cache/value.go

## Purpose
This file defines `Value`, the immutable reference-counted buffer stored in the block cache, and its manual/Go allocation policy.

## Important APIs, Types, And Functions
`ValueMetadataSize` reserves metadata bytes for manual allocations. `Value` contains `buf` and `refcnt`. `Alloc`, `free`, `RawBuffer`, `Truncate`, `refs`, `acquire`, `Release`, and `Free` implement ownership and access. `valueEntryCanBeGoAllocated` and `valueEntryGoAllocated` control allocation strategy.

## Control Flow
`Alloc(0)` returns nil. Nonzero allocations either allocate a Go `Value` with manually allocated backing bytes or allocate metadata and payload in one manual block. New values start with refcount 1. Cache insertion acquires another reference through entries. `Release` frees when the count reaches zero; `Free` asserts the value has not been added to the cache before releasing.

## State And Persistence Behavior
Values are in-memory only. In invariant builds, `free` poisons bytes with `0xff` and finalizers detect leaked buffers. Manual allocations use `manual.BlockCacheData`.

## Dependencies And Integration Points
The file depends on `manual`, `buildtags`, `invariants`, `refcnt`, and `entry.go`. It is the buffer type returned by `Handle.Get`, `Peek`, and read-shard miss coordination.

## Risks And Edge Cases
Risks are leaks when callers forget `Release`/`Free`, mutation after cache insertion, truncating after publication, freeing cached values, and GC invisibility with cgo/manual memory. The allocation policy ensures Go-visible references when necessary.

## Test Signals
Cache tests repeatedly allocate, set, release, evict, and free values. Finalizer and tracing builds provide stronger leak/use-after-free detection than ordinary unit tests.
