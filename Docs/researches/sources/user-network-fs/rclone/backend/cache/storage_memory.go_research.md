# sources/user-network-fs/rclone/backend/cache/storage_memory.go

## Purpose
`storage_memory.go` implements transient in-memory chunk storage for active cache readers.

## Important APIs, Types, And Control Flow
`Memory` wraps `patrickmn/go-cache`. `NewMemory` and `Connect` initialize the cache. `HasChunk`, `GetChunk`, `AddChunk`, and `AddChunkAhead` use keys formatted as `objectAbs-offset`. `CleanChunksByAge` removes expired entries. `CleanChunksByNeed` scans all keys, parses the trailing offset after the final hyphen, and deletes chunks older than the requested offset. `CleanChunksBySize` is a no-op because this layer is bounded by read flow, not byte accounting.

## State And Persistence
State is process-local only. Chunks are `[]byte` values in memory and disappear on handle close or process exit. `Handle.Close` flushes the underlying cache.

## Dependencies And Integration Points
Memory storage is used by `Handle` when `ChunkNoMemory` is false. Workers promote chunks from persistent storage to memory, downloads write to both layers, and `queueOffset` evicts already-read offsets.

## Risks And Test Signals
Risks include key parsing when object paths contain hyphens, unchecked type assertions in `GetChunk`, lack of size enforcement, and scanning all cache items for eviction. Read tests and max chunk size cleanup tests indirectly validate that memory behavior does not break persistent chunk delivery.
