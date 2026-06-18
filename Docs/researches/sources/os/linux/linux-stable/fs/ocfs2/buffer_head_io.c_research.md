# File Research: sources/os/linux/linux-stable/fs/ocfs2/buffer_head_io.c

## Summary
Implements OCFS2 metadata buffer-head I/O helpers. It handles synchronous metadata reads/writes, clustered metadata-cache uptodate state, optional validation of freshly read buffers, readahead handling, and non-journaled superblock/backup writes with ECC computation.

## Main Responsibilities
- Write a metadata buffer outside JBD2 while updating OCFS2’s metadata cache state.
- Read one or more blocks synchronously, allocating buffer heads when needed.
- Read through the clustered metadata cache with `IGNORE_CACHE` and `READAHEAD` modes.
- Mark freshly read buffers for validation and call a provided validator after I/O completion.
- Keep JBD-managed buffers from being read or written incorrectly.
- Write the main superblock or backup superblocks with metadata ECC.

## Key Interfaces
- `ocfs2_write_block()` writes one non-journaled metadata block.
- `ocfs2_read_blocks_sync()` performs direct synchronous multi-block reads.
- `ocfs2_read_blocks()` is the cache-aware read helper used broadly by metadata code.
- `ocfs2_write_super_or_backup()` validates target block identity and writes superblock data.

## Important Behavior
`ocfs2_read_blocks()` uses an OCFS2-specific `BH_NeedsValidate` buffer state bit. Validation is only run for buffers freshly read from disk, but readahead can set the flag so a later synchronous caller validates the completed buffer.

Read error cleanup is careful about ownership: if this helper allocated the buffer heads it drops and nulls them, while caller-supplied buffers have uptodate state cleared.

## State and Synchronization
Uses OCFS2 metadata cache I/O locks, buffer locks, local buffer uptodate/dirty state, clustered uptodate tracking from `uptodate.c`, and JBD2 buffer ownership checks.

## Risks
Correctness depends on not racing JBD2 ownership, preserving caller ownership of buffer-head arrays, and validating all disk-fresh metadata before trusting it. Superblock writes bypass journaling and therefore must only target the primary or known backup superblocks.
