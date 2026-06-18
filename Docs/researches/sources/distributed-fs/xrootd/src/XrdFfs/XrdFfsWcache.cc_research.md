# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.cc

## Purpose

This file implements a per-file-descriptor cache used by XrootdFS. It batches consecutive small writes into larger `pwrite()` calls and, for a restricted direct-I/O read case, caches one read block to improve erasure-coded or remote read performance.

## Important APIs, Types, and Functions

`XrdFfsWcache_init(basefd, maxfd)` initializes the descriptor table and cache sizing. `XrdFfsWcache_create(fd, flags)` allocates a buffer and mutex for a descriptor. `destroy()`, `flush()`, `pread()`, and `pwrite()` manage descriptor-local cache contents.

`XrdFfsWcacheFilebuf` stores cached offset, length, buffer pointer, buffer size, and mutex pointer. Global state includes base virtual fd, maximum fd count, cache buffer array, write buffer size, and read-cache buffer size.

## Control Flow

Initialization sizes read cache to 128 KiB by default, to the EC data-block size when `XRDCL_EC` is set, or to `XROOTDFS_WCACHESZ` when present. `create()` allocates either read-cache or write-cache sized buffers depending on open flags.

`pwrite()` bypasses the cache for large writes or out-of-range descriptors. Small consecutive writes append to the descriptor buffer. Non-consecutive writes or buffer overflow force `flush()`, which calls `XrdFfsPosix_pwrite()` and clears the cache on success. `pread()` loads the block containing the requested offset and serves bytes from cache when possible.

## State and Persistence Behavior

Cached data is process-local and per virtual fd. Remote persistence only happens on `flush()`, direct bypass writes, `fsync()`, `ftruncate()`, or release paths that explicitly flush. Destroy does not call flush, so callers must flush first.

## Dependencies and Integration Points

The implementation depends on XrdFfsPosix for actual I/O and is used by `xrootdfs_open()`, `create()`, `read()`, `write()`, `fsync()`, `ftruncate()`, and `release()`.

## Risks and Edge Cases

`XROOTDFS_WCACHESZ` assigns to `XrdFfsRcacheBufsize`, not the write-cache size, despite the name. `create()` can leak the first allocation if mutex allocation fails. Descriptor bounds are checked after subtracting base fd in some paths but not consistently before table access. Destroying without flush loses buffered writes.

## Test Signals

Tests should cover consecutive small-write coalescing, flush on gaps/overflow, direct large write bypass, release/fsync/ftruncate flush behavior, direct-I/O read cache hits/misses, fd bounds, environment sizing, and failure cleanup under allocation errors.
