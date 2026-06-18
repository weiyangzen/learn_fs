# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/iobuf.c

Implements the fixed-size block buffer cache for `ext2srv`.

Key behavior:
- Maintains 100 `Iobuf` headers and hash buckets keyed by block address modulo `HIOB`.
- `getbuf()` returns a busy cached buffer or reuses the least recently used non-busy buffer from the tail.
- Dirty buffers are written back before reuse.
- `putbuf()` decrements busy count and moves the buffer to the LRU head.
- `syncbuf()` writes all dirty buffers.
- `purgebuf()` drops all buffers for a given `Xfs` and clears hash chains.
- `xread()` and `xwrite()` perform block-sized I/O at `addr * block_size`.

Important implementation details:
- Cache buffers are allocated at `EXT2_MAX_BLOCK_SIZE`; actual reads and writes use the filesystem block size.
- The LRU list is updated even for buffers that may still be referenced by other callers after busy count changes.

Risks and invariants:
- No explicit locking appears in this cache; correctness depends on the server's threading model and usage discipline.
- `getbuf()` panics when all buffers are busy.
