# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_wbuf.c

Purpose: Implements CHFS write-buffering for flash page-sized writes, including padding nodes and direct large writes.

Key entry points:
- `chfs_write_wbuf`: writes iovec data into the mount write buffer and flushes page-aligned chunks to flash.
- `chfs_flush_pending_wbuf`: forces pending buffered bytes to flash with padding.
- Internal `chfs_flush_wbuf`: flushes current buffer to flash, optionally appending a padding node.
- Internal `chfs_fill_wbuf`: copies bytes into the buffer and returns bytes consumed.

Important behavior:
- Writes must be contiguous relative to `chm_wbuf_ofs + chm_wbuf_len`; otherwise the code panics.
- `WBUF_SETPAD` pads to page size with `0xff`, creates a `CHFS_NODETYPE_PADDING` node, allocates an obsolete node ref, and moves free bytes to wasted bytes.
- Full write-buffer pages are written using `chfs_write_leb`.
- Large page-aligned residual data can bypass the buffer and be written directly.
- `chfs_write_wbuf` holds `chm_lock_wbuf` as writer internally; callers hold mountfields and sizes.

Dependencies:
- Flash write IO via `chfs_write_leb`.
- Node refs from `chfs_alloc_node_ref`.
- Size accounting from `chfs_change_size_free/wasted`.

Research notes:
- The error path label in `chfs_write_wbuf` returns without releasing `chm_lock_wbuf`, which is notable if `chfs_flush_wbuf` fails.
- `chfs_flush_pending_wbuf` acquires `chm_lock_sizes` and `chm_lock_wbuf`; callers must not already hold conflicting locks except as asserted.
