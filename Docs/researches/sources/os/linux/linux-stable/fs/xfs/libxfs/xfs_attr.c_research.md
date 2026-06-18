# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.c

## Purpose

`xfs_attr.c` is the main libxfs extended-attribute orchestration layer. It exposes inode attribute presence checks, get/set/remove entry points, attribute fork creation, namespace/name validation, hashing, and the deferred xattr state machine that spans shortform, leaf, node, and remote-value operations.

## Main APIs and Data Flow

- `xfs_inode_hasattr` and `xfs_attr_is_leaf` classify whether an inode has any attr data and whether the attr fork is a single local leaf block. `xfs_attr_is_leaf` requires loaded attr extents and verifies that the only extent starts at attr fork block 0 and is one block long.
- `xfs_attr_get` prepares `xfs_da_args` fields (`owner`, geometry, fork, hash, `OKNOENT`), takes the attr mapping lock, and calls `xfs_attr_get_ilocked`.
- `xfs_attr_get_ilocked` dispatches by attr fork format: shortform values use `xfs_attr_shortform_getvalue`, single-leaf forks use `xfs_attr_leaf_get`, and larger forks use `xfs_attr_node_get`.
- `xfs_attr_set` is the public mutation entry point for remove, upsert, create, and replace. It computes reservations, creates the attr fork if needed, extends incore extent capacity, does an existence lookup, and selects remove/set/replace helpers.
- `xfs_attr_set_iter` runs deferred attr intents across transaction rolls. It handles add/remove states for shortform, leaf, and node formats, remote-value allocation/removal, replace flag flips, and final cleanup.

## Format and Operation Selection

The file uses shortform fast paths when possible. `xfs_attr_can_shortcut` allows direct single-transaction changes only when the inode has an attr fork and it is shortform. `xfs_attr_setname`, `xfs_attr_removename`, and `xfs_attr_replacename` try this path and otherwise enqueue deferred work with `xfs_attr_defer_add`.

For non-shortform operations, the code chooses between:

- leaf operations for one-block attr forks without remote blocks;
- node operations for btree attr forks and for leaf-plus-remote cases that cannot be distinguished by extent count alone;
- remote value states when `args->rmtblkno` / `rmtblkcnt` are set by leaf insertion.

## Deferred State Machine

The state machine uses `enum xfs_delattr_state` from `xfs_attr.h`. Important transitions include:

- `XFS_DAS_SF_ADD` attempts shortform insertion and converts to leaf on `-ENOSPC`.
- `XFS_DAS_LEAF_ADD` inserts into a single leaf, converts to node if full, or advances to remote allocation / replace / done.
- `XFS_DAS_NODE_ADD` looks up the insertion point and splits or converts as needed.
- remove states mark node entries incomplete, invalidate remote buffers, unmap remote extents, remove the leaf entry, and shrink leaf/node structures if possible.
- replace states use INCOMPLETE flag flipping to make the new value visible atomically before deleting the old one.

`xfs_attr_complete_op` clears replace state and the incomplete filter. Parent-pointer replace (`XFS_ATTRI_OP_FLAGS_PPTR_REPLACE`) updates the canonical name/value fields after the remove phase.

## Dependencies and Integration

This file sits above:

- `xfs_attr_leaf.c` for shortform, leaf, lookup, conversion, and INCOMPLETE flag operations;
- `xfs_attr_remote.c` for remote value extent allocation, synchronous value writes, invalidation, and unmapping;
- directory/attribute btree code (`xfs_da3_node_lookup_int`, `xfs_da3_split`, `xfs_da3_join`, `xfs_da_state_*`);
- transaction, quota, bmap, and intent-log infrastructure.

Parent-pointer support is integrated via `xfs_parent_hashattr`, `xfs_parent_namecheck`, and the special PPTR replace path.

## Invariants and Risks

- Mutations assume callers initialized `xfs_da_args`, attached dquots, and do not hold inode locks before `xfs_attr_set`.
- `xfs_attr_lookup` returns `-EEXIST` for found and `-ENOATTR` for absent, which is intentionally inverted from ordinary success semantics and must be handled carefully.
- Replace operations depend on correct preservation of `blkno/index` for the old attr and `blkno2/index2` for the new attr.
- Remote attrs rely on INCOMPLETE state until value blocks are fully allocated and synchronously written.
- The disabled `xfs_attr_fillstate` optimization leaves a stub. Current correctness does not depend on buffer reattachment optimization, but comments show this area is historically subtle around transaction rolls.

## Testing Notes

High-value tests include create/replace/remove across shortform-to-leaf and leaf-to-node boundaries, remote value allocation and removal across transaction rolls, parent-pointer replace, logged attr recovery, and shutdown/error injection through attr leaf-to-node and remote-value paths.
