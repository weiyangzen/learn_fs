<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_aggregate.c -->
# sources/object-store/daos/src/vos/vos_aggregate.c

## Purpose
`vos_aggregate.c` implements VOS aggregation and discard. Aggregation removes obsolete versions, merges or deletes covered extent records, coalesces visible logical extents into new physical records, recalculates checksums, frees storage, updates the highest aggregated epoch, and yields cooperatively under credit limits. Discard removes data in an epoch range, optionally scoped to one object. The file is central to reclaim, snapshot deletion, VOS tree compaction, and metadata-on-SSD pressure handling.

## Important APIs, Types, And Functions
Public entry points are `vos_aggregate_enter()`, `vos_aggregate_exit()`, `vos_aggregate()`, and `vos_discard()`. `aggregate_enter()` and `aggregate_exit()` maintain container-level mutual exclusion flags for aggregation, discard, and object discard, and flush the WAL header when entering a mode.

`struct vos_agg_param` carries the container handle, current object ID, epoch filter, flags, error bits, UMEM pointer, yield callback, max SV epoch, skip flags, and `struct agg_merge_window`. `struct vos_agg_credits` limits scan/delete/merge work. `struct agg_merge_window` queues physical extent records (`agg_phy_ent`), removal records (`agg_rmv_ent`), visible logical entries (`agg_lgc_ent`), and I/O context (`agg_io_context`) for one evtree merge window.

Key callbacks are `vos_agg_filter()`, `vos_aggregate_pre_cb()`, and `vos_aggregate_post_cb()`. SV aggregation flows through `vos_agg_sv()` and `agg_del_sv()`. EV aggregation flows through `vos_agg_ev()`, `set_window_size()`, `join_merge_window()`, `flush_merge_window()`, `prepare_segments()`, `fill_segments()`, `insert_segments()`, and `cleanup_segments()`.

## Control Flow
`vos_aggregate()` asserts a valid epoch range, enters aggregation mode, chooses a filter epoch from HAE or `VOS_AGG_FL_FORCE_SCAN`, checks the container object-root aggregation timestamp, configures object iteration with `VOS_IT_PUNCHED`, `VOS_IT_RECX_COVERED`, `VOS_IT_FOR_PURGE`, and `VOS_IT_FOR_AGG`, initializes credits and merge-window lists, and calls `vos_iterate_obj()`. `-DER_BUSY` object conflicts trigger yield and retry. Checksum, no-space, and in-progress DTX states abort selected subtrees without blindly advancing HAE.

`vos_discard()` enters discard or object-discard mode, chooses iterator type and epoch expression from the supplied range, sets `VOS_IT_FOR_DISCARD`, and calls `vos_iterate()`. In discard mode value callbacks delete entries directly rather than building merge windows.

For EV aggregation, the sorted iterator emits logical records with visibility flags and original physical extents. `join_merge_window()` deletes fully covered intact records immediately, records remove entries, handles aborted/prepared DTX states, flushes the current window at thresholds or gaps, enqueues physical/logical entries, and flushes/closes on the iterator's last flag. `flush_merge_window()` decides whether work is worthwhile, prepares coalesced and truncated output segments, copies data, recalculates checksums, then transactionally deletes old evtree rectangles, inserts new rectangles, and publishes SCM/NVMe reservations.

## State And Persistence Behavior
Aggregation mutates persistent VOS trees and allocation state under UMEM transactions. `agg_del_sv()` wraps single-value deletion in `umem_tx_begin()`/`umem_tx_end()`. `insert_segments()` starts a transaction, publishes reserved SCM extents, updates physical-entry state for truncation, deletes old EV rectangles, processes removal records, inserts new evtree entries, clears the window, publishes NVMe reservations, and commits or aborts as a unit. On failure, `cleanup_segments()` cancels unpublished reservations.

Data movement uses BIO copy descriptors. `reserve_segment()` chooses SCM or NVMe via `vos_io_scm()` and reserves space through `vos_reserve_scm()` or `vos_reserve_blocks()`. `fill_one_segment()` builds source and destination BIO SGLs, widens reads when checksum chunks require extra bytes, verifies/recalculates checksums with `vos_csum_recalc_fn` through `vos_offload_exec()`, copies data, and updates aggregation metrics.

Container state includes `cd_hae`, `vc_in_aggregation`, `vc_in_discard`, `vc_obj_discard_count`, epoch ranges for active operations, no-space logging timestamps, and telemetry counters. `vos_aggregate()` updates HAE only when safe, and always calls `umem_heap_gc()` before returning.

## Dependencies And Integration Points
The implementation depends on VOS iterator APIs, object/key/ilog aggregation helpers (`oi_iter_*`, `vos_obj_iter_*`), evtree operations (`evt_insert()`, `evt_delete()`), BIO address/SGL/copy APIs, VEA/NVMe reservation publication, UMEM transactions and heap GC, checksum services, DTX state classification, DAOS fault injection, ABT yielding, and telemetry counters. It is directly exercised by VOS WAL/metadata-bucket tests that punch and aggregate objects to reclaim space.

## Risks And Edge Cases
Correctness risks cluster around partial physical extents, removal-record coalescing, checksum chunk alignment, transaction boundaries, and DTX conflict handling. Prepared entries return `-DER_TX_BUSY` and set skip flags to avoid orphaning parent tree state; aborted EV entries are deleted and cause iterator restart. No-space during aggregation is recorded without spamming logs, aborts current work, and avoids unsafe HAE advancement. Merge-window assertions and trace dumping are extensive because a sorted-iterator mismatch or stale visibility decision can corrupt evtree structure.

Large windows are bounded by byte threshold and `MW_MAX_MERGE_CNT` to limit WAL/local transaction size. `need_flush()` deliberately skips same-media coalescing when it would cost more than it saves, but forces flush for invisible data, removals, SCM-to-NVMe migration, holes, and forced merge. Discard and aggregation concurrency is restricted through container flags and WAL header flushes; object discard has separate counting but cannot overlap with full discard.

## Test Signals
Expected signals are indirect across VOS aggregation, discard, WAL, and metadata-bucket tests: obsolete SV/EV entries disappear, visible latest values remain fetchable, object/key trees collapse when empty, HAE advances only after successful safe aggregation, checksum errors return `-DER_CSUM`, no-space avoids corruption, in-progress DTX entries suppress parent aggregation, and storage usage decreases after punch plus `vos_aggregate()` followed by GC. Telemetry counters for scans, skips, deletes, merges, checksum errors, uncommitted entries, blocked retries, merge record counts, and merge bytes provide runtime observability.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_aggregate.c -->
