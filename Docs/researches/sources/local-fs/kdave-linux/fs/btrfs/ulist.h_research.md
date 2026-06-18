# File Research: sources/local-fs/kdave-linux/fs/btrfs/ulist.h

## Purpose

`ulist.h` declares the Btrfs unique-`u64` list container used for iterative graph/tree traversal without recursion. It defines the public structs and helper functions implemented in `ulist.c`.

## Public Types

`struct ulist_iterator` stores the current list position for `ulist_next()`.

`struct ulist_node` stores:

- `val`: the unique `u64` key.
- `aux`: auxiliary `u64` data associated with the first insertion.
- `list`: linked-list membership for iteration.
- `rb_node`: rb-tree membership for lookup.

`struct ulist` stores the node count, linked list, rb-tree root, and one preallocated spare node.

## Public APIs

The header declares lifecycle, mutation, deletion, and iteration functions:

- `ulist_init()`
- `ulist_release()`
- `ulist_reinit()`
- `ulist_alloc()`
- `ulist_prealloc()`
- `ulist_free()`
- `ulist_add()`
- `ulist_add_merge()`
- `ulist_del()`
- `ulist_next()`

`ULIST_ITER_INIT()` initializes an iterator by clearing its current list pointer.

## Pointer Auxiliary Helper

`ulist_add_merge_ptr()` wraps `ulist_add_merge()` for pointer auxiliary data. On 64-bit builds it casts the pointer directly through `u64`. On 32-bit builds it uses a temporary `u64` to preserve the helper signature while converting through `uintptr_t`.

## Integration Notes

This header exposes the internal struct layout, so callers can inspect `nnodes` or node fields directly after iteration. It keeps the implementation simple but means layout changes are source-visible.

The key behavioral constraint is external locking: the container itself provides no synchronization.
