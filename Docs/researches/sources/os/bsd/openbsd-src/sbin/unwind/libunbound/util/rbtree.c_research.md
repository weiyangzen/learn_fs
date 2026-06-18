# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rbtree.c

Implements a generic intrusive red-black tree originally adapted from NSD. User objects embed `rbnode_type` as their first field, and comparison is supplied per tree.

Core behavior:
- `rbtree_create` allocates and initializes a tree; `rbtree_init` initializes caller-provided storage.
- Insert walks by `cmp`, rejects duplicate keys, links a red node, then rebalances with standard rotations and recoloring.
- Delete searches by key, swaps with the in-order successor when deleting a two-child node, then performs red-black delete fixup.
- Search uses `rbtree_find_less_equal`, which can return exact matches or the predecessor.
- `rbtree_first`, `rbtree_last`, `rbtree_next`, and `rbtree_previous` provide ordered traversal.
- `traverse_postorder` calls a callback after children, useful for freeing embedded-node objects without mutating the tree during traversal.

Invariants and implementation details:
- Uses a global black sentinel `rbtree_null_node`, exposed as `RBTREE_NULL`.
- The tree stores only key pointers and node links; object lifetime is owned by callers.
- The comparison callback is checked through `fptr_wlist` before use.
- Delete code changes parent/child pointers rather than swapping key/data because the rb node is embedded in caller-owned structures.

Integration points:
- Used by DNS-name/address trees and TCP connection limit storage in this group.
- Uses `log_assert` for structural assumptions during rotation and deletion.
