# File Research: sources/os/linux/linux/fs/ocfs2/buffer_head_io.h

Header for OCFS2 buffer_head I/O helpers.

Declares:
- `ocfs2_write_block()`.
- `ocfs2_read_blocks_sync()`.
- `ocfs2_read_blocks()` with optional validation callback.
- `ocfs2_write_super_or_backup()`.

Defines:
- `OCFS2_BH_IGNORE_CACHE`: force disk read instead of clustered metadata cache.
- `OCFS2_BH_READAHEAD`: submit best-effort metadata readahead.
- `ocfs2_read_block()` inline wrapper for a single-block cached read.

Contract:
- Validation callbacks are invoked only for freshly read buffers, not cache hits.
- Readahead callers still need to pass validation callbacks so the buffer can be marked for later validation.
