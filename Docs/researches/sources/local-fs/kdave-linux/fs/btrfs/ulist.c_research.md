# File Research: sources/local-fs/kdave-linux/fs/btrfs/ulist.c

## Purpose

`ulist.c` implements a small Btrfs utility container for unique `u64` values with an optional `u64` auxiliary payload. It supports insertion, deletion, and iteration while guaranteeing that a value is present at most once.

The intended use is non-recursive traversal of graphs or trees whose nodes are addressable by `u64`, especially metadata tree/block graph enumeration where recursion would be unsafe for kernel stack usage.

## Data Structure

A `struct ulist` combines:

- A linked list, `nodes`, used for iteration and append order.
- An rb-tree, `root`, used for efficient uniqueness lookup by `val`.
- A node count, `nnodes`.
- A single preallocated node slot, `prealloc`, used by callers that want to prepare one allocation before a critical path.

Each `struct ulist_node` stores `val`, `aux`, a list node, and an rb-tree node.

## Lifecycle APIs

`ulist_init()` initializes an externally allocated ulist.

`ulist_release()` frees all nodes and the preallocated spare node, then resets the rb-tree and list head. It does not free the `struct ulist` itself.

`ulist_reinit()` releases and reinitializes a ulist for reuse.

`ulist_alloc()` allocates and initializes a ulist.

`ulist_free()` releases all internal allocations and frees the ulist object. It is NULL-safe.

`ulist_prealloc()` allocates a spare `ulist_node` if one is not already present.

## Mutation APIs

`ulist_add()` inserts a value with auxiliary data and returns:

- `1` if inserted.
- `0` if the value already existed.
- `-ENOMEM` on allocation failure.

`ulist_add_merge()` is the implementation behind `ulist_add()`. If the value already exists and `old_aux` is supplied, it returns the existing auxiliary value through `old_aux` and ignores the new auxiliary value.

`ulist_del()` removes a node only when both `val` and `aux` match. It returns `0` for successful deletion and positive `1` when not found or when the auxiliary value does not match.

Internally, uniqueness is enforced by `ulist_rbtree_search()` and `ulist_rbtree_insert()` using `rb_find()` and `rb_find_add()`.

## Iteration

`ulist_next()` iterates through the linked-list order using a caller-owned `struct ulist_iterator`, initialized with `ULIST_ITER_INIT()` from the header. It returns NULL at end.

The implementation explicitly allows `ulist_add()` during enumeration. Newly appended items are guaranteed to appear later in the same running enumeration because iteration follows the list and insertions append to the tail.

No ordering guarantee is made beyond this traversal property; callers must not rely on numerical order.

## Locking And Dependencies

The file does not implement locking. Callers must provide external synchronization. Comments require write locking for mutation and read locking for iteration when an rwlock is used.

The implementation uses Linux slab allocation and rb-tree helpers, plus Btrfs `ASSERT`/`BUG_ON` diagnostics from `messages.h`.

## Invariants And Risks

The rb-tree and linked list must remain consistent. Every inserted node is in both structures, and every deletion removes it from both. `nnodes` is incremented after insertion and decremented after erase.

The preallocation path transfers ownership of `ulist->prealloc` into the tree and clears the spare pointer. If callers assume more than one reserved insertion, they can still hit `-ENOMEM`.

The container is intentionally narrow: it does not update auxiliary data for duplicates, does not sort iteration, and is unsafe without caller-provided locking.
