<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go

## Purpose

This file implements `MetadataPrefetcher`, an asynchronous helper that warms directory metadata/type caches after an unknown child lookup. It is designed to improve sibling lookup performance while avoiding stale cache writes during directory lifecycle changes or active writes.

## Important APIs, Types, and Functions

Constants `prefetchReady` and `prefetchInProgress` define atomic state. `MetadataPrefetcher` stores cache TTL, atomic state, inode lifecycle context, current-run cancel function, maximum prefetch count, cache clock, last successful prefetch time, large-directory flag, shared semaphore, a list function callback, and a `shouldRun` callback.

`NewMetadataPrefetcher` wires config values and callbacks. `Run(fullObjectName string)` decides whether to start a background prefetch. `Cancel()` cancels only the current run, not the owning inode context.

## Control Flow

`Run` exits if the inode context is nil/cancelled, if `shouldRun` is false, or if the previous successful prefetch is still within TTL. It atomically switches ready to in-progress, creates a child context for the run, and launches a goroutine. The goroutine tries to acquire the shared semaphore without waiting; if unavailable it skips. It optionally uses `fullObjectName` as `StartOffset` for directories previously marked large, then pages `listCallFunc` up to `maxPrefetchCount`, respecting context cancellation before each call. If the limit is reached with a continuation token, it marks the directory large. On successful completion it records `lastPrefetchTime` and always resets state.

## State and Persistence Behavior

State is in-memory and per directory inode. It tracks current run state, cancellation function, last prefetch timestamp, and large-directory heuristic. Cache persistence is delegated to the `listCallFunc` callback, normally `dirInode.readObjectsUnlocked`, which updates metadata cache under the inode lock after checking context cancellation.

## Dependencies and Integration Points

The prefetcher integrates `cfg.MetadataCache`, inode lifecycle contexts, `timeutil.Clock`, shared `semaphore.Weighted`, `logger`, and `dirInode` listing/cache insertion via callback. `dirInode.LookUpChild` triggers it for unknown type-cache entries; directory writes call cancel/active-writer hooks to avoid stale updates.

## Risks and Edge Cases

The shared `runCancelFunc` is written without its own mutex and relies on caller-side directory locking for setup/cancel coordination. Since semaphore acquisition is non-blocking, prefetch can be skipped under load. TTL is updated only after successful completion. Large-directory mode starts at the looked-up object and will not prefetch lexicographically earlier siblings. Correctness depends on callback-side context checks before cache updates.

## Test Signals

The paired tests cover trigger-on-unknown, large-directory start offset, disabled config, single-run atomic state, destroy cancellation, max count and multi-page limits, shared semaphore concurrency limits, TTL guard, write cancellation race, recursive cancellation, nil context skip, active-writer skip, and stale-prefetch avoidance after delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go -->
