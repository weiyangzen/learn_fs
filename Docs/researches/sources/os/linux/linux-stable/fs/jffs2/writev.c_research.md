# File Research: sources/os/linux/linux-stable/fs/jffs2/writev.c

This file provides direct, non-write-buffered flash write helpers.

Key responsibilities:
- `jffs2_flash_direct_writev()` optionally records the kvec write in the summary collector when the filesystem is not write-buffered, then calls `mtd_writev()`.
- `jffs2_flash_direct_write()` calls `mtd_write()` for a contiguous buffer and then records the same write as a one-element kvec in summary collection when summary support is active.

Important interactions:
- Used directly in non-write-buffer builds and indirectly by `wbuf.c` when write buffering is disabled.
- Feeds summary collection for direct writes so mount-time summary nodes can describe newly written data.

Notable invariants and risks:
- In `jffs2_flash_direct_write()`, summary collection runs after `mtd_write()` even if the write returned an error; callers still receive the original write result unless summary collection itself returns an error.
- Summary collection can fail with `-ENOMEM`, replacing the write helper return even though flash I/O may already have occurred.
