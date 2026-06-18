# sources/user-network-fs/s3fs-fuse/src/fdcache_stat.h

Purpose: Declares `CacheFileStat`, the lockable sidecar-file abstraction for cache page metadata.

Important APIs and types: Static APIs check, delete, rename, and locate the cache-stat tree. Instance APIs open sidecars for read/write or read-only, release locks/fds, set object path, return fd, and atomically overwrite content.

Control flow contract: Construct with an object path or call `SetPath`, open with `Open`/`ReadOnlyOpen`, use `GetFd` or `OverWriteFile`, then call `Release` or rely on the destructor. Copy/move are disabled to keep fd/lock ownership singular.

State and persistence behavior: Stores the logical object path and current sidecar fd. Persistent content format is defined by `PageList`.

Dependencies and integration points: Included by `fdcache_page.cpp`, `fdcache_entity.cpp`, and `fdcache.cpp`. The private `MakeCacheFileStatPath` centralizes path derivation.

Risks: Callers must respect lock lifetime and not hold stale fds after object rename/delete. Header hides path creation, so tests generally need real cache configuration or stubs.

Test signals: Cache persistence, cache cleanup, and cache consistency diagnostics are the main validation paths.
