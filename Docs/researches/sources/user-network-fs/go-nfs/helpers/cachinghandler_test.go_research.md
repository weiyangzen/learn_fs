<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go -->
# sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go

## Purpose
Concurrency tests for the caching handler's handle and reverse-cache paths.

## Important APIs, Types, and Functions
Tests are `TestCachingHandlerConcurrentToHandle`, `TestCachingHandlerConcurrentToHandleAndFromHandle`, and `TestCachingHandlerConcurrentInvalidateHandle`.

## Control Flow
They create a memfs-backed null-auth handler, wrap it in `CachingHandler`, then run goroutines creating, resolving, and invalidating handles across unique and shared paths.

## State and Persistence Behavior
State is in-memory cache structures and a memfs filesystem.

## Dependencies and Integration Points
Depends on `helpers/memfs` and helper handler construction.

## Risks and Edge Cases
The tests do not assert returned values; they are intended primarily for race detector coverage.

## Test Signals
Run with `go test -race -run TestCachingHandlerConcurrent ./helpers` to catch synchronization bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go -->
