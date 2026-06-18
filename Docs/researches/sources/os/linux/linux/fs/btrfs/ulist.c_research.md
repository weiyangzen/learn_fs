# File Research: sources/os/linux/linux/fs/btrfs/ulist.c

## Purpose

`ulist.c` implements a small Btrfs utility container for unique `u64` values with an optional `u64` auxiliary payload. It supports efficient duplicate checks through an rb-tree and iteration through an insertion-order linked list.

The file comments describe its main use case: non-recursive traversal of graphs or trees whose nodes are addressable as 64-bit values, avoiding repeated visits without consuming kernel stack through recursion.

## Container Structure

A `struct ulist` owns:

- `nodes`, a linked list for iteration.
- `root`, an rb-tree keyed by `val` for lookup.
- `nnodes`, the current element count.
- `prealloc`, one optional preallocated node for callers that need to avoid allocation in a later critical section.

Each `struct ulist_node` stores `val`, `aux`, one list node, and one rb-tree node.

## Lifetime Operations

`ulist_init()` initializes a caller-provided `struct ulist`.

`ulist_release()` frees all dynamically allocated nodes and the preallocated node, clears `prealloc`, resets the rb-tree, and reinitializes the list head. It is intended for statically or externally allocated `struct ulist` objects.

`ulist_reinit()` releases contents and then fully initializes the container for reuse.

`ulist_alloc()` allocates and initializes a `struct ulist`.

`ulist_free()` handles NULL, releases all contents, and frees the container itself.

`ulist_prealloc()` allocates a single spare node if none is already present.

## Lookup and rb-tree Helpers

`ulist_node_val_key_cmp()` defines rb-tree ordering by `val`. `ulist_rbtree_search()` uses `rb_find()` to find an existing node.

`ulist_rbtree_insert()` uses `rb_find_add()` and returns `-EEXIST` if a duplicate key already exists. The public add path searches first, so insertion asserts that duplicates are impossible.

`ulist_rbtree_erase()` removes a node from both the rb-tree and list, frees it, and decrements `nnodes`, with a `BUG_ON` guard against underflow.

## Add, Merge, and Delete

`ulist_add()` is a wrapper around `ulist_add_merge()` when the caller does not need the old auxiliary value.

`ulist_add_merge()` searches by `val`. If a node already exists, it optionally returns the existing `aux` through `old_aux` and returns 0. If not found, it consumes `prealloc` or allocates a node, stores `val` and `aux`, inserts into the rb-tree, appends to the linked list, increments `nnodes`, and returns 1. Allocation failure returns `-ENOMEM` and leaves the ulist unchanged.

`ulist_del()` removes an entry only when both `val` and `aux` match. It returns 0 for deletion and 1 when the value is absent or the auxiliary value differs.

## Iteration Semantics

`ulist_next()` walks the linked list using `struct ulist_iterator`. It returns NULL for an empty list or after the final element. The iteration order is the list order, not sorted rb-tree order.

The implementation permits callers to add new elements during enumeration; because new nodes are appended to the list, they will be reached by the running iterator.

## Concurrency Contract

The container performs no internal locking. The comments require caller-provided locking: write locking for mutation and read locking for iteration when rwlocks are used.

## Filesystem Role

`ulist` is a reusable support data structure for Btrfs graph-style algorithms, especially backref and extent relationship walks that need uniqueness, auxiliary metadata, and bounded stack usage.
