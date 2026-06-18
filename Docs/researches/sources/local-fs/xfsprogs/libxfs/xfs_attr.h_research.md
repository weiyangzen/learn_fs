# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr.h

## Purpose

`xfs_attr.h` declares the XFS extended attribute interface, list context, delayed attribute state machine, attr intent structure, update operation enum, hashing helpers, namespace/name validation, and internal helpers shared across libxfs attr implementation files.

## Attribute Model

The header documents two attr storage forms:
- Large attr lists use DA btrees with data in leaf nodes. Names hash to integer keys, duplicate hash keys are allowed, and internal links are logical file-block offsets.
- Small attr lists are packed into the inode literal area as shortform data.

It defines `ATTR_MAX_VALUELEN` as 64 KiB for attr values and attr-list buffers.

## Listing Types

- `struct xfs_attrlist_cursor_kern`: kernel/internal cursor with hash value, block, equal-hash offset, padding matching user ABI, and initialized flag.
- `put_listent_func_t`: callback for emitting list entries.
- `struct xfs_attr_list_context`: carries transaction, inode, cursor, output buffer, abort/error state, incomplete-entry allowance, count/dupcnt/buffer sizing, first-used buffer byte, namespace filter, resync flag, output callback, and index.

## Delayed Attribute State Machine

`enum xfs_delattr_state` enumerates resumable states for delayed set/remove/replace operations:

- `XFS_DAS_UNINIT`
- initial states: `XFS_DAS_SF_ADD`, `XFS_DAS_SF_REMOVE`, `XFS_DAS_LEAF_ADD`, `XFS_DAS_LEAF_REMOVE`, `XFS_DAS_NODE_ADD`, `XFS_DAS_NODE_REMOVE`
- leaf sequence: `XFS_DAS_LEAF_SET_RMT`, `XFS_DAS_LEAF_ALLOC_RMT`, `XFS_DAS_LEAF_REPLACE`, `XFS_DAS_LEAF_REMOVE_OLD`, `XFS_DAS_LEAF_REMOVE_RMT`, `XFS_DAS_LEAF_REMOVE_ATTR`
- node sequence: `XFS_DAS_NODE_SET_RMT`, `XFS_DAS_NODE_ALLOC_RMT`, `XFS_DAS_NODE_REPLACE`, `XFS_DAS_NODE_REMOVE_OLD`, `XFS_DAS_NODE_REMOVE_RMT`, `XFS_DAS_NODE_REMOVE_ATTR`
- `XFS_DAS_DONE`

The large diagrams in the header are significant implementation documentation. They describe remove and set operation state transitions, where `-EAGAIN` causes transaction roll and reentry, and how subroutine states are owned by the called function until it completes.

`XFS_DAS_STRINGS` maps enum values to trace/debug strings.

## Attr Intent Structure

`struct xfs_attr_intent` tracks deferred attr work:
- list node for intent logging.
- DA state pointer for node operations.
- DA args pointer.
- shared logged name/value buffer.
- current delayed state.
- attr operation flags from `XFS_ATTRI_OP_FLAGS_*`.
- remote block allocation progress: logical block, block count, and current mapping.

`xfs_attr_intent_op` masks `xattri_op_flags` to the operation type.

## Public APIs

High-level:
- `xfs_attr_inactive`
- `xfs_attr_list_ilocked`
- `xfs_attr_list`
- `xfs_inode_hasattr`
- `xfs_attr_is_leaf`
- `xfs_attr_get_ilocked`
- `xfs_attr_get`
- `xfs_attr_set`

Delayed operation iterators:
- `xfs_attr_set_iter`
- `xfs_attr_remove_iter`

Validation and sizing:
- `xfs_attr_check_namespace`
- `xfs_attr_namecheck`
- `xfs_attr_calc_size`
- `xfs_attr_set_resv`

Format/fork helpers:
- `xfs_attr_sf_totsize`
- `xfs_attr_add_fork`
- `xfs_attr_setname`
- `xfs_attr_removename`
- `xfs_attr_replacename`

Hashing:
- `xfs_attr_hashname`
- `xfs_attr_hashval`
- `xfs_attr_sethash` inline helper.

Cache lifecycle:
- `xfs_attr_intent_cache`
- `xfs_attr_intent_init_cache`
- `xfs_attr_intent_destroy_cache`

## Update Operation Enum

`enum xfs_attr_update` defines public mutation semantics:
- `XFS_ATTRUPDATE_REMOVE`
- `XFS_ATTRUPDATE_UPSERT`
- `XFS_ATTRUPDATE_CREATE`
- `XFS_ATTRUPDATE_REPLACE`

## Inline State Helpers

- `xfs_attr_is_shortform` treats local format or zero-extent extents format as shortform/nonexistent attr data.
- `xfs_attr_init_add_state` sets `XFS_DA_OP_ADDNAME` and chooses shortform, leaf, node, or done if a pure remove has eliminated the attr fork.
- `xfs_attr_init_remove_state` chooses shortform, leaf, or node remove state.
- `xfs_attr_init_replace_state` sets add+replace flags and chooses remove-first when logged attrs are enabled, otherwise add-first.
- `xfs_attr_sethash` computes and stores `args->hashval` from mount, namespace, name, value, and value length.

## Integration Notes

This header ties together `xfs_attr.c`, attr shortform/leaf/remote helpers, deferred log intent code, parent pointer support, inode fork logic, and attr listing code. The state machine documentation is part of the contract: callers must retry after `-EAGAIN` using the stored state until completion or error.

## Risk Areas

- The leaf and node state enum sequences are intentionally parallel; code increments state values to move through remote allocation/removal phases, so reordering enum values is risky.
- Logged attr replacement starts with removal to preserve recoverable consistency; non-logged replacement can add first.
- `xfs_attr_init_add_state` has a special no-attr-fork case for pure remove completion.
- Namespace validation permits fewer than two namespace bits, not exactly one, because some attrs may use the default namespace.
