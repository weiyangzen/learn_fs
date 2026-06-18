## sources/user-network-fs/blobfuse2/internal/handlemap/handle_map.go

Purpose: Defines blobfuse2 file handle state and a global concurrent handle map from blobfuse handle IDs to `Handle` objects.

Important APIs and flow: `Handle` embeds `sync.RWMutex` and stores an OS file, optional stream cache, buffers, ID, size, mtime, Unix FD, operation count, flags, path, and arbitrary key/value data. Methods expose dirty/fsynced/cached flag queries, file object get/set, FD, value set/get/remove, and cleanup. Global `Add` allocates a unique ID with atomic increment and stores the handle in `sync.Map`; `Load`, `Delete`, and `GetHandles` access the map. `CreateCacheObject` attaches an LRU block cache. `Store` is a test utility.

State and dependencies: Persistent runtime state is global `defaultHandleMap` and `nextHandleID`; per-handle state coordinates libfuse, caches, xload, and storage components. Depends on `common.BitMap64`, cache policy LRU, `os.File`, `sync`, and atomic counters.

Risks: Global map can leak handles if releases do not delete them. `values` map is not separately synchronized beyond caller use of the handle lock. Native cgo paths store raw `Handle` pointers, so lifetime matters. Tests in this subset exercise handle use indirectly through loopback, xload, and libfuse wrappers.
