# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.cc

## Purpose
Implements memory-mapped read optimization for OSS files, including mapping reuse, optional `mlock`, optional page preloading, idle reclamation, and configuration display/update.

## Important APIs, types, and functions
Static state includes `MM_Hash`, `MM_Mutex`, permanent and idle queues, enable/check/preload flags, max bytes, page size/count, and current mapped bytes. `Display()` prints effective `oss.memfile` settings. `Map()` stats the fd, creates a device+inode hash key, reuses an existing mapping when present, reclaims idle mappings if `MM_max` would be exceeded, `mmap()`s the whole file, optionally `mlock()`s it, creates an `XrdOssMioFile`, adds it to the hash, queues permanent mappings, and starts a preload thread when configured. `preLoad()` touches one byte per page and then recycles. `Recycle()` decrements use count and moves non-permanent mappings to the idle list. `Reclaim()` removes idle mappings from queues/hash. `Set()` overloads update boolean mode flags and max-memory policy.

## Control flow
Map callers get a shared `XrdOssMioFile` whose `inUse` count protects the mapping. When callers finish, they call `Recycle()`. Idle mappings remain cached until memory pressure triggers `Reclaim(amount)` or a reuse path removes them from the idle list.

## State and persistence
State is entirely in-process memory. `XrdOssMioFile::~XrdOssMioFile()` unmaps memory when the hash deletes the object. No disk persistence occurs.

## Dependencies and integration points
Configured by `oss.memfile` in `XrdOssConfig.cc` and likely used by OSS file open/read paths outside this subset. Depends on POSIX mmap/mlock support, `XrdOucHash`, `XrdSysThread`, `XrdOucUtils::bin2hex`, and OSS logging/tracing.

## Risks and test signals
Risk areas include zero-length files passed to `mmap`, `MM_inuse` not decremented on some `mmap`/object-allocation failure paths after it is incremented, preload thread races with reuse/recycle, and platform support differences. Tests should exercise reuse, idle reclaim ordering, permanent mappings, max percent parsing, mlock permission failure, preload lifecycle, and non-POSIX-mapped builds.
