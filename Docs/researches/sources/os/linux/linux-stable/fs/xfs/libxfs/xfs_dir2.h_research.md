# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.h

## Role
`xfs_dir2.h` declares the generic directory API, directory format enumeration, directory offset conversion helpers, live-update hook interface, and higher-level child update structures.

## Main Definitions
- `xfs_name_dotdot` and `xfs_name_dot` are exported canonical directory names.
- `xfs_dir2_samename` compares two `struct xfs_name` values by length and bytes.
- `enum xfs_dir2_fmt` enumerates shortform, block, leaf, node, and error formats.
- `struct xfs_dir_update_params`, `struct xfs_dir_hook`, and hook helpers are available under `CONFIG_XFS_LIVE_HOOKS`.
- `struct xfs_dir_update` packages parent directory, entry name, child inode, and optional parent-pointer args for high-level directory updates.

## Exported API
- Mount/startup: `xfs_dir_startup`, `xfs_da_mount`, and `xfs_da_unmount`.
- Core operations: `xfs_dir_init`, `xfs_dir_createname`, `xfs_dir_lookup`, `xfs_dir_removename`, `xfs_dir_replace`, and `xfs_dir_canenter`.
- Args-based dispatchers: `xfs_dir_lookup_args`, `xfs_dir_createname_args`, `xfs_dir_removename_args`, and `xfs_dir_replace_args`.
- Conversion/shrink/data operations: `xfs_dir2_sf_to_block`, `xfs_dir2_shrink_inode`, data free-space logging and allocation helpers, data/leaf/block header checks, and buffer ops declarations.
- High-level child updates: `xfs_dir_create_child`, `xfs_dir_add_child`, `xfs_dir_remove_child`, `xfs_dir_exchange_children`, and `xfs_dir_rename_children`.

## Conversion Helpers
The header provides inline conversions among directory byte offsets, dataptrs, logical directory blocks, DA blocks, and block offsets. These helpers encode the XFS directory address model where data, leaf, and free spaces are separated by large logical offsets.

## Other Helpers
- `xfs_dir2_block_tail_p` and `xfs_dir2_leaf_tail_p` compute tail pointers from geometry and block base addresses.
- `XFS_READDIR_BUFSIZE` provides the estimated user buffer size for readdir mapping/readahead heuristics.
- `xfs_ascii_ci_need_xfrm` and `xfs_ascii_ci_xfrm` implement legacy ASCII/Latin uppercase folding for ascii-ci directory hash/compare behavior.

## Dependencies
The header includes `xfs_da_format.h` and `xfs_da_btree.h`, making directory APIs tightly connected to the shared DA format and btree abstractions.

## Research Notes
This header is the public directory contract for libxfs. Its most important technical detail is the set of logical address conversion helpers, because directory data, leaf, and free-space blocks all share one file fork but occupy distinct logical spaces.
