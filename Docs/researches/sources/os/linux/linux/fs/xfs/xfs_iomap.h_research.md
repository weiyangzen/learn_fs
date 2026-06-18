# File Research: sources/os/linux/linux/fs/xfs/xfs_iomap.h

## Role
Declares XFS iomap helper functions and operation tables used by XFS file I/O, fiemap, xattr mapping, zeroing, and truncate code.

## Main Declarations
- Allocation/conversion helpers: `xfs_iomap_write_direct`, `xfs_iomap_write_unwritten`, `xfs_iomap_eof_align_last_fsb`.
- Mapping helpers: `xfs_iomap_inode_sequence`, `xfs_bmbt_to_iomap`.
- Zero/truncate helpers: `xfs_zero_range`, `xfs_truncate_page`.
- `xfs_aligned_fsb_count` inline helper expands a file-block count to satisfy extent-size alignment.
- Iomap ops tables for buffered write, direct write, zoned direct write, read, seek, xattr, DAX write, atomic-write COW, and write validation.

## Interactions
Included by inode operations and other XFS I/O code. It is the public boundary for `xfs_iomap.c` and advertises the set of iomap modes XFS supports.

## Invariants
`xfs_aligned_fsb_count` preserves the original requested span while extending start/end coverage to an extent-size multiple when a nonzero extent size hint is supplied.
