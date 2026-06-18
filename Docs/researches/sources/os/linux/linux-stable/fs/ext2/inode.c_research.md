# File Research: sources/os/linux/linux-stable/fs/ext2/inode.c

## Summary
Implements ext2 inode lifecycle, block mapping through direct/indirect/triple-indirect trees, iomap integration, buffered address-space operations, DAX mapping support, truncation, inode read/write, getattr, and setattr.

## Main Responsibilities
- Maps logical file blocks to physical blocks and allocates missing branches.
- Builds and splices indirect block chains safely against truncate races.
- Provides `ext2_get_block()` for buffer-head based I/O and `ext2_iomap_ops` for iomap/DAX/direct I/O.
- Handles write failures by truncating pagecache and blocks.
- Evicts deleted inodes, truncates data, deletes xattrs, frees inode blocks and inode bitmap state.
- Truncates direct and indirect block trees.
- Reads raw on-disk inodes into VFS/ext2 in-memory inodes.
- Writes in-memory inode state back to disk, including large-file feature enablement.
- Implements `getattr`, `setattr`, and file operation selection.

## Key APIs
- `ext2_get_block()`.
- `ext2_iomap_ops`.
- `ext2_aops`.
- `ext2_fiemap()`.
- `ext2_evict_inode()`.
- `ext2_iget()`.
- `ext2_write_inode()`.
- `ext2_setattr()`, `ext2_getattr()`.
- `ext2_set_inode_flags()`, `ext2_set_file_ops()`.

## Important Behavior
Ext2 uses 12 direct pointers plus single, double, and triple indirect blocks. `ext2_block_to_path()` computes offsets into that tree. `ext2_get_branch()` reads existing indirect blocks and detects concurrent changes with key verification. Allocation happens under `truncate_mutex`, allocates all needed metadata/data blocks before linking them, and only splices the missing pointer after rechecking the chain.

Iomap writes to holes inside `i_size` with direct I/O are rejected with `-ENOTBLK` to force buffered I/O. DAX allocations zero newly allocated blocks before exposing them through the tree.

Truncation detaches partial branches under `i_meta_lock`, frees subtrees recursively, discards reservations, and uses `invalidate_lock` around block tree changes. Fast symlinks are excluded from block truncation.

## State and Synchronization
`truncate_mutex` serializes block allocation and truncation. `i_meta_lock` protects indirect pointer verification/detach. `mapping->invalidate_lock` protects truncate/DAX invalidation interactions. Metadata buffer heads are tracked through `i_metadata_bhs`.

## Risks
The block tree code is race-sensitive: partial indirect chains can change during lookup, truncate can remove branches, and allocation must not expose uninitialized blocks. Inode timestamp storage is 32-bit ext2 format, matching the Kconfig deprecation warning.
