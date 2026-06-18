# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_subr.c

## Purpose
Provides shared ext2 helpers for reading directory/file blocks by byte offset and maintaining free-cluster summary accounting.

## Main Elements
- `ext2_blkatoff()` maps a byte offset to a logical block, reads the block with `bread()`, verifies directory block checksum via `ext2_dir_blk_csum_verify()`, returns the buffer, and optionally returns a pointer into the block.
- `ext2_clusteracct()` initializes and updates per-group contiguous-free-run summaries used by allocator cluster selection.
- Cluster accounting scans bitmap bits on first use, then adjusts forward/backward run lengths around an allocation or free event.

## Dependencies And Integration
Used heavily by lookup, directory mutation, bmap/allocation-adjacent code, and checksum validation. It depends on `fs.h` block macros and `m_ext2fs` cluster summary arrays.

## Risk Notes
`ext2_blkatoff()` applies directory checksum validation to every block it returns. `ext2_clusteracct()` assumes bitmap bit semantics and group geometry are already validated by mount-time code.
