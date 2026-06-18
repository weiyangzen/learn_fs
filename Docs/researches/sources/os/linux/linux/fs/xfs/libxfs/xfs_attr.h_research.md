# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.h

## Purpose
Declares the kernel-facing XFS extended attribute API, attr list context, delayed attr intent structure, update operation enum, and delayed attribute state-machine states.

## Main Interfaces
- Listing context: `struct xfs_attr_list_context`, `struct xfs_attrlist_cursor_kern`, `put_listent_func_t`.
- Delayed operation state: `enum xfs_delattr_state`, `struct xfs_attr_intent`, `xfs_attr_intent_op()`.
- Public attr operations: `xfs_attr_get()`, `xfs_attr_set()`, `xfs_attr_set_iter()`, `xfs_attr_remove_iter()`, `xfs_attr_list()`, `xfs_attr_inactive()`.
- Format helpers: `xfs_attr_is_shortform()`, `xfs_attr_init_add_state()`, `xfs_attr_init_remove_state()`, `xfs_attr_init_replace_state()`.
- Hashing and validation: `xfs_attr_hashname()`, `xfs_attr_hashval()`, `xfs_attr_sethash()`, `xfs_attr_namecheck()`.

## Main Contents
The header documents the delayed remove and set state machines with large diagrams. Remove operations progress from format detection through optional remote block invalidation/removal, leaf/node entry removal, tree shrink, and state cleanup. Set operations progress through fork creation, shortform add or conversion, leaf or node insertion, remote value allocation, replace flag flips, old remote block removal, and cleanup.

`enum xfs_delattr_state` encodes initial shortform/leaf/node add and remove states, leaf and node remote set/allocation states, replace states, old-entry removal states, remote removal states, final remove-entry states, and `XFS_DAS_DONE`.

## State And Data Model
`struct xfs_attr_intent` carries a deferred log list node, optional DA state, DA args, shared logged name/value buffer, current delayed state, operation flags, and remote allocation progress (`xattri_lblkno`, `xattri_blkcnt`, `xattri_map`). Inline helpers initialize the correct start state from the current attr fork format and replace/logged mode.

## Integration Points
Included by the attr implementation, remote attr implementation, deferred attr item code, xattr VFS-facing code, parent-pointer code, and attr leaf logic. The header also exposes the `xfs_attr_intent_cache` slab lifecycle and lower-level helpers such as `xfs_attr_add_fork()`, `xfs_attr_setname()`, `xfs_attr_removename()`, and `xfs_attr_replacename()`.

## Notable Behaviors
- `xfs_attr_is_shortform()` treats a zero-extent extents-format attr fork as shortform/nonexistent for upgrade decisions.
- Logged replacement starts from remove state so recovery always has enough log data to complete the operation.
- `xfs_attr_init_add_state()` returns done if a pure remove has already deleted the attr fork.
- The state string macro mirrors the enum for tracing/debugging.

## Risks And Review Focus
- Any insertion or reordering in `enum xfs_delattr_state` can break code that relies on sequential leaf/node state ranges.
- Public prototypes must stay synchronized with deferred attr logging and parent-pointer behavior.
- Cursor and list context fields are ABI-shape sensitive because they mirror user-level list cursor padding.
