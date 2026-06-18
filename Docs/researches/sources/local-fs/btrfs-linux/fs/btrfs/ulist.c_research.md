# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ulist.c

Implements `ulist`, a small Btrfs helper collection for unique `u64` values with optional `u64` auxiliary data, rb-tree lookup, and list-based enumeration.

Key entry points:
- `ulist_init()` initializes an already allocated list object.
- `ulist_release()` frees all list nodes and the optional preallocated node but leaves the base `struct ulist` storage owned by the caller.
- `ulist_reinit()` releases current contents and resets the object for reuse.
- `ulist_alloc()` / `ulist_free()` allocate and free dynamic `struct ulist` instances.
- `ulist_prealloc()` reserves one zeroed node for a later insertion that may need to avoid allocation failure.
- `ulist_add()` inserts a value only if absent.
- `ulist_add_merge()` inserts a value or, if present, returns the existing auxiliary value through `old_aux`.
- `ulist_del()` removes a node only when both value and auxiliary value match.
- `ulist_next()` iterates list nodes and guarantees nodes added during iteration will be reached later in the same traversal.

Core mechanics:
- The rb-tree provides uniqueness and lookup by `val`; the linked list provides stable append-order traversal for graph/tree worklists.
- Insertions first search the rb-tree. Existing values return `0`; newly inserted values return `1`; allocation failures return `-ENOMEM`.
- `ulist->prealloc` is consumed by the next successful insertion path and cleared, otherwise insertion allocates with the caller-provided GFP mask.
- Deletion erases the rb-node, unlinks the list node, frees it, and decrements `nnodes`.
- Iteration stores the current list position in `struct ulist_iterator`; callers initialize it with `ULIST_ITER_INIT()`.

Important invariants:
- Locking is external. Writers need write-side locking when shared; iteration needs caller-provided read-side protection.
- `val` is the uniqueness key; `aux` is payload and is not considered by normal add/lookup.
- `ulist_del()` is stricter than lookup and requires both `val` and `aux` to match before deleting.
- `ulist_release()` does not explicitly reset `nnodes`; `ulist_reinit()` follows it with `ulist_init()` when full reuse state is needed.

Filesystem relevance:
- Btrfs uses ulist-style structures for non-recursive traversal of metadata/reference graphs where logical addresses or ids fit in `u64` and repeated visits must be suppressed.

Notable risks:
- The collection is not internally synchronized.
- Iterator validity depends on callers not deleting the current node unexpectedly during traversal.
- `ulist_add_merge_ptr()` in the header casts pointers through `u64`; the 32-bit branch preserves the public signature but pointer-sized assumptions remain important.
