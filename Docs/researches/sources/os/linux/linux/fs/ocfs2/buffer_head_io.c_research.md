# File Research: sources/os/linux/linux/fs/ocfs2/buffer_head_io.c

OCFS2 buffer_head read/write helper implementation. It layers OCFS2 clustered metadata-cache state and validation over Linux buffer_head I/O.

Key functions:
- `ocfs2_write_block()`: synchronous nonjournaled metadata write for system-file style buffers. It rejects hard-readonly mounts, marks the buffer uptodate, clears dirty state, submits write I/O, waits, and updates OCFS2’s metadata uptodate cache on success.
- `ocfs2_read_blocks_sync()`: simple synchronous read of a contiguous block range without clustered cache validation.
- `ocfs2_read_blocks()`: main cached metadata read routine. It honors `OCFS2_BH_IGNORE_CACHE`, `OCFS2_BH_READAHEAD`, JBD-owned buffers, dirty buffers, OCFS2 clustered uptodate state, and optional validation callbacks.
- `ocfs2_write_super_or_backup()`: writes the primary or backup superblock directly, computes metadata ECC first, and refuses emergency readonly state.

Internal state:
- Defines `BH_NeedsValidate` as an OCFS2-private buffer state bit after JBD private bits.
- `NeedsValidate` is set when a freshly submitted read must later run the caller’s validation callback.

Important behavior:
- Caller-provided `bhs[]` must contain either all `NULL` or all non-`NULL` entries; allocation and cleanup logic depends on that.
- On read failure, newly allocated buffer_heads are put and nulled; externally supplied uptodate buffers have uptodate cleared.
- Readahead does not wait for completion but still records buffers in the OCFS2 uptodate cache.
- Buffers owned by JBD are skipped because the journal controls their state.
- Superblock writes verify the block number is the primary or a known backup and do not use the metadata cache lock path.
