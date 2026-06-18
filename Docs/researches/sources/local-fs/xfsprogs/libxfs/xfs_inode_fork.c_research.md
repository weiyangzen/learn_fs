# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.c

## Role

This file manages incore inode fork contents. It formats data and attribute forks from dinodes, manages local fork data and btree roots, serializes fork contents back to dinodes during flush, initializes CoW forks, verifies shortform fork contents, handles large extent counter upgrades, and answers fork placement questions.

## Fork Formatting

`xfs_iformat_data_fork` initializes the data fork format and extent count, sets `if_needextents` for btree forks with release semantics, then dispatches by inode mode and fork format:

- device modes use `XFS_DINODE_FMT_DEV`
- local regular file data is invalid, but local directories and symlinks are loaded and verified
- extents format is loaded with `xfs_iformat_extents`
- btree format copies the on-disk bmap root with `xfs_iformat_btree`
- metadata-btree format loads special realtime metadata btrees

`xfs_iformat_attr_fork` initializes the attr fork and handles local shortform xattrs, extents, or btree roots. Invalid attr formats mark the inode sick and reset the attr fork.

## Local And Extent Loading

`xfs_init_local_fork` copies inline data into memory. Symlink data is overallocated by one byte and NUL-terminated so it can be returned directly to VFS-style callers.

`xfs_iformat_local` bounds-checks inline fork size against available dinode fork space before copying.

`xfs_iformat_extents` validates extent count and byte size, decodes each disk bmbt record, validates it with `xfs_bmap_validate_extent`, inserts it into the incore extent tree, and traces the loaded extent.

`xfs_iformat_btree` validates btree root shape, level, record count, fork space, and extent count before allocating `if_broot` and converting the disk root to incore btree format. Actual extents are read lazily later.

## Memory Management

- `xfs_broot_alloc` allocates an incore btree root.
- `xfs_broot_realloc` resizes or frees the root, using allocate-copy-free when shrinking.
- `xfs_idata_realloc` resizes local fork data and updates `if_bytes`.
- `xfs_idestroy_fork` frees local data, btree roots, and extent trees according to fork format.
- `xfs_ifork_zap_attr` destroys and resets the attr fork.

## Flushing Forks

`xfs_iflush_fork` writes dirty fork contents into the dinode according to the current fork format, with format taking precedence over log flags:

- local data copies `if_data`
- extent format copies non-delalloc extents through `xfs_iextents_copy`
- btree format converts incore btree root to disk bmdr root
- device format writes the device id
- metadata-btree format calls realtime metadata-specific flush helpers

`xfs_iextents_copy` skips delayed allocation records because they are incore only and asserts each written extent validates.

## CoW And Verification

`xfs_ifork_init_cow` allocates and initializes the CoW fork for reflink inodes.

`xfs_ifork_verify_local_data` validates local directory and symlink contents using directory and symlink shortform verifiers.

`xfs_ifork_verify_local_attr` validates shortform attr contents and requires an attr fork.

## Extent Count Limits

`xfs_iext_count_extend` checks whether adding extents would overflow the fork's extent count. If the filesystem supports large extent counters and the inode is not already upgraded, it sets `XFS_DIFLAG2_NREXT64` and logs the inode core. CoW forks are exempt.

`xfs_ifork_is_realtime` reports whether a mapping belongs to the realtime device; attr forks are never realtime.

## Dependencies

This file integrates with bmap btree conversion, incore extent tree APIs, bmap extent validation, shortform dir/attr/symlink verifiers, realtime metadata btree handlers, transaction logging, and inode health reporting.

## Research Notes

The release/acquire pairing around `if_needextents` and fork format is a key concurrency contract shared with `xfs_need_iread_extents`. Another central risk is ensuring delayed allocation extents remain incore-only and are not serialized into the dinode.
