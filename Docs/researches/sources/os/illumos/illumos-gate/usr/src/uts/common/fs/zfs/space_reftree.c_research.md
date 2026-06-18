# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_reftree.c

This file implements space reference trees, an AVL-based sweep-line representation that converts ranges into offset deltas so unions and intersections can be computed by reference-count threshold.

Key behavior:
- A reference tree stores `space_ref_t` nodes sorted by offset, with pointer comparison as a tie-breaker so multiple deltas at the same offset can coexist.
- `space_reftree_create()` initializes the AVL tree.
- `space_reftree_destroy()` frees all `space_ref_t` nodes and destroys the AVL.
- `space_reftree_add_node()` allocates a delta node for a specific offset.
- `space_reftree_add_seg()` adds `+refcnt` at segment start and `-refcnt` at segment end.
- `space_reftree_add_map()` converts every range-tree segment into reference-tree deltas with the supplied refcount.
- `space_reftree_generate_map()` sweeps sorted deltas, tracks cumulative refcount, and emits ranges where `refcnt >= minref`.

Important uses:
- The file comment describes use in DTL reassessment: mirrors, RAID-Z, and interior vdevs can derive missing/outage regions by thresholding accumulated child DTL maps.
- Union is represented by `minref >= 1`; intersection by `minref >= N`.

Important invariants:
- Generated output range tree is vacated before filling.
- Final cumulative refcount must return to zero and no open range may remain at the end.
