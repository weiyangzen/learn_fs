# sources/storage-engines/pebble/internal/bytealloc/bytealloc.go

Purpose: Implements a simple chunk allocator for byte slices with shared lifetime and exponential growth.

APIs and types: Type `A []byte`, constants `chunkAllocMinSize` and `chunkAllocMaxSize`, methods `Alloc`, `Copy`, `Reset`, and internal `reserve`.

Control flow and state: The allocator is itself the current chunk. `Alloc` reserves a new rawalloc chunk when remaining capacity is insufficient, returns a full-slice-capacity allocation, and advances length. `Copy` allocates then copies. `Reset` reuses the current chunk by setting length to zero.

Persistence and dependencies: Runtime memory only. Depends on `internal/rawalloc`.

Integration points: Used by components needing many same-lifetime byte copies while reducing allocation overhead.

Risks: Returned slices share backing chunks; resetting while slices are still in use can corrupt callers. Large chunks can be pinned by small surviving slices.

Test signals: No direct tests in this subset; behavior is simple but lifetime-sensitive.
