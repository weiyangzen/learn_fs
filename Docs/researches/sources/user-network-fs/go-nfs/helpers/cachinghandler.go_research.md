<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler.go -->
# sources/user-network-fs/go-nfs/helpers/cachinghandler.go

## Purpose
Provides an LRU-backed implementation of opaque NFS file handles and directory verifier caching around another handler.

## Important APIs, Types, and Functions
`NewCachingHandler`, `CachingHandler.ToHandle`, `FromHandle`, `InvalidateHandle`, `HandleLimit`, `VerifierFor`, `DataForVerifier`, and reverse-cache helpers are central.

## Control Flow
`ToHandle` reuses an existing UUID for the same filesystem/path or allocates one, evicting the oldest cache entry. `FromHandle` resolves UUIDs and refreshes related entries. Directory verifiers hash path and sorted contents and cache listings.

## State and Persistence Behavior
Persistent process state includes active handle LRU, reverse path-to-UUID map protected by a mutex, verifier LRU, and cache size.

## Dependencies and Integration Points
Used by examples and recommended for handlers that do not provide stable handles themselves.

## Risks and Edge Cases
`activeHandles` LRU is used concurrently without an outer mutex; reverse handle slices are returned without copying; filesystem comparison uses `reflect.DeepEqual`. Race tests target this area.

## Test Signals
`cachinghandler_test.go` stresses concurrent ToHandle/FromHandle/Invalidate; running with `-race` is important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler.go -->
