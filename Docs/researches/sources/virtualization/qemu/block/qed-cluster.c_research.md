# File Research: sources/virtualization/qemu/block/qed-cluster.c

Implements logical-to-file cluster lookup for QED. `qed_count_contiguous_clusters()` scans an L2 table from a given index and counts a contiguous run of entries, treating allocated clusters, unallocated markers, and zero-cluster markers as distinct run types.

`qed_find_cluster()` limits a request to a single L2-table boundary, looks up the L1 entry, validates the L2 table offset, reads or reuses the L2 table through the cache, then determines whether the requested range maps to allocated data, zero clusters, missing L2 entries, or missing L1 entries. It returns `QED_CLUSTER_FOUND`, `QED_CLUSTER_ZERO`, `QED_CLUSTER_L2`, `QED_CLUSTER_L1`, or a negative error.

The function also shortens `*len` to the contiguous run and stores the raw table offset/marker in `*img_offset`. It transfers an L2 cache reference into `request->l2_table`, replacing any previous reference, so callers can reuse the table for subsequent write allocation/update work.
