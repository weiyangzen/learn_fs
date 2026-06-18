# File Research: sources/os/linux/linux/fs/jffs2/writev.c

## Role

Provides direct MTD write helpers for JFFS2 when write buffering is inactive or when scalar direct writes are needed.

## Key Responsibilities

- `jffs2_flash_direct_writev()` optionally records summary metadata for vector writes when write buffering is not active, then calls `mtd_writev()`.
- `jffs2_flash_direct_write()` calls `mtd_write()` for scalar writes and records summary metadata via a one-element `kvec` when summary support is active.

## Important Interactions

- Used by `os-linux.h` as the direct-write backend when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Used indirectly by write paths that call `jffs2_flash_writev()` in non-write-buffered configurations.
- Feeds summary collection for direct writes so summarized eraseblocks remain consistent.

## Invariants and Risks

- Summary collection errors are returned before or instead of write results where applicable.
- Direct writes do not perform write-buffer recovery, pending-inode tracking, or read-overlay behavior; those are exclusive to `wbuf.c`.
