# sources/user-network-fs/rclone/backend/archive/squashfs/cache.go

Purpose: Implements a `backend.Storage` adapter for go-diskfs squashfs reading over an rclone VFS node, with a small file-handle cache optimized for `ReadAt` offsets.

Important APIs/types/functions: `cache` stores a `vfs.Node`, mutex, and slice of cached handles. `cacheHandle` records expected next offset and handle. `newCache`, `open`, `close`, `ReadAt`, `Close`, and stub methods `WriteAt`, `Seek`, `Read`, `Stat`, `Sys`, `Writable` satisfy `backend.Storage`.

Control flow: `ReadAt` obtains a handle whose cached offset matches the request if possible, otherwise reuses the first cached handle or opens the node. After reading, it caches the handle with next offset `off+len(p)`. `Close` closes all cached handles.

State and persistence: Maintains in-memory pool of VFS handles and offsets. Does not persist data or write to archives.

Dependencies and integration points: Bridges `github.com/diskfs/go-diskfs/backend.Storage` with rclone `vfs.Node`/`vfs.Handle`. Used by `squashfs.New` to feed `squashfs.Read`.

Risks: Handle pool can grow with concurrent access until `Close`. Offset caching is heuristic; a reused nonmatching handle relies on underlying `ReadAt` correctness. Stub methods return internal errors if diskfs unexpectedly needs them.

Test signals: Squashfs archive tests indirectly validate parallel/random reads through this adapter.
