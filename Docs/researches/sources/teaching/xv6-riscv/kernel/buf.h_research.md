# File Research: sources/teaching/xv6-riscv/kernel/buf.h

Defines `struct buf`, the in-memory representation of a cached disk block.

Fields:
- `valid` tracks whether `data` has been loaded from disk.
- `disk` is used by the virtio driver to indicate an in-flight disk operation.
- `dev` and `blockno` identify the cached block.
- `lock` is a sleeplock protecting block contents.
- `refcnt`, `prev`, and `next` support cache lifetime and LRU ordering.
- `data[BSIZE]` stores the 1024-byte filesystem block.

Filesystem relevance: this structure is shared by the buffer cache, log, filesystem, and virtio driver, making it the common unit for block I/O and transaction pinning.
