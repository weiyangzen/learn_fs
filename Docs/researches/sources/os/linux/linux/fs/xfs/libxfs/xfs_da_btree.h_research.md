# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.h

## Scope

This header declares the shared directory/attribute Btree geometry, operation arguments, search comparison results, tree traversal state, in-core v3 node header abstraction, logging range helpers, and the public DA Btree API used by directory and attribute code.

## Main Interfaces

- `struct xfs_da_geometry` describes DA block geometry, node capacity, directory data/leaf/free address-space boundaries, and maximum fork extents.
- `struct xfs_da_args` carries a single directory or attribute operation: names, values, inode, transaction, owner, hash, fork, block/index outputs, remote attr metadata, flags, and comparison result.
- `enum xfs_dacmp` reports different, exact, or case-insensitive name matches.
- Operation flags include just-check, replace, add-name, ok-no-entry, case-insensitive lookup, recovery, and logged intent operation.
- `xfs_da_state_blk`, `xfs_da_state_path`, and `xfs_da_state` hold traversal/split/join state.
- `struct xfs_da3_icnode_hdr` abstracts v2/v3 node header fields and points to node entries.
- Declares split/join/search/path/buffer/allocation/hash/state APIs.

## Data Model

The geometry is per mount and differs between the data fork directory Btree and the attribute fork. Directory geometry can span logical data, leaf, and free spaces; attribute geometry is one filesystem block. `xfs_da_args` is the central cross-layer argument object used by generic DA code, directory implementations, and attribute implementations.

## Dependencies

Forward declares inode and transaction types and depends on DA format definitions for magic values, block numbers, hash types, and node depth. Consumers include `xfs_da_btree.c`, directory shortform/block/leaf/node files, and attribute leaf/node/remote code.

## Risks And Invariants

- `XFS_DA_NODE_MAXDEPTH` is a structural limit assumed by traversal arrays and corruption checks.
- `xfs_da_args` fields are both input and output; callers must initialize owner, fork, geometry, hash, operation flags, and transaction consistently.
- `XFS_DA_LOGRANGE` computes byte ranges for metadata logging; incorrect base/size use can under-log metadata changes.
- State path arrays must match active depth and must not retain stale buffer pointers across reset/free.
