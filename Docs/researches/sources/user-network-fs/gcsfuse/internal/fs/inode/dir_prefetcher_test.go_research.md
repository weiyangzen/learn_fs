<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go

## Purpose

This testify suite validates directory metadata prefetch behavior, including cache warming, large-directory heuristics, concurrency limits, TTL gating, cancellation, and races with writes.

## Important APIs, Types, and Functions

`DirPrefetchTest` owns a context, syncer bucket, fake bucket, simulated clock, `*dirInode`, and config. `setup` builds a directory inode with metadata prefetch enabled or disabled. Helper callbacks include `blockingListFunc` and `mockListFuncWithCtr`. Tests directly inspect `MetadataPrefetcher` atomic state, type cache values, semaphore behavior, and cancellation effects.

## Control Flow

Tests seed directory objects, call `LookUpChild` to trigger prefetch or call `MetadataPrefetcher.Run` directly, then use `assert.Eventually`, sleeps, or blocking channels to coordinate goroutines. Some tests replace the prefetcher's list callback with custom functions that block, count calls, return stale data, or observe context cancellation.

## State and Persistence Behavior

State includes fake bucket contents, `dirInode` type cache, prefetcher atomic state, large-directory flag, last prefetch time, semaphore permits, and cancellable contexts. The suite destroys the inode in teardown, cancelling prefetch contexts. No durable files are written.

## Dependencies and Integration Points

The suite integrates `NewDirInode`, `MetadataPrefetcher`, fake GCS buckets, storage utilities, metadata type cache, simulated clock, semaphores, contexts, atomics, and testify suite/assertions. It validates the contract between `dirInode.LookUpChild`, prefetch callback cache insertion, and directory write cancellation.

## Risks and Edge Cases

Several tests are timing-sensitive and depend on goroutine scheduling. The race-with-delete test is important because stale prefetch data must not overwrite fresh cache invalidation after a write. Large-directory tests encode lexicographic start-offset behavior and max-prefetch limits.

## Test Signals

Signals include expected cache entries for sibling files/implicit dirs, unknown cache entries outside start offset or beyond max count, `prefetchReady` restoration, context cancellation, semaphore saturation, call counts, TTL-respected call suppression, no cache update after cancel, and no prefetch when inode context is nil/cancelled or active writers exist.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go -->
