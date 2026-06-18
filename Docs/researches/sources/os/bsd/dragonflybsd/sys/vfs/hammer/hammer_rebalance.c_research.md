# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_rebalance.c

Purpose: implements the B-tree rebalance ioctl. It repacks child node elements under internal nodes to reduce sparse nodes and delete excess children after pruning or other churn.

Top-level behavior: `hammer_ioc_rebalance()` validates caller ranges, clamps the requested saturation between half and full internal-node capacity, derives per-PFS or all-PFS localizations, and walks the B-tree forward with `HAMMER_CURSOR_REBLOCKING` so internal nodes are returned on the upward traversal. Leaf visits are collapsed to their last element because the parent/internal node is the object of interest.

Core algorithm: `rebalance_node()` upgrades the cursor, locks the parent, children, and grandchildren, copies locked on-disk nodes, counts all child elements, calculates a target average element count, and packs elements into earlier child nodes. If the average occupancy is below requested saturation, it reduces the desired child count and recomputes the average.

Metadata maintenance: while moving elements, the code updates mirror TIDs, parent internal-element boundaries, child parent pointers for moved internal elements, and live cursor tracking via `hammer_cursor_moved_element()`, `hammer_cursor_removed_node()`, and related helpers. Extra nodes beyond the new packed range are marked deleted in the copied node images and then synced with `hammer_btree_sync_copy()`.

Boundary helpers: `rebalance_closeout()` updates child counts, right-hand boundaries for internal children, and parent boundary base keys while preserving parent btype/internal metadata. `rebalance_parent_ptrs()` repoints a moved child node to its new parent and informs cursor tracking.

Operational behavior: rebalancing watches memory pressure (`vm_test_nominal()`), read-only transitions, user signals, metadata/UNDO pressure, and B-tree deadlocks. The operation is sync-lock protected only around actual node rebalancing, not the whole scan.
