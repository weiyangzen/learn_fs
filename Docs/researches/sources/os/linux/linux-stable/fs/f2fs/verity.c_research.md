# File Research: sources/os/linux/linux-stable/fs/f2fs/verity.c

## Purpose
`verity.c` implements F2FS `fsverity_operations`, enabling fs-verity metadata storage, descriptor lookup, Merkle tree IO, and enable/cleanup flow.

## Main Responsibilities
- Stores verity metadata beyond normal file size, starting at the first 64 KiB boundary after `i_size`.
- Reads and writes metadata through pagecache helpers that can access pages beyond `i_size`.
- Records descriptor location in a small F2FS verity xattr rather than storing the descriptor itself in xattrs.
- Hooks F2FS into the generic fs-verity layer through `f2fs_verityops`.

## Key Data and Interfaces
- `f2fs_verity_metadata_pos(inode)` returns `round_up(i_size, 65536)`.
- `struct fsverity_descriptor_location` stores version, descriptor size, and descriptor position.
- `f2fs_begin_enable_verity` rejects concurrent verity enable and atomic files, initializes quotas, converts inline data, and marks `FI_VERITY_IN_PROGRESS`.
- `f2fs_end_enable_verity` writes the descriptor, flushes file metadata, sets the verity xattr, sets the inode verity flag, and marks inode dirty.
- `f2fs_get_verity_descriptor` reads descriptor location from xattr, validates bounds, and reads the descriptor.
- `f2fs_read_merkle_tree_page`, `f2fs_readahead_merkle_tree`, and `f2fs_write_merkle_tree_block` translate fs-verity offsets into F2FS metadata offsets.

## Failure Handling
If enablement fails, `f2fs_end_enable_verity` truncates cached and on-disk metadata beyond `i_size`, protects cleanup with `i_gc_rwsem[WRITE]` so GC cannot reinstantiate pages, clears `FI_VERITY_IN_PROGRESS`, and marks the filesystem for fsck if truncation fails.

## Dependencies
- Uses `f2fs_getxattr` and `f2fs_setxattr` from the xattr layer.
- Uses `max_file_blocks` from `super.c` to enforce max metadata position.
- Installed by `super.c` through `sb->s_vop = &f2fs_verityops` when `CONFIG_FS_VERITY` is enabled.

## Notable Edge Cases
- Verity cannot be enabled for atomic files.
- Descriptor xattr corruption triggers `ERROR_CORRUPTED_VERITY_XATTR`.
- Xattrs cannot hold the descriptor directly because F2FS xattrs are small and not encrypted, while verity metadata must be encrypted for encrypted files.
