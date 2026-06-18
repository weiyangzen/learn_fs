# sources/storage-engines/tikv/src/server/gc_worker/rawkv_compaction_filter.rs

Purpose: implements the RawKV API v2 RocksDB compaction filter used by GC to remove obsolete RawKV MVCC versions and enqueue asynchronous deletion/TTL cleanup for latest deleted or expired records.

Important APIs/types/functions: `RawCompactionFilterFactory` implements `CompactionFilterFactory`; `RawCompactionFilter` implements `CompactionFilter`; `featured_filter` wraps error handling; `do_filter` owns key/value classification; `raw_gc_mvcc_deletions`, `schedule_gc_task`, and `raw_handle_delete` bridge to `GcTask::RawGcKeys`; `make_key` is test/export support.

Control flow: factory creation is gated by global `GC_CONTEXT`, nonzero safe point, non-stalled DB, and `check_need_gc`. Filtering ignores non-data keys, non-Raw API v2 key modes, and non-value records. For a new user-key prefix, it treats the first version as latest: versions at or above safe point are kept; latest versions below safe point are decoded and, when deleted or expired on the bottommost level, queued for async raw GC while still kept in this compaction pass. Later versions of the same key with commit timestamp below safe point are removed.

State and persistence: the filter holds only per-compaction in-memory state: current key prefix, version counters, pending `mvcc_deletions`, histograms, and an `encountered_errors` fail-open flag. Actual persistence changes happen through RocksDB compaction decisions and later GC worker deletes. `Drop` flushes pending async deletions and metrics before compaction result installation.

Dependencies and integration: depends on `api_version::ApiV2`, RocksDB raw compaction filter traits, `ttl_current_ts`, `RegionInfoProvider`, GC worker scheduling, and MVCC/GC metrics. It is specific to RawKV key mode under API v2 and uses raftstore region info for the later async delete task.

Risks: malformed API v2 keys or raw values make the filter fail open for the rest of the compaction, preserving data but reducing GC. Scheduler saturation drops async latest-delete cleanup and records failure metrics. Only bottommost compactions enqueue latest deleted/expired keys, so behavior depends on compaction level. Prefix tracking assumes keys are visited in RocksDB order.

Test signals: unit tests verify safe-point removal/retention boundaries, equality to safe point, deleted latest-version async GC, expired latest-version async GC, and generated raw key encoding.
