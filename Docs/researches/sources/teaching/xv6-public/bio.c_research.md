# File Research: sources/teaching/xv6-public/bio.c

Implements the xv6 block buffer cache.

Key behavior:
- Initializes `NBUF` buffers in an MRU/LRU doubly linked list, each protected by a sleeplock.
- `bget` finds an existing cached `(dev, blockno)` buffer or recycles an unused, non-dirty LRU buffer.
- `bread` returns a locked buffer, reading from disk through `iderw` if not valid.
- `bwrite` marks a locked buffer dirty and synchronously drives IDE I/O.
- `brelse` releases the sleeplock, decrements the reference count, and moves unused buffers to the MRU head.

Important interactions:
- Dirty buffers are not recycled because the log may have pinned them before commit.
- The buffer cache is the synchronization point shared by filesystem, log, and IDE layers.
