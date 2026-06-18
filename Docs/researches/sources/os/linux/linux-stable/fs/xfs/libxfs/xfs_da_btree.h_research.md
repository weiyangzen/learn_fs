# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_btree.h

## Role
`xfs_da_btree.h` declares the shared directory/attribute btree interface, search state, operation arguments, and geometry used by XFS directory and extended attribute code.

## Main Definitions
- `struct xfs_da_geometry` describes DA block size, fsblock count, header sizes, maximum entries, magic free-space percentage, directory logical segment starts, and fork extent limits.
- `enum xfs_dacmp` models name comparison outcomes: different, exact, or case-insensitive match.
- `struct xfs_da_args` is the common operation context for directory and attribute actions. It carries the name, optional new name/value, inode, transaction, owner, hash, fork selector, remote attr tracking fields, and operation flags.
- `XFS_DA_OP_*` flags describe operation intent such as just-check, replace, add-name, no-entry-ok, case-insensitive lookup, recovery, and logged operation.
- `struct xfs_da_state_blk`, `struct xfs_da_state_path`, and `struct xfs_da_state` model the active and alternate paths through DA btrees during lookup, split, and join operations.
- `struct xfs_da3_icnode_hdr` is the in-core abstraction for v2/v3 node headers and points directly at on-disk btree entries.

## Exported API
- Growth and shrinkage: `xfs_da3_node_create`, `xfs_da3_split`, `xfs_da3_join`, `xfs_da3_fixhashpath`, and `xfs_attr3_node_entry_remove`.
- Lookup/path movement: `xfs_da3_node_lookup_int` and `xfs_da3_path_shift`.
- Block and inode management: `xfs_da3_blk_link`, `xfs_da3_node_read`, `xfs_da3_node_read_mapped`, `xfs_da_grow_inode`, `xfs_da_grow_inode_int`, `xfs_da_get_buf`, `xfs_da_read_buf`, `xfs_da_reada_buf`, and `xfs_da_shrink_inode`.
- Utility helpers: `xfs_da_buf_copy`, `xfs_da_hashname`, `xfs_da_compname`, state allocation/free/reset, header conversion, and owner/header checks.

## Design Notes
- `xfs_da_args` deliberately combines directory and xattr fields, which lets the btree code operate on either fork with one algorithm.
- Geometry is passed rather than recomputed so directory and attribute forks can differ in block sizing and layout while sharing code.
- `XFS_DA_LOGOFF` and `XFS_DA_LOGRANGE` standardize byte-range logging of modified metadata fields.

## Dependencies
The header depends on format constants from `xfs_da_format.h` and is included by directory, attr, and DA btree implementations. It exposes `xfs_da_state_cache`, the slab cache backing large per-operation state objects.

## Research Notes
This header is the best compact map of the DA btree subsystem. The key concept is that `xfs_da_args` describes the operation while `xfs_da_state` describes the btree path and temporary split/join blocks.
