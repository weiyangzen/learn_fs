# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/inode.h

## Purpose
Defines the in-core ext2 inode representation, logical block path helpers, inode flags, file mode/type constants, and NFS file-handle overlay.

## Main Elements
- Defines ext2 direct/indirect counts and block/time typedefs.
- `struct inode` stores vnode/mount links, inode number, lookup side-effect fields, allocation hints, UFS-like metadata fields, block pointers or extent data overlay, extent cache, and cluster-write state.
- `i_shortlink` aliases direct block pointers for inline symlink storage.
- Defines ext2 permission and file type constants.
- Defines in-core state flags: access/change/update, modified, rename-in-progress, lazy mod/access, space counted.
- Defines translation flags `IN_E3INDEX` and `IN_E4EXTENTS`.
- Provides `VTOI()` and `ITOV()` conversions.
- Defines `struct indir` for indirect block traversal and `struct ufid` for file handles.

## Dependencies And Integration
Central to all ext2fs kernel files. Directory lookup mutates `i_offset`, `i_count`, `i_endoff`, and `i_diroff`; allocation uses block group and next allocation hints; vnode ops use metadata fields.

## Risk Notes
The block pointer array is reused for inline symlinks and ext4 extents, so code must check inode mode and `IN_E4EXTENTS` before interpreting it.
