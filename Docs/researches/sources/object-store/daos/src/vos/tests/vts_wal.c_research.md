<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_wal.c -->
# sources/object-store/daos/src/vos/tests/vts_wal.c

## Purpose
`vts_wal.c` is the VOS-level WAL recovery test suite for metadata-on-SSD mode. It validates pool/container WAL replay, external checkpoint behavior, object update/fetch recovery across reopen, replay and checkpoint fault handling, key query/punch/update replay, metadata-bucket allocation/reclamation after restart, and phase-2 evictable bucket accounting.

## Important APIs, Types, And Functions
`struct wal_test_args` owns a cloned pool image and a 32 MiB copy buffer used by `save_pool()` and `restore_pool()` to simulate restart from a pre-operation VOS file while relying on WAL or checkpointed metadata blobs. The suite uses VOS pool/container APIs (`vos_pool_create()`, `vos_pool_open()`, `vos_pool_close()`, `vos_pool_destroy()`, `vos_cont_create()`, `vos_cont_open()`, `vos_cont_close()`, `vos_cont_destroy()`, `vos_pool_query()`), checkpoint APIs (`vos_pool_checkpoint_init()`, `vos_pool_checkpoint()`, `vos_pool_checkpoint_fini()`), object APIs (`vos_obj_update()`, `vos_obj_fetch()` through test helpers, `vos_obj_query_key()`, `vos_obj_punch()`), and aggregation (`vos_aggregate()`) for reclaim tests.

The memory-bucket portion exercises `umem_allot_mb_evictable()`, `umem_alloc_from_bucket()`, `umem_alloc()`, `umem_free()`, `umem_atomic_free()`, `umem_heap_gc()`, `umempobj_get_mbusage()`, `umempobj_get_heapusage()`, cache pin/unpin APIs, and page-cache statistics.

## Control Flow
`run_wal_tests()` first skips all tests unless `bio_nvme_configured(SMD_DEV_TYPE_META)` reports metadata-on-SSD support. It then runs pool/container WAL tests, basic single/extent-value I/O tests, object-type matrix I/O tests over `type_list`, an interrupt query/punch test for multi-uint64 objects, and memory-bucket tests when the backend is `DAOS_MD_BMEM_V2`.

The core recovery flow is repeated throughout: mutate VOS state, optionally checkpoint, close the pool, optionally set fault injection, reopen with `VOS_POF_EXTERNAL_CHKPT`, and then verify pool info, container handles, fetched object values, query-key results, or allocator accounting. `wal_pool_refill()` encapsulates close/reopen/refetch comparisons for object I/O tests and handles no-replay, fail-replay, checkpoint, and fail-checkpoint modes.

The later P2 and MB tests deliberately fill non-evictable and evictable memory buckets, free selected percentages, run GC, checkpoint during bulk allocation, reopen, and validate bucket reuse, MB usage accounting, page load/evict/miss stats, and object bucket IDs.

## State And Persistence Behavior
This file is heavily persistence-oriented. Pool cloning/restoration in `wal_tst_pool_cont()` clears local tmpfs-style state after WAL-producing operations, proving that container creation can be recovered from WAL replay. When checkpointing is enabled with `DAOS_WAL_NO_REPLAY`, tests prove checkpointed metadata alone is sufficient. `compare_pool_info()` checks container count, SCM/NVMe totals and free space, and VEA attributes before and after recovery.

Object tests cover small and large single values and extents, zero-copy modes, overwrite mode, many keys, many objects, and record-extent mode. The memory-bucket tests validate persistence of bucket IDs, usage counters, free-list reuse, spill-over evictable buckets, NEMB percentage configuration fixed at pool creation time, and post-restart page-cache behavior.

## Dependencies And Integration Points
The suite depends on VOS test helpers from `vts_io.h`, DAOS object type/key helpers, BIO/NVMe configuration, fault injection, DAOS environment variables (`DAOS_NEMB_EMPTY_RECYCLE_THRESHOLD`, `DAOS_MD_ON_SSD_NEMB_PCT`), VOS internals for handle-to-pool/container conversion, UMEM internals, and aggregation/GC helpers. It directly verifies integration among VOS, BIO WAL, metadata blobs, VEA space accounting, UMEM heap/cache, and the object tree layer.

## Risks And Edge Cases
The suite is storage-intensive: some setups allocate 1-2 GiB logical pool/blob sizes and run 10K-key loops. It is conditionally skipped outside MD-on-SSD mode, so non-MD-on-SSD CI does not exercise it. Fault-injection cases require FI support. The MB tests make detailed assumptions about bucket size, reserved non-evictable counts, backend type, page-cache stats, and GC timing; they include repeated GC calls and checkpoint intervals to reduce timing sensitivity.

Several tests rely on exact allocator preference ordering by utilization bands and exact cache stat increments after reopen/fetch. These are high-value regression signals but may need deliberate updates if allocator policy changes.

## Test Signals
Important pass signals include successful recovery with and without WAL replay, identical `vos_pool_info_t` before/after reopen, correct fetch data after restart for small/large SV/EV records, replay interruption returning `-DER_AGAIN` followed by successful retry, checkpoint failure returning `-DER_AGAIN`, query-key max dkey shifting after punch and back after update, MB usage equality across restart, free-block reuse after replay/checkpoint, and P2 bucket space returning to initial values after aggregation and GC.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_wal.c -->
