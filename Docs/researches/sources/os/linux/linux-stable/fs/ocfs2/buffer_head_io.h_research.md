# File Research: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.h

## Summary
Declares OCFS2 buffer-head I/O helpers and read flags.

## Main Responsibilities
- Expose metadata block read/write helpers.
- Define `OCFS2_BH_IGNORE_CACHE` and `OCFS2_BH_READAHEAD`.
- Provide a single-block inline wrapper around `ocfs2_read_blocks()`.
- Document validator behavior for fresh disk reads.

## Key Interfaces
- `ocfs2_read_blocks()` accepts an optional validator invoked only for fresh disk I/O.
- `ocfs2_read_block()` is the common one-block helper.
- `ocfs2_write_super_or_backup()` is the specialized non-journaled superblock writer.

## Risks
Callers using validators must pass them for readahead too when later validation is required, because the helper uses a buffer state bit to remember validation need.
