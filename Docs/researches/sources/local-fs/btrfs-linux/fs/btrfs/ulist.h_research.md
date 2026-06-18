# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ulist.h

Declares the `ulist` unique-`u64` collection used by Btrfs traversal code.

Key declarations:
- `struct ulist_iterator` holds a current list position for `ulist_next()`.
- `struct ulist_node` stores `val`, `aux`, a linked-list node, and an rb-tree node.
- `struct ulist` stores `nnodes`, the list head, rb-tree root, and one optional preallocated node.
- APIs cover initialization, release, reuse, allocation/free, preallocation, add, add-with-existing-aux-return, delete, and iteration.
- `ulist_add_merge_ptr()` is a pointer-oriented wrapper for storing pointer payloads in `aux`.
- `ULIST_ITER_INIT()` initializes an iterator before traversal.

Core mechanics:
- The public data structure intentionally exposes both list and rb-tree nodes, matching kernel-style lightweight containers.
- `ulist_add_merge_ptr()` handles pointer payloads differently on 32-bit and 64-bit builds to preserve the `u64` backing storage API.

Important invariants:
- `ulist_node.val` is the unique key.
- `ulist_node.aux` is caller-defined metadata and may encode ids, logical addresses, or pointers.
- Callers must provide locking if a ulist is accessed concurrently.

Filesystem relevance:
- This header provides a reusable primitive for Btrfs graph walks that need "visit once, enumerate all" behavior without recursion.

Notable risks:
- Because the structure layout is public, direct field manipulation by callers could bypass rb-tree/list consistency if not disciplined.
- Pointer payload use through `aux` must account for architecture width and lifetime of the pointed-to objects.
