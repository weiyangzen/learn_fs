# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager_test.go

## Scope

This testify suite validates the new compositional `ReadManager` for both non-zonal and zonal bucket types.

## Purpose

The tests protect reader-chain construction, simple read behavior, fallback semantics, file-cache integration, and error propagation.

## Important APIs, Types, And Functions

- `readManagerConfig(fileCacheEnable, bufferedReadEnable)` builds test configs with optional cache handler and worker pool.
- `mockNewReaderWithHandleCallForTestBucket` matches GCS range requests.
- `readAt` wraps `ReadManager.ReadAt` with invariant checks.
- Test cases cover construction combinations, EOF, GCS errors, clobbering, cache hit, and fallback.

## Control Flow

`SetupTest` creates object metadata, a testify mock bucket, context, and default read manager with file cache enabled. Individual tests override config or construct synthetic managers with mock readers to isolate fallback logic. Buffered-read tests start and stop a worker pool when needed.

## State And Persistence Behavior

The suite checks `readers` slice composition and uses cache directories under `$HOME/test_cache_dir` for file cache behavior. It verifies that a first read can populate cache and a second read succeeds without additional GCS reads. `TearDownTest` destroys the manager and stops worker pools.

## Dependencies And Integration Points

It integrates with `bufferedread`, file cache/downloader/LRU, `client_readers.GCSReader`, `gcsx.MockReader`, fake readers, storage testify mocks, semaphores, worker pools, metrics/tracing noops, and clobber error types.

## Risks And Maintenance Notes

The construction assertions rely on concrete reader types and exact ordering. File-cache tests touch filesystem paths outside `t.TempDir` unless explicitly removed. Buffered creation failure is simulated by a zero-weight semaphore; if buffered reader initialization changes, that test may need updating.

## Test Signals

Signals include expected reader counts and concrete types for each config, empty-read success, EOF for reads at/past object size, network error propagation, timeout propagation, `FileClobberedError` wrapping on not found, cache reuse on repeated full-object reads, fallback on `FallbackToAnotherReader`, and no fallback on hard errors.
