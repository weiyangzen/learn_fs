# File Research: sources/teaching/xv6-riscv/kernel/bio.c

Implements xv6’s buffer cache: a fixed `NBUF` array of `struct buf` objects arranged as an LRU doubly linked list. The cache gives filesystem and log code a synchronized block-level interface through `bread`, `bwrite`, `brelse`, `bpin`, and `bunpin`.

Important behavior:
- `binit()` initializes the global cache lock, each buffer sleeplock, and the LRU list.
- `bget()` first searches for an existing `(dev, blockno)` buffer, otherwise recycles an unused least-recently-used buffer.
- `bread()` loads a block through `virtio_disk_rw()` only when `valid == 0`.
- `bwrite()` requires the buffer sleeplock and writes synchronously to the virtio disk.
- `brelse()` releases the sleeplock, drops `refcnt`, and moves unused buffers to the MRU head.
- `bpin()`/`bunpin()` adjust `refcnt` so the log can keep dirty buffers resident until commit.

Filesystem relevance: this file is the shared synchronization point between inode/block allocation code, the write-ahead log, and the virtio disk driver. The split between a global spinlock and per-buffer sleeplocks is central to avoiding duplicate cached copies while still allowing long block use.
