# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr.h

## Purpose

`xfs_attr.h` declares the public and cross-file interface for XFS extended attributes. It defines list cursor/context state, mutation operation types, the delayed-attribute state enum, the delayed intent structure, helper functions for initial state selection, and prototypes implemented by `xfs_attr.c` and related attr files.

## Main Types

- `ATTR_MAX_VALUELEN` caps attribute value buffers at 64 KiB.
- `struct xfs_attrlist_cursor_kern` is the kernel-side attr list cursor, tracking hash, block suggestion, duplicate offset, and initialization.
- `put_listent_func_t` abstracts list-output formatting.
- `struct xfs_attr_list_context` carries transaction, inode, cursor, output buffer, filter, iteration state, duplicate-hash tracking, and an `allow_incomplete` switch.
- `enum xfs_delattr_state` names all resumable delayed-attribute states. Leaf and node remote/replace/remove sequences are deliberately aligned so arithmetic on state values can advance between corresponding stages.
- `struct xfs_attr_intent` is the in-memory delayed operation. It holds list linkage, optional directory/attr btree state, da args, shared log name/value storage, current delayed state, attr intent operation flags, and remote extent allocation progress.
- `enum xfs_attr_update` represents remove, upsert, create-only, and replace-only requests.

## State Selection Helpers

`xfs_attr_init_add_state`, `xfs_attr_init_remove_state`, and `xfs_attr_init_replace_state` choose the first state for an operation based on the current attr fork format and logging mode. Logged replace begins with removal of the old attr so recovery always has enough logged information to finish consistently. Non-logged replace begins with adding the new attr and uses incomplete flag flips.

`xfs_attr_is_shortform` treats local-format forks and empty extents-format attr forks as shortform candidates. `xfs_attr_sethash` computes the correct hash for normal xattrs or parent-pointer attrs.

## Exported Interfaces

The header exposes:

- lookup and mutation entry points: `xfs_attr_get`, `xfs_attr_get_ilocked`, `xfs_attr_set`, `xfs_attr_set_iter`, `xfs_attr_remove_iter`;
- lifecycle/listing hooks: `xfs_attr_inactive`, `xfs_attr_list`, `xfs_attr_list_ilocked`;
- fork and format helpers: `xfs_inode_hasattr`, `xfs_attr_is_leaf`, `xfs_attr_add_fork`;
- validation and hashing: `xfs_attr_check_namespace`, `xfs_attr_namecheck`, `xfs_attr_hashname`, `xfs_attr_hashval`;
- reservation/size helpers: `xfs_attr_calc_size`, `xfs_attr_set_resv`;
- lower-level mutation helpers for set/remove/replace names.

## Dependencies and Integration

The declarations bind together `xfs_attr.c`, `xfs_attr_leaf.c`, `xfs_attr_remote.c`, attr intent logging, parent pointers, da btree code, and transaction reservation logic. Consumers must include this header to construct delayed attr intents or call the high-level mutation API.

## Invariants and Risks

- Namespace validation permits at most one on-disk namespace bit.
- State enum ordering matters. Leaf and node sequences must remain synchronized with state-increment logic in `xfs_attr_set_iter`.
- The replace-state helpers mutate `args->op_flags`; callers must not assume flags are unchanged after initialization or completion.
- `xfs_attr_intent` remote allocation fields are part of a resumable transaction-roll protocol and must stay consistent with `xfs_attr_remote.c`.
