# File Research: sources/local-fs/reiserfsprogs/lib/io.c

Implements the user-space buffer cache and rollback support. Buffers are kept in a circular active list, free list, and 4096-bucket hash table. `getblk()` reuses clean unreferenced buffers, grows the cache in groups of ten, and flushes dirty buffers once the soft memory limit is reached. `bread()` reads a block into an uptodate buffer and treats EOF/read errors distinctly.

Write path:
- `bwrite()` skips clean/non-uptodate buffers, invokes optional callbacks, seeks to block offset, optionally saves original disk content to the rollback file, writes full buffer data, marks clean, and invokes end-I/O callback.
- `flush_buffers()`, `free_buffers()`, and `invalidate_buffers()` manage cache lifecycle.

Rollback support writes a magic header, block size, count, and original block images before destructive fsck writes. `do_fsck_rollback()` restores saved blocks to the data or journal device by matching recorded device ids.
