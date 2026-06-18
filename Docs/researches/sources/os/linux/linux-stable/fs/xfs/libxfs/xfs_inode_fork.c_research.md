# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.c

## Role
`xfs_inode_fork.c` imports, manages, verifies, flushes, and destroys XFS inode forks. It handles local-format data, extent-format forks, btree-format roots, metadata btree forks, attr forks, CoW forks, and conversion of in-core extents back to disk records.

## Main Responsibilities
- Initialize inline/local forks, including NUL termination for in-core symlink bodies.
- Import local, extents, btree, and metadata-btree fork formats from a dinode.
- Initialize, reset, and destroy attr forks and CoW forks.
- Allocate and resize in-core bmap btree roots.
- Resize local fork data buffers.
- Copy in-core extent records to on-disk bmbt records during inode flush.
- Flush each fork according to its current format and inode log flags.
- Verify shortform directory, symlink, and attr fork contents.
- Check whether a fork can accept additional extents and upgrade to large extent counters if possible.

## Important Functions
- `xfs_iformat_local` copies local fork bytes after checking the size fits in the selected fork region.
- `xfs_iformat_extents` imports inline bmbt records into the in-core extent tree, validating every extent through bmap validation.
- `xfs_iformat_btree` validates and imports an inode-rooted bmap btree root into `if_broot`.
- `xfs_iformat_data_fork` chooses fork import logic based on inode mode and data fork format, including special device handling and metadata-btree dispatch.
- `xfs_iformat_attr_fork` imports the attr fork and zaps it back to empty extents format on failure.
- `xfs_broot_alloc` and `xfs_broot_realloc` manage in-core btree root buffers; shrink uses allocate-copy-free to avoid relying on `krealloc` shrinking behavior.
- `xfs_idata_realloc` resizes local fork data and updates `if_bytes`.
- `xfs_idestroy_fork` frees local data, btree roots, and in-core extent trees.
- `xfs_iextents_copy` skips delayed allocation/null-startblock mappings and writes only real extents to disk format.
- `xfs_iflush_fork` serializes the selected fork based on current format, not merely stale log flags.
- `xfs_iext_count_extend` checks extent-count limits, optionally sets `XFS_DIFLAG2_NREXT64`, and logs the inode core.

## Data and Invariants
- `if_format` controls how `if_data`, `if_broot`, and `if_bytes` are interpreted.
- `if_needextents` uses release/acquire semantics so readers that notice deferred btree extent loading also see the fork format.
- Local regular files are not supported; local data fork verification applies to shortform directories and symlinks.
- Btree-format forks must have enough extents to justify btree format and a nonzero root level within max bmap levels.
- Disk flushing prioritizes current fork format because fork format may have changed after log flags were set.
- CoW fork extent counts are not constrained by on-disk extent counters.

## Error Handling and Corruption Response
- Bad fork sizes, invalid extents, impossible btree roots, or invalid fork formats produce verifier errors, mark inode core sick, and return `-EFSCORRUPTED`.
- Attr fork import failure destroys any partially imported attr fork and resets it to empty extents format.
- Large extent counter upgrade returns `-EFBIG` if limits would be exceeded and the filesystem cannot upgrade.

## Dependencies
This file depends on bmap/bmbt conversion, DA directory and attr shortform verifiers, symlink verifier, realtime metadata btree import/flush helpers, inode log item flags, and the in-core extent tree from `xfs_iext_tree.c`.

## Research Notes
This is the bridge between the dinode fork bytes and XFS’s in-core fork representations. The key behavior is format-driven import/flush with strict validation before any fork contents become trusted.
