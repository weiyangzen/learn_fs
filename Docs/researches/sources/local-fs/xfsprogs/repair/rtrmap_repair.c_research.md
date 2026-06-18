# File Research: sources/local-fs/xfsprogs/repair/rtrmap_repair.c

Rebuilds realtime reverse-mapping btrees for rtgroups from the in-memory rmap observations collected during earlier repair phases.

Key structure:
- `struct xrep_rtrmap`: holds an in-memory rmap btree cursor, staged new inode fork state, bulkload geometry, repair context, rtgroup, and estimated free block budget.

Core flow:
- `populate_rtgroup_rmapbt` creates a transaction for the rtgroup rmap inode and rebuilds the tree if realtime rmapbt is enabled.
- `xrep_rtrmap_build_new_tree` stages a metadata btree fork, bulkloads all observed rtrmap records, commits the staged tree, updates counters, commits bulkload state, and rolls the transaction.
- `xrep_rtrmap_btree_load` computes geometry from `rmap_record_count`, reserves transaction blocks, allocates file blocks, opens an in-memory rmap cursor, and invokes libxfs bulkload.
- `xrep_rtrmap_get_records` feeds records from `rmap_get_mem_rec`.
- `rtgroup_update_counters` recalculates used blocks for zoned filesystems and updates `i_used_blocks`.

Important behavior:
- On rebuild failure, this file calls `do_error`, because the rtgroup rmapbt is required for enabled rtrmap filesystems.
- Rebuilt rt rmap btree blocks are owned through the bulkload file-block allocator.
- Zoned filesystems receive special used-block counter recomputation from the realtime block map.
