# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_inode.c

This file implements FFS inode update, truncation, indirect block reclamation, and timestamp materialization. It is the core code for persisting inode changes and freeing storage safely.

Key responsibilities:
- Write in-core inode state back to on-disk dinode blocks.
- Truncate normal file data and UFS2 extension data.
- Grow files by allocating the last byte/range needed.
- Free direct and indirect blocks, including partial final fragments.
- Coordinate quota updates and WAPBL deallocation registration.
- Update atime, mtime, ctime, and modrev from pending inode flags.

Important functions:
- `ffs_update`: Applies pending times with `FFS_ITIMES`, reads the containing inode block, updates WAPBL unlinked-inode registration state, writes UFS1/UFS2 dinode bytes with optional endian swapping, and writes or delays the buffer based on update flags.
- `ffs_truncate`: Handles special vnode no-ops, negative length rejection, `IO_EXT` truncation of UFS2 EA blocks, short symlink clearing, file growth allocation, EOF zeroing before shrink, inode pointer clearing, indirect/direct block freeing, WAPBL deallocation registration, quota updates, and VM size consistency.
- `ffs_indirtrunc`: Recursively frees blocks referenced by single/double/triple indirect blocks. It writes cleared pointers before freeing for non-WAPBL safety, handles endian-aware pointer arrays, and unwinds WAPBL deallocation cookies on error.
- `ffs_itimes`: Converts `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, and `IN_MODIFY` into dinode timestamp updates, avoids mtime updates for snapshots, increments `i_modrev`, marks `IN_ACCESSED`/`IN_MODIFIED`, and clears transient flags.

Important interactions:
- Uses `ffs_balloc`, `ffs_blkfree`, `ffs_snapremove`, `ffs_update`, `ffs_getblk`, WAPBL macros, quota hooks, UVM page invalidation/zeroing, and UFS byte-order helpers.
- `ffs_truncate` is used by normal vnode truncation, EA truncation, failed snapshot setup cleanup, and reclaim/inactive flows.

Notable behavior and risks:
- Partial EA truncation is intentionally unsupported and panics if requested with nonzero length.
- For WAPBL, regular file data block frees may differ from metadata/non-regular deallocation handling.
- On `EAGAIN` during deallocation, truncation restores logical size but may have created holes.
- Triple indirect support is present but noted as untested.
