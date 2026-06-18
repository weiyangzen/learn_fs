# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dentry.c

This file implements dentry/block mapping helpers for KFS file data and directories.

Key behavior:
- `getdir` returns a `Dentry*` within a directory block by slot.
- `accessdir` updates atime, mtime, qid version, and buffer dirty flags unless read-only or `noatime`.
- `dbufread` is a no-op placeholder for read-ahead.
- `rel2abs` maps a file-relative block number to a disk block through direct, single-indirect, or double-indirect pointers, allocating blocks when a nonzero tag is requested.
- `dnodebuf` returns a locked data block without releasing the parent buffer.
- `dnodebuf1` releases the parent buffer before returning the child block to reduce lock interference.
- `indfetch` reads/allocates indirect entries.
- `dtrunc` frees double-indirect, single-indirect, and direct blocks, clears size, marks the dentry dirty, and updates write metadata.

Dependencies:
- Uses `balloc`, `bfree`, `getbuf`, `putbuf`, `checktag`, and `settag`.
- Depends on block-size globals `BUFSIZE`, `INDPERBUF`, and `INDPERBUF2`.

Notable detail:
- Tags carry qid path identity, so indirect/data block lookups validate both block type and owning qid path.
