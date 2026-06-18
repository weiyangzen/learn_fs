# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.h

This header declares XFS iomap integration entry points and exported iomap operation tables.

Exports:
- Direct allocation and unwritten conversion:
  - `xfs_iomap_write_direct`
  - `xfs_iomap_write_unwritten`
- EOF allocation alignment:
  - `xfs_iomap_eof_align_last_fsb`
- Sequence and conversion:
  - `xfs_iomap_inode_sequence`
  - `xfs_bmbt_to_iomap`
- Zero/truncate helpers:
  - `xfs_zero_range`
  - `xfs_truncate_page`
- `xfs_aligned_fsb_count`, an inline helper that expands a block count to satisfy extent-size alignment.
- Iomap operation tables for buffered write, direct write, zoned direct write, read, seek, xattr, DAX write, atomic CoW write, and iomap write validation.

Role:
- Provides the shared interface between XFS file operations, inode operations, writeback/direct I/O paths, and the implementation in `xfs_iomap.c`.
