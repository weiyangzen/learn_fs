# Research: sources/storage-engines/rocksdb/include/rocksdb/io_dispatcher.h

## Purpose

`io_dispatcher.h` declares RocksDB's experimental block-read dispatch control plane. It lets callers submit a set of block handles for a `BlockBasedTable`, receive a `ReadSet`, and later read blocks by original index or file offset while the implementation decides whether each block came from cache, asynchronous I/O, pending prefetch, or a synchronous fallback read.

## Important APIs, Types, and Functions

The header exposes `IODispatcherOptions`, `JobOptions`, `IOJob`, `ReadSet`, `IODispatcher`, `NewIODispatcher()`, `NewIODispatcher(const IODispatcherOptions&)`, and `TrackingIODispatcher`. `IODispatcherOptions::max_prefetch_memory_bytes` bounds prefetched block memory across read sets, and `statistics` enables memory-limiter counters. `JobOptions` carries the read options, I/O coalescing threshold, and the `block_handles_are_sorted` optimization. `IOJob` binds block handles to a `BlockBasedTable`. `ReadSet` exposes `ReadIndex`, `ReadOffset`, `ReleaseBlock`, `IsBlockAvailable`, and sync/async/cache-hit counters. Internally it tracks pinned blocks, sorted block indices, async state, pending prefetch flags, and dispatcher memory-budget references. `TrackingIODispatcher` wraps another dispatcher and aggregates `ReadSet` counters for tests.

## Control Flow

Callers build an `IOJob`, call `IODispatcher::SubmitJob`, and receive a shared `ReadSet` on success. Submit logic is implemented out of line in `util/io_dispatcher_imp.cc`; the header contract shows the intended sequence: cache lookup and block pinning first, asynchronous coalesced reads where possible, queued pending prefetch when memory is exhausted, and synchronous reads from `ReadIndex` or `ReadOffset` when data was not ready. `ReadOffset` uses a sorted index for lookup by block offset, while `ReadIndex` addresses the original manifest order.

## State and Persistence Behavior

The API does not persist metadata. Runtime state is held in `ReadSet`: pinned cache entries, async I/O handles, pending-prefetch membership, block-size accounting, and atomics for read statistics. `ReadSet` is non-copyable and non-movable, and its destructor has RAII responsibility for aborting active I/O and releasing pinned blocks. `ReleaseBlock` eagerly drops a block and releases prefetch memory; after that, reads for the same block should fail.

## Dependencies and Integration Points

The header depends on RocksDB options/status APIs plus internal table, block, cache, file-system, and async-I/O types. Usage searches show concentrated coverage in `util/io_dispatcher_test.cc`, integration with `BlockBasedTable`, block-cache memory allocation, read-scoped block buffer providers, and `MultiScan`. HISTORY entries mention recent fixes for memory accounting leaks and MultiScan fallback behavior, which indicates the API is actively evolving.

## Risks and Edge Cases

The interface is explicitly experimental. Memory limiting is subtle: a block read out of a `ReadSet` must still release its prefetch budget, and the HISTORY notes a past leak in this area. Incorrectly setting `block_handles_are_sorted` can cause skipped defensive sorting and wrong offset behavior. Asynchronous I/O handles must be deleted exactly once, including abort paths and coalesced requests shared by several block indices. `ReleaseBlock` invalidates later reads, so callers must avoid retaining stale indexes as if data remained available.

## Test Signals

Primary signals are `util/io_dispatcher_test.cc` tests for basic SST reads, cache hits, read-scoped providers, direct I/O scratch, statistics tracking, coalescing, sorted-handle optimization, invalid read-scoped leases, `ReadSet` destruction unpinning, memory-limit blocking/partial prefetch, and MultiScan integration. Useful assertions include sync/async/cache-hit counter values, pinned block-cache usage before and after `ReadSet` lifetime, I/O request details, and memory-limiter statistics.
