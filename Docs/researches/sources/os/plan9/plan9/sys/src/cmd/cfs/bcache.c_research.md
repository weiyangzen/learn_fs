# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.c

This file implements the fixed-size block cache used by `cfs` for its on-disk cache partition.

Key behavior:
- `bcinit()` initializes cache buffers, LRU list, dirty list, block size, and backing fd.
- `bcfind()` locates an in-use buffer by block number or chooses the least-recently-used buffer, flushing dirty contents before reuse.
- `bcalloc()` assigns a buffer to a block without reading from disk.
- `bcread()` reads a block into cache on miss.
- `bcmark()` marks buffers dirty and queues them in write order.
- `bcwrite()` writes dirty buffers through a target buffer, preserving ordering.
- `bcsync()` writes all dirty buffers.
- `bread()` and `bwrite()` perform positional block-sized I/O using `pread`/`pwrite`.

Important details:
- `Indbno` is masked out for physical block reads/writes.
- Dirty-page ordering is explicit because inode/pointer/data update order matters to cache consistency.
- Cache size is fixed by `Nbcache` from `bcache.h`.

Filesystem relevance:
- Direct. This is the block-cache layer for `cfs`’s persistent local cache.
