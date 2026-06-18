# File Research: sources/os/linux/linux/fs/btrfs/ulist.h

## Purpose

`ulist.h` declares Btrfs' unique-`u64` list container. It exposes the data structures because callers commonly allocate `struct ulist` and iterators directly.

## Public Structures

`struct ulist_iterator` contains the current list cursor used by `ulist_next()`.

`struct ulist_node` is one element. It stores a unique `u64 val`, an auxiliary `u64 aux`, a linked-list node, and an rb-tree node.

`struct ulist` stores the element count, list head, rb-tree root, and optional preallocated node.

## Public API

The header declares:

- initialization and cleanup: `ulist_init()`, `ulist_release()`, `ulist_reinit()`, `ulist_alloc()`, `ulist_free()`.
- allocation preparation: `ulist_prealloc()`.
- mutation: `ulist_add()`, `ulist_add_merge()`, `ulist_del()`.
- iteration: `ulist_next()`.

`ULIST_ITER_INIT()` resets an iterator before enumeration.

## Pointer Auxiliary Helper

`ulist_add_merge_ptr()` adapts `ulist_add_merge()` for pointer auxiliary values. On 64-bit builds it casts the pointer storage directly through `u64 *`. On 32-bit builds it uses a temporary 64-bit value and converts through `uintptr_t`, avoiding an invalid direct 64-bit pointer alias.

## Filesystem Role

The header provides the public contract for a small Btrfs traversal helper. The type is intentionally simple: uniqueness comes from the rb-tree, traversal from the linked list, and synchronization from the caller.
