# File Research: sources/virtualization/qemu/block/qcow2-refcount.c

Implements qcow2 refcount storage, allocation, freeing, discard queuing, refcount checking/repair, metadata overlap protection, refcount-order conversion, refcount table shrinking, and metadata preallocation detection.

Key entry points:
- `qcow2_refcount_init()` / `qcow2_refcount_close()` load and free the in-memory refcount table and select packed refcount accessor functions for refcount orders 0 through 6.
- `qcow2_get_refcount()` reads one cluster refcount from the refcount table/refblock cache, treating missing table/block entries as zero.
- `qcow2_refcount_area()` creates self-covering refcount metadata at image creation or table growth time.
- `qcow2_alloc_clusters()`, `qcow2_alloc_clusters_at()`, `qcow2_alloc_bytes()`, `qcow2_free_clusters()`, and `qcow2_free_any_cluster()` are the main allocation/free APIs used by qcow2 metadata and data paths.
- `qcow2_update_snapshot_refcount()` walks L1/L2 tables to add/drop snapshot references and refresh `QCOW_OFLAG_COPIED`.
- `qcow2_check_refcounts()` constructs an independent in-memory refcount map, compares it with on-disk refcounts, optionally repairs leaks/corruption, rebuilds refcount structures when necessary, and checks copied flags.
- `qcow2_check_metadata_overlap()` and `qcow2_pre_write_overlap_check()` protect qcow2 metadata from invalid writes.
- `qcow2_change_refcount_order()` rewrites refblocks/reftable for a new refcount entry width.
- `qcow2_shrink_reftable()`, `qcow2_get_last_cluster()`, and `qcow2_detect_metadata_preallocation()` provide cleanup and image-layout helpers.

Core mechanics:
- Refcount entries are packed according to `s->refcount_order`: 1, 2, 4, 8, 16, 32, or 64-bit counts via `get_refcount_ro*()` and `set_refcount_ro*()`.
- `alloc_refcount_block()` allocates refblocks without normal recursive allocation, handles self-describing refblocks, grows the reftable through `qcow2_refcount_area()`, and returns `-EAGAIN` when callers must retry allocation after metadata consumed candidate clusters.
- `update_refcount()` rounds byte ranges to clusters, allocates needed refblocks, checks overflow/underflow, updates `s->free_cluster_index`, invalidates cached tables whose clusters become free, and queues optional passthrough discards.
- Discards are coalesced in `queue_discard()` and submitted by `qcow2_process_discards()` after refcount work succeeds unless discard caching is active.
- Check/repair code counts references from the header, active and snapshot L1/L2 trees, snapshot table, refcount table, refblocks, crypto header, and persistent bitmaps, then compares against on-disk refcounts.
- Rebuild mode allocates replacement refblocks and reftable from an in-memory refcount table, writes them, updates the qcow2 header, and leaves old structures as leaks for a later leak-fix pass.
- Metadata overlap checks cover main header, active/inactive L1 and L2 tables, refcount table, refblocks, snapshot table, and bitmap directory.

Important invariants:
- Refblock offsets must be cluster-aligned and nonzero when installed.
- Refcount arithmetic must not exceed `s->refcount_max` or underflow.
- Refcount metadata updates are ordered against L2-table updates through cache dependency calls.
- Refcount block allocation must avoid endless recursion by using no-ref allocation and self-covering metadata layouts.
- Snapshot refcount updates intentionally special-case the active L1 table; `qcow2_snapshot_goto()` depends on that behavior.
- `QCOW_OFLAG_COPIED` is valid only when the referenced cluster/refblock has refcount 1.

Filesystem/block relevance:
- This is the qcow2 allocator and consistency engine. It decides which host clusters are owned, shared, leaked, discardable, or safe to overwrite, so it is central to qcow2 copy-on-write correctness.

Notable risks:
- Failure during free paths can leak clusters; several comments explicitly choose leaking over risking corruption.
- Corrupt refcount metadata may force full refcount-structure rebuild rather than local repair.
- Overlap checking relies on all metadata regions being known and correctly represented in memory.
