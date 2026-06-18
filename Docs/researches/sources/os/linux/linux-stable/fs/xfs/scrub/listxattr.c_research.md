# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.c

This file provides a scrub-safe extended attribute walker. It calls caller-provided callbacks for every xattr entry in shortform, leaf, or node-format attr forks.

Shortform path:
- `xchk_xattr_walk_sf` iterates in-core shortform entries and calls `attr_fn` with flags, name, value pointer, and lengths.

Leaf path:
- `xchk_xattr_walk_leaf` reads attr leaf block zero and calls `xchk_xattr_walk_leaf_entries`.
- `xchk_xattr_walk_leaf_entries` decodes each leaf entry, distinguishes local vs remote values, passes local values directly, and passes `NULL` for remote values while preserving remote value length.

Node path:
- `xchk_xattr_find_leftmost_leaf` descends the dabtree from block zero to the leftmost leaf, checking node/leaf magic, headers, levels, and loops with an `xdab_bitmap`.
- `xchk_xattr_walk_node` walks leaf sibling links from left to right, invokes `leaf_fn` between leaves if provided, and detects leaf loops with the bitmap.

Public API:
- `xchk_xattr_walk` requires the inode ILOCK, returns immediately if no attrs exist, handles shortform directly, reads attr fork extents for non-local formats, and selects leaf vs node walking.

Important invariants:
- No cursor restarts are allowed; callers must hold ILOCK.
- Any structural problem, including dabtree loops, returns `-EFSCORRUPTED`.
- Remote attr values are not read here; callers receive metadata and length only.

Risks and edge cases:
- Node format traversal validates only enough structure to walk safely and detect loops.
- Callback errors stop traversal immediately.
- The optional `leaf_fn` gives callers a per-leaf boundary hook for stateful scrub logic.
