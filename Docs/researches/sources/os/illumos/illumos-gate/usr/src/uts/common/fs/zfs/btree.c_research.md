# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/btree.c

## Scope

Implements the illumos ZFS generic B-tree container: creation, lookup, insertion, removal, iteration, destructive traversal, clearing, and optional verification/debug poisoning.

Read completely: 2,173 lines.

## Core Model

`zfs_btree_t` owns a comparator, element size, computed leaf capacity, root pointer, tree height, element/node counts, and `bt_bulk` state for append-heavy bulk insertion.

Node types are distinguished by `bth_first`:

- Core nodes have `bth_first == -1`, store separator elements and child pointers.
- Leaf nodes store actual elements in a movable window inside a fixed-size leaf allocation.

The implementation stores element bytes directly with `memcpy`/`memmove`; elements must be plain copyable values whose comparator defines a strict order.

## Main APIs

Lifecycle:

- `zfs_btree_init()` creates the leaf kmem cache.
- `zfs_btree_fini()` destroys the cache.
- `zfs_btree_create()` initializes a tree.
- `zfs_btree_destroy()` asserts the tree is empty.
- `zfs_btree_clear()` recursively frees all nodes.

Lookup and iteration:

- `zfs_btree_find()` searches for a value and optionally returns an insertion/removal index.
- `zfs_btree_first()` and `zfs_btree_last()` return boundary elements.
- `zfs_btree_next()` and `zfs_btree_prev()` advance from an index.
- `zfs_btree_get()` returns the element at an index.
- `zfs_btree_numnodes()` returns the element count despite the name.

Mutation:

- `zfs_btree_add()` finds an insertion point and inserts a new value.
- `zfs_btree_add_idx()` inserts at a known index.
- `zfs_btree_remove()` finds and removes a value.
- `zfs_btree_remove_idx()` removes at a known index.
- `zfs_btree_destroy_nodes()` destructively iterates all elements while freeing nodes as traversal finishes with them.

Verification:

- `zfs_btree_verify()` dispatches staged checks based on `zfs_btree_verify_intensity`.

## Control Flow

Lookup descends from the root, binary-searching core separators with `zfs_btree_find_in_buf()`, then searching the target leaf. During bulk mode, it optimizes for searches near the last leaf.

Insertion handles three cases:

- Empty tree: allocate a leaf root.
- Leaf insertion: grow the movable leaf window, or split the full leaf and insert a separator into the parent.
- Core insertion: replace the separator with the new value and insert the old separator into the first slot of the right subtree.

Leaf and core splits choose half-full distribution normally, or a roughly three-quarter/one-quarter distribution during bulk insertion. Parent insertion can recursively split core nodes and create a new root.

`zfs_btree_bulk_finish()` exits bulk mode by rebalancing underfull last leaf/core nodes from their left neighbors until occupancy invariants are restored.

Removal first converts core-node removal into leaf removal by replacing the separator with the predecessor from the left subtree. Leaf removal then shrinks in place when possible, borrows from a left or right sibling when available, or merges siblings and recursively removes a separator from the parent. Core removal uses the same borrow/merge strategy and can promote a child when the root collapses.

Iteration walks leaf-local entries first, then climbs parent links to find the next separator or descends into subtrees. The same helper supports `zfs_btree_destroy_nodes()` with a callback that frees nodes after traversal no longer needs them.

## Verification Levels

`zfs_btree_verify_intensity` controls cumulative checks:

- 1: uniform tree height and node count.
- 2: child parent pointers.
- 3: occupancy/count invariants and total element count.
- 4: strict ordering and separator correctness through comparator calls.
- 5: unused-memory poisoning checks in debug builds.

Debug poison uses `0x0f` for unused element bytes and `BTREE_POISON` for unused core child pointers.

## Dependencies

Depends on ZFS/illumos allocation, `kmem_cache`, assertions, panic/verify macros, `sys/btree.h` for structure layout and capacities, and `sys/bitops.h` alignment helpers.

## Invariants And Risks

- Comparator correctness is critical; ordering verification expects normalized negative/positive behavior in several places.
- `zfs_btree_index_t` values can be invalidated by structural mutations, especially bulk-finish and removal.
- Bulk mode temporarily relaxes non-root minimum occupancy for the final nodes.
- Split/merge paths must maintain parent pointers and separator values precisely.
- Borrowing is only implemented from siblings with the same parent.
- `zfs_btree_destroy_nodes()` invalidates normal tree operations until it completes and returns `NULL`.
