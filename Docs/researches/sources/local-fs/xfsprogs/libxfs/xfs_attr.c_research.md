# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr.c

## Purpose

`xfs_attr.c` implements high-level extended attribute get/set/remove/replace operations for XFS. It dispatches between shortform, single-leaf, and node/remote-value formats; computes transaction reservations; manages resumable delayed attribute intents; handles atomic replacement semantics; and validates namespaces and names.

The file is structured around three storage formats:
- shortform attributes packed into the inode attr fork.
- one-block leaf attributes.
- multi-block node format, including single leaf blocks with remote value extents.

## Format Detection and Read Paths

- `xfs_inode_hasattr` checks if an inode has a non-empty attr fork.
- `xfs_attr_is_leaf` verifies the attr fork is exactly one extent at logical offset 0 with blockcount 1.
- `xfs_attr_get_ilocked` requires an inode lock, loads attr extents, and dispatches to shortform, leaf, or node get routines.
- `xfs_attr_get` prepares owner, geometry, fork, hash, and lookup flags; takes the attr-map shared lock; calls `xfs_attr_get_ilocked`; and releases the lock.
- `xfs_attr_leaf_get` reads the single leaf block, performs lookup, and fetches the value.
- `xfs_attr_node_get` allocates DA state, searches the node tree, fetches local or remote value from the found leaf, releases path buffers, and frees state.

## Size and Reservation Logic

- `xfs_attr_calc_size` computes required blocks for a new attr. It accounts for leaf entry size, double-split possibility for large local entries, remote value blocks, and attr fork extent expansion.
- `xfs_attr_set_resv` computes permanent log reservation for set/replace/upsert based on metadata and remote transaction reservation components.
- `xfs_attr_add_fork` creates an attribute fork in a transaction if one does not already exist.

## Hashing and Validation

- `xfs_attr_hashname` uses generic directory/attribute hashing.
- `xfs_attr_hashval` delegates parent-pointer attrs to `xfs_parent_hashattr`; otherwise hashes the name.
- `xfs_attr_check_namespace` enforces at most one on-disk namespace bit.
- `xfs_attr_namecheck` enforces namespace validity, `MAXNAMELEN` limit, no embedded NULs for normal attrs, and delegates parent pointer names to parent validation.

## Shortform Paths

- `xfs_attr_try_sf_addname` creates shortform storage if needed, tries to add, updates ctime on success, and sets sync transaction behavior for wsync mounts.
- `xfs_attr_sf_addname` is the delayed-state wrapper. If shortform add returns `-ENOSPC`, it converts shortform to leaf and advances state to leaf add.
- `xfs_attr_shortform_addname` handles replacement-in-shortform by removing the old entry first, checks maximum entry component sizes, checks whether the new total fits in the inode fork, and adds the entry.
- `xfs_attr_sf_totsize` returns the shortform total size.
- `xfs_attr_setname`, `xfs_attr_removename`, and `xfs_attr_replacename` use shortform shortcuts when no remote blocks and the current fork can support a one-transaction update; otherwise they enqueue deferred attr operations.

## Leaf and Node Add/Replace Paths

Leaf:
- `xfs_attr_leaf_addname` reads the leaf block, looks up the name, enforces create/replace semantics, saves existing remote-block metadata for replacement, attempts leaf insertion, converts to node if the leaf cannot fit the new entry, and advances state to remote-value allocation or replacement cleanup.

Node:
- `xfs_attr_node_addname` finds the insertion/replacement target and calls `xfs_attr_node_try_addname`.
- `xfs_attr_node_addname_find_attr` allocates/resets DA state, looks up the attr, enforces replace semantics, and saves old remote-block state for replacement.
- `xfs_attr_node_try_addname` attempts leaf insertion at the found path. If a single leaf with remote values needs true node conversion, it returns `1`. Otherwise it splits DA btree nodes as needed or fixes hash paths, then frees state.

Remote values:
- `xfs_attr_rmtval_alloc` allocates remote blocks one step at a time, writes the remote value, advances the delayed state, and clears the incomplete flag when creation is complete and not part of a rename/replace flow.

Atomic replacement:
- `xfs_attr_save_rmt_blk` saves old attr remote block metadata in secondary fields and clears current remote metadata for the new attr.
- `xfs_attr_restore_rmt_blk` restores old attr remote metadata before old-value removal.
- `xfs_attr_complete_op` consumes `XFS_DA_OP_REPLACE`, updates parent-pointer replacement arguments when needed, clears `XFS_ATTR_INCOMPLETE`, and chooses either the next replace state or done.
- `xfs_attr_update_pptr_replace_args` swaps canonical name/value fields to the new parent-pointer name/value after the remove phase.

## Remove Paths

- `xfs_attr_leaf_removename` removes an attr from a single leaf block and shrinks to shortform if all entries fit.
- `xfs_attr_node_removename_setup` looks up the node attr, marks it incomplete, and invalidates remote blocks if present.
- `xfs_attr_leaf_mark_incomplete` fills/resets DA state metadata and sets the leaf incomplete flag.
- `xfs_attr_leaf_remove_attr` removes a leaf attr already located by replacement state and shrinks to shortform if possible.
- `xfs_attr_leaf_shrink` collapses a leaf-format attr fork to shortform when possible after node removal.
- `xfs_attr_node_removename` removes the name from a node leaf and fixes hash values on the path.
- `xfs_attr_node_remove_attr` refinds an incomplete old attr, removes it, joins/collapses DA btree nodes if possible, and frees DA state.

## Delayed Attribute State Machine

`xfs_attr_set_iter` is the main resumable state machine for delayed attr operations. It dispatches on `xattri_dela_state` and returns after work that requires a transaction roll.

State groups:
- initial add states: `XFS_DAS_SF_ADD`, `XFS_DAS_LEAF_ADD`, `XFS_DAS_NODE_ADD`
- initial remove states: `XFS_DAS_SF_REMOVE`, `XFS_DAS_LEAF_REMOVE`, `XFS_DAS_NODE_REMOVE`
- remote allocation states: `XFS_DAS_LEAF_SET_RMT`, `XFS_DAS_LEAF_ALLOC_RMT`, `XFS_DAS_NODE_SET_RMT`, `XFS_DAS_NODE_ALLOC_RMT`
- replacement flip/remove states: `XFS_DAS_LEAF_REPLACE`, `XFS_DAS_NODE_REPLACE`, `XFS_DAS_LEAF_REMOVE_OLD`, `XFS_DAS_NODE_REMOVE_OLD`, `XFS_DAS_LEAF_REMOVE_RMT`, `XFS_DAS_NODE_REMOVE_RMT`, `XFS_DAS_LEAF_REMOVE_ATTR`, `XFS_DAS_NODE_REMOVE_ATTR`

Behavior:
- Shortform/leaf/node adds return after one format-specific step.
- Remove states either complete or advance into add states for replace flows.
- Remote allocation and removal states can repeat across transaction rolls.
- Replace states flip incomplete flags atomically, then remove old remote blocks and old leaf entries.
- Recovery-specific `ENOATTR` during node remove can be tolerated and converted into the next add/done state.

The file contains disabled state refill code under `#if 0`; active builds use a stub `xfs_attr_fillstate` returning success. Comments explain that name-path state refill was an optimization sidelined by combined state-machine work.

## Public Set/Remove Entry Point

`xfs_attr_set` is the public mutator. It:

1. Determines operation type: remove, upsert, create, or replace.
2. Computes reservation and remote block needs.
3. Adds an attr fork if needed for set-like operations.
4. Allocates an inode transaction.
5. Extends incore extent-count reservation for attr fork manipulations.
6. Looks up the current attr.
7. Enforces create/replace/remove semantics.
8. Calls the shortform shortcut or queues deferred set/remove/replace work.
9. Applies sync mount behavior, updates ctime, logs inode core, commits, and unlocks.

Expected semantic errors:
- `XFS_ATTRUPDATE_CREATE` returns `-EEXIST` if the attr exists.
- `XFS_ATTRUPDATE_REPLACE` returns `-ENOATTR` if absent.
- `XFS_ATTRUPDATE_REMOVE` returns `-ENOATTR` if absent.

## Dependencies

This file relies on DA btree code, attr leaf and shortform helpers, remote attr helpers, inode fork/bmap code, transaction reservation and inode transaction helpers, quota attachment expectations, deferred intent infrastructure, parent pointer hashing/validation, tracepoints, and mount feature flags.

## Invariants and Risks

- Attr fork extents must be loaded before `xfs_attr_is_leaf`.
- Replace operations depend on incomplete flags for crash-consistent visibility.
- Remote value allocation/removal is transaction-roll sensitive and must preserve state fields correctly.
- Parent-pointer replace has distinct name/value field handling.
- Shortform fast paths must fall back to deferred intents on `-ENOSPC` without losing create/replace semantics.
- Node removal of incomplete attrs must set the filter to find the old incomplete entry.
